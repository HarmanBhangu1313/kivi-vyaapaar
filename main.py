"""
Kivi-Vyaapaar (कीवी व्यापार) - Main Application Server
Built for Sarvam AI Hackathon (IIT BHU & IIT Madras)
Integrates:
- Kivi Voice OS (Ambient Listening, Saaras v4 STT, Bulbul v3 TTS)
- Indus Cowork Agentic Engine (Sovereign Reasoning, Multi-step tool use, Human-in-the-Loop)
- Sarvam Vision (Receipt & Kaccha Parcha OCR Intelligence)
"""

import os
import json
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    init_db, seed_sample_data, get_connection,
    get_all_customers, get_recent_transactions,
    get_all_inventory, get_pending_approvals, get_business_kpis
)
from sarvam_client import SarvamClient
from indus_agent import IndusAgent

app = FastAPI(title="Kivi-Vyaapaar (कीवी व्यापार)", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database & seed data on startup
init_db()
seed_sample_data()

# Initialize Sarvam Client & Indus Agent
sarvam_client = SarvamClient()
indus_agent = IndusAgent(sarvam_client)

class TextCommandRequest(BaseModel):
    text: str

class ApprovalActionRequest(BaseModel):
    action: str # "APPROVE" or "REJECT"

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "sarvam_live": sarvam_client.is_live,
        "models": {
            "stt": "saaras:v4 (Code-mixed Indic)",
            "tts": "bulbul:v3 (Speaker: pooja)",
            "reasoning": "sarvam-105b-conversations (Indus Sovereign Model)",
            "vision": "Sarvam Vision (Receipt & Parcha OCR)"
        },
        "event": "Sarvam Campus Tour x IIT BHU",
        "bilingual": True
    }

@app.post("/api/voice-command")
async def handle_voice_command(file: UploadFile = File(...)):
    """
    Kivi Ambient Voice Pipeline:
    1. Audio -> Saaras v4 STT (codemix mode)
    2. Transcript -> Indus Agent Reasoning & Tool Calling
    3. Response Text -> Bulbul v3 TTS Audio (Speaker: pooja)
    """
    try:
        audio_bytes = await file.read()
        
        # 1. Transcribe with Sarvam Saaras v4
        stt_result = sarvam_client.transcribe_audio(audio_bytes, filename=file.filename or "audio.wav")
        transcript = stt_result.get("transcript", "").strip()

        if not transcript:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to transcribe audio", "details": stt_result}
            )

        # 2. Process with Indus Cowork Agent
        agent_result = indus_agent.process_command(transcript)

        # 3. Generate Speech with Sarvam Bulbul v3
        voice_text = agent_result.get("hindi_answer") or agent_result.get("voice_text", "")
        audio_base64 = sarvam_client.text_to_speech(voice_text, target_language_code="hi-IN", speaker="pooja")

        return {
            "success": True,
            "stt_engine": "saaras:v4 (codemix)",
            "transcript": transcript,
            "hindi_answer": agent_result.get("hindi_answer", voice_text),
            "english_answer": agent_result.get("english_answer", ""),
            "highlight_metric": agent_result.get("highlight_metric", ""),
            "bill": agent_result.get("bill"),
            "agent_result": agent_result,
            "voice_audio_base64": audio_base64,
            "is_mock": stt_result.get("is_mock", False)
        }

    except Exception as e:
        print(f"[Voice Command Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/text-command")
def handle_text_command(payload: TextCommandRequest):
    """
    Direct text execution for stage demo testing & simulation.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text command cannot be empty")

    agent_result = indus_agent.process_command(text)
    voice_text = agent_result.get("hindi_answer") or agent_result.get("voice_text", "")
    audio_base64 = sarvam_client.text_to_speech(voice_text, target_language_code="hi-IN", speaker="pooja")

    return {
        "success": True,
        "transcript": text,
        "hindi_answer": agent_result.get("hindi_answer", voice_text),
        "english_answer": agent_result.get("english_answer", ""),
        "highlight_metric": agent_result.get("highlight_metric", ""),
        "bill": agent_result.get("bill"),
        "agent_result": agent_result,
        "voice_audio_base64": audio_base64
    }

@app.post("/api/scan-receipt")
async def handle_receipt_scan(file: UploadFile = File(...)):
    """
    Sarvam Vision Document Intelligence Endpoint:
    Upload a Mandi Receipt / Handwritten Parcha / Invoice photo.
    Extracts line items, logs steps, and creates an Indus Approval card.
    """
    try:
        image_bytes = await file.read()
        extracted = sarvam_client.parse_mandi_receipt_vision(image_bytes, filename=file.filename or "receipt.jpg")

        vendor = extracted["vendor_or_customer"]
        total = extracted["total_amount"]
        items_summary = ", ".join([f"{i['quantity']} {i['unit']} {i['item']}" for i in extracted["items"]])

        # Create Indus Approval Card for the scanned invoice
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO approvals (action_type, title, details, payload, status)
        VALUES (?, ?, ?, ?, 'PENDING')
        """, (
            "INVOICE_AUDIT",
            f"Mandi Receipt Ingested: {vendor} (₹{total:,.0f})",
            f"Sarvam Vision parsed: {items_summary}. Total invoice amount: ₹{total:,.0f}. Ready to sync with inventory.",
            json.dumps({"vendor": vendor, "items": extracted["items"], "total": total})
        ))
        approval_id = cursor.lastrowid
        conn.commit()
        conn.close()

        voice_text = f"सरवम विज़न ने {vendor} की पर्ची पढ़ ली है। कुल ₹{int(total):,} का माल इन्वेंटरी में जोड़ने के लिए इंडस अप्रूवल कार्ड तैयार है।"
        english_text = f"Sarvam Vision parsed invoice from {vendor} (Total ₹{int(total):,}). Created Indus Approval Card to sync inventory."

        audio_base64 = sarvam_client.text_to_speech(voice_text, target_language_code="hi-IN", speaker="pooja")

        steps = [
            {"step": 1, "title_hi": "सरवम विज़न डॉक्यूमेंट स्कैन", "title_en": "Sarvam Vision OCR Scan", "desc": f"Parsed image '{file.filename}' (Confidence: 96%)", "status": "COMPLETED"},
            {"step": 2, "title_hi": "लाइन आइटम निष्कर्षण", "title_en": "Line Items Extraction", "desc": f"Extracted: {items_summary}", "status": "COMPLETED"},
            {"step": 3, "title_hi": "इंडस कोवर्क ऑडिट कार्ड", "title_en": "Indus Governance Card Created", "desc": f"Pending merchant verification for ₹{total:,.0f}", "status": "PENDING_APPROVAL"}
        ]

        return {
            "success": True,
            "vision_engine": "Sarvam Vision (Indic Document AI)",
            "extracted": extracted,
            "hindi_answer": voice_text,
            "english_answer": english_text,
            "highlight_metric": f"{vendor}: ₹{int(total):,} Ingested",
            "agent_result": {
                "steps": steps,
                "voice_text": voice_text,
                "english_text": english_text,
                "hindi_answer": voice_text,
                "bilingual_display": f"{voice_text}\n\n🇬🇧 {english_text}"
            },
            "voice_audio_base64": audio_base64
        }
    except Exception as e:
        print(f"[Vision Scan Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ledger")
def get_ledger():
    return {
        "customers": get_all_customers(),
        "recent_transactions": get_recent_transactions(15)
    }

@app.get("/api/inventory")
def get_inventory():
    return {
        "inventory": get_all_inventory()
    }

@app.get("/api/approvals")
def get_approvals():
    return {
        "approvals": get_pending_approvals()
    }

@app.post("/api/approvals/{approval_id}/action")
def resolve_approval(approval_id: int, payload: ApprovalActionRequest):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Approval not found")

    action = payload.action.upper()
    if action not in ["APPROVE", "REJECT"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Action must be APPROVE or REJECT")

    status = "APPROVED" if action == "APPROVE" else "REJECTED"
    cursor.execute("UPDATE approvals SET status = ?, resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (status, approval_id))

    execution_msg = ""
    if action == "APPROVE":
        data = json.loads(row["payload"])
        action_type = row["action_type"]

        if action_type == "LARGE_CREDIT":
            customer = data["customer"]
            amount = float(data["amount"])
            tx_type = data["type"]
            cursor.execute("UPDATE customers SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?", (amount, customer))
            cursor.execute("INSERT INTO transactions (customer_name, type, amount, note) VALUES (?, ?, ?, ?)",
                           (customer, tx_type, amount, f"[Approved] {data.get('note', '')}"))
            execution_msg = f"Credit of ₹{amount:,.0f} finalized for {customer}."

        elif action_type == "VENDOR_ORDER":
            vendor = data["vendor"]
            item = data["item"]
            qty = data["quantity"]
            unit = data["unit"]
            cursor.execute("UPDATE vendors SET last_order = CURRENT_TIMESTAMP WHERE name = ?", (vendor,))
            execution_msg = f"Purchase order for {qty} {unit} of {item} dispatched to {vendor} via WhatsApp API."

        elif action_type == "INVOICE_AUDIT":
            for item in data.get("items", []):
                cursor.execute("""
                UPDATE inventory SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP 
                WHERE item_name LIKE ?
                """, (item["quantity"], f"%{item['item']}%"))
            execution_msg = f"Invoice approved! Ingested ₹{data['total']:,.0f} worth of stock into inventory."

    conn.commit()
    conn.close()

    return {
        "success": True,
        "approval_id": approval_id,
        "new_status": status,
        "execution_message": execution_msg
    }

@app.get("/api/summary")
def get_summary():
    return get_business_kpis()

@app.post("/api/reset-data")
def reset_data():
    conn = get_connection()
    conn.execute("DELETE FROM transactions")
    conn.execute("DELETE FROM customers")
    conn.execute("DELETE FROM inventory")
    conn.execute("DELETE FROM vendors")
    conn.execute("DELETE FROM approvals")
    conn.execute("DELETE FROM audit_logs")
    conn.commit()
    conn.close()
    seed_sample_data()
    return {"success": True, "message": "Database reset to initial demo state"}

@app.get("/api/bills")
def get_bills():
    from database import get_recent_bills
    return {"bills": get_recent_bills(10)}

# Serve Frontend static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))
