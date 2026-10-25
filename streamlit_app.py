"""
Kivi-Vyaapaar (कीवी व्यापार) - Streamlit Dashboard
Voice-First Sovereign AI Coworker for Bharat MSMEs & Mandi Merchants
Powered by Sarvam AI: Saaras v4 (STT), Bulbul v3 (TTS), Sarvam 105B (Indus), Sarvam Vision
"""

import os
import io
import json
import base64
from datetime import datetime
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Kivi-Vyaapaar | कीवी व्यापार (Sarvam AI)",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import internal modules
from database import (
    init_db, seed_sample_data, get_connection,
    get_all_customers, get_recent_transactions,
    get_all_inventory, get_pending_approvals, get_business_kpis,
    get_recent_bills
)
from sarvam_client import SarvamClient
from indus_agent import IndusAgent

# Ensure database is initialized
init_db()
seed_sample_data()

# Initialize Sarvam Client & Indus Agent
@st.cache_resource
def get_agents():
    client = SarvamClient()
    agent = IndusAgent(client)
    return client, agent

sarvam_client, indus_agent = get_agents()

# Custom CSS for dark luxury theme
st.markdown("""
<style>
    .main {
        background-color: #07090e;
        color: #f1f5f9;
    }
    .stMetric {
        background-color: rgba(15, 20, 34, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px;
    }
    .hero-answer-box {
        background: linear-gradient(135deg, rgba(49, 46, 129, 0.4) 0%, rgba(88, 28, 135, 0.3) 50%, rgba(15, 23, 42, 0.8) 100%);
        border: 2px solid rgba(99, 102, 241, 0.5);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 0 35px rgba(99, 102, 241, 0.2);
        margin-bottom: 20px;
    }
    .invoice-card {
        background-color: #0d121f;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 20px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- Sidebar -----------------
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/sparkling.png", width=48)
    st.title("कीवी व्यापार")
    st.caption("Kivi-Vyaapaar | IIT BHU Campus Tour")
    st.markdown("---")

    st.subheader("🔑 Sarvam Sovereign Stack")
    api_status = "🟢 Live Connected" if sarvam_client.is_live else "🟠 Mock Engine"
    st.write(f"**API Status:** {api_status}")
    st.write("**STT:** Saaras v4 (`codemix`)")
    st.write("**TTS:** Bulbul v3 (`pooja`)")
    st.write("**Reasoning:** Sarvam 105B (Indus)")
    st.write("**Vision:** Sarvam Vision OCR")
    st.markdown("---")

    if st.button("🔄 Reset Demo Database"):
        conn = get_connection()
        for t in ["transactions", "customers", "inventory", "vendors", "approvals", "audit_logs", "bills"]:
            conn.execute(f"DELETE FROM {t}")
        conn.commit()
        conn.close()
        seed_sample_data()
        st.success("Database reset to demo state!")
        st.rerun()

    st.markdown("---")
    st.caption("Built with Sarvam AI APIs & Streamlit by Harman Singh")

# ----------------- Top Header & KPIs -----------------
st.title("🌾 Kivi-Vyaapaar (कीवी व्यापार)")
st.markdown("##### बोलिए या पर्ची स्कैन कीजिए — **बिना टाइप किए व्यापार चलाइए** | Voice & Document AI Coworker")

# Business KPIs
kpis = get_business_kpis()
col1, col2, col3, col4 = st.columns(4)
col1.metric("बाज़ार कुल उधार | Total Credit", f"₹{int(kpis['total_udhaar']):,}")
col2.metric("कम स्टॉक अलर्ट | Low Stock", f"{kpis['low_stock_alerts']} Items")
col3.metric("आज का वॉल्यूम | Volume", f"₹{int(kpis['total_transaction_volume']):,}")
col4.metric("इंडस अप्रूवल्स | Approvals", f"{kpis['pending_approvals_count']} Pending")

st.markdown("---")

# ----------------- Session State Initialization -----------------
if "latest_response" not in st.session_state:
    st.session_state.latest_response = {
        "hindi_answer": "नमस्ते! बोलकर ग्राहक का बकाया, स्टॉक, या बिल बनाने का आदेश दें।",
        "english_answer": "Hello! Speak or type to check balances, inventory, or generate bills hands-free.",
        "highlight_metric": "Ready",
        "voice_audio_base64": None,
        "bill": None
    }

# ----------------- Hero Upfront AI Answer Card -----------------
ans = st.session_state.latest_response
st.markdown(f"""
<div class="hero-answer-box">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="background-color: rgba(99, 102, 241, 0.3); border: 1px solid rgba(99, 102, 241, 0.5); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #a5b4fc;">
            ✨ प्रत्यक्ष उत्तर | Upfront AI Answer
        </span>
        <span style="background-color: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; color: #6ee7b7;">
            {ans.get('highlight_metric', 'Active')}
        </span>
    </div>
    <h2 style="color: #ffffff; margin-top: 4px; margin-bottom: 6px; font-size: 22px;">
        "{ans.get('hindi_answer')}"
    </h2>
    <p style="color: #cbd5e1; font-style: italic; margin-bottom: 0px; font-size: 14px;">
        🇬🇧 "{ans.get('english_answer')}"
    </p>
</div>
""", unsafe_allow_html=True)

# Play Voice Audio if available
if ans.get("voice_audio_base64"):
    audio_bytes = base64.b64decode(ans["voice_audio_base64"])
    st.audio(audio_bytes, format="audio/wav")

# If a Bill was generated, display invoice card upfront
if ans.get("bill"):
    bill = ans["bill"]
    st.markdown(f"""
    <div class="invoice-card">
        <h3 style="color: #6366f1; margin-bottom: 2px;">🧾 डिजिटल बिल पर्ची | Invoice #{bill['bill_no']}</h3>
        <p style="color: #94a3b8; font-size: 12px;">कीवी किराना स्टोर्स (वाराणसी) • ग्राहक: <b>{bill['customer_name']}</b> • {bill.get('created_at', 'Today')}</p>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 8px 0;">
        <table style="width: 100%; font-size: 13px;">
            <tr style="color: #94a3b8; border-bottom: 1px solid rgba(255,255,255,0.1);">
                <th style="text-align: left;">सामान | Item</th>
                <th style="text-align: center;">मात्रा | Qty</th>
                <th style="text-align: right;">दर | Rate</th>
                <th style="text-align: right;">रकम | Total</th>
            </tr>
            {''.join([f"<tr><td>{i['item']}</td><td style='text-align:center;'>{i['quantity']} {i.get('unit','')}</td><td style='text-align:right;'>₹{i.get('rate', i['amount']/i['quantity'])}</td><td style='text-align:right; color:#34d399;'>₹{i['amount']}</td></tr>" for i in bill['items']])}
        </table>
        <hr style="border-color: rgba(255,255,255,0.1); margin: 8px 0;">
        <div style="display: flex; justify-content: space-between; font-size: 16px; font-weight: bold; color: #34d399;">
            <span>कुल देय राशि | Grand Total:</span>
            <span>₹{int(bill['total']):,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------- Interactive Tabs -----------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎙️ बोलिए व पर्ची स्कैन (Input)",
    "👥 ग्राहक खाता (Khata Ledger)",
    "📜 लेन-देन पासबुक (Passbook)",
    "📦 गोदाम व स्टॉक (Inventory)",
    "🧾 सभी बिल (Invoices)",
    "🛡️ मंज़ूरी केंद्र (Approvals)"
])

# ----- Tab 1: Voice & Command Hub -----
with tab1:
    st.subheader("⚡ तुरंत टेस्ट करने के लिए स्टेज प्रीसेट क्लिक करें:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        if st.button("🧾 हरमन बंगू का बिल बनाएं (Invoice)"):
            with st.spinner("Sarvam 105B calculating bill line items..."):
                res = indus_agent.process_command("हरमन बंगू के लिए बिल बनाएं: 2 पैकेट बासमती राइस 650 रुपये, 3 किलो सरसों तेल 145 रुपये और 5 किलो चीनी 44 रुपये")
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": res.get("bill")
                }
                st.rerun()

    with col_p2:
        if st.button("🔍 बंगू का बकाया amount बताएं"):
            with st.spinner("Querying Khata balance..."):
                res = indus_agent.process_command("बंगू का बकाया amount बताएं।")
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": None
                }
                st.rerun()

    with col_p3:
        if st.button("👤 हरमन बंगू: ₹1,000 जमा करें"):
            with st.spinner("Recording deposit into Khata..."):
                res = indus_agent.process_command("हरमन बंगू के खाते में हज़ार रुपये जमा करें।")
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": None
                }
                st.rerun()

    col_p4, col_p5 = st.columns(2)
    with col_p4:
        if st.button("🛢️ Refined Oil ka stock kitna bacha hai?"):
            with st.spinner("Checking godown inventory..."):
                res = indus_agent.process_command("Refined Oil ka stock kitna bacha hai?")
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": None
                }
                st.rerun()

    with col_p5:
        if st.button("📜 Kirana store ke edible oil par GST kitna lagta hai?"):
            with st.spinner("Consulting Sarvam 105B Indic Knowledge..."):
                res = indus_agent.process_command("Kirana store ke edible oil par GST kitna lagta hai?")
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": None
                }
                st.rerun()

    st.markdown("---")

    # Command Input
    st.subheader("💬 बोलिए या टाइप कीजिए (Voice / Text Command)")
    user_input = st.text_input("आदेश दर्ज करें:", placeholder="e.g. हरमन बंगू के लिए बिल बनाएं: 2 पैकेट राइस 650, 3 किलो तेल 145")
    if st.button("प्रक्रिया करें | Execute Command", type="primary"):
        if user_input.strip():
            with st.spinner("Indus executing command..."):
                res = indus_agent.process_command(user_input.strip())
                voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                st.session_state.latest_response = {
                    "hindi_answer": res.get("hindi_answer", voice_text),
                    "english_answer": res.get("english_answer", ""),
                    "highlight_metric": res.get("highlight_metric", ""),
                    "voice_audio_base64": audio_b64,
                    "bill": res.get("bill")
                }
                st.rerun()

    st.markdown("---")

    # Audio & Receipt Uploaders
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.subheader("🎙️ ऑडियो फाइल अपलोड करें (Saaras v4)")
        audio_file = st.file_uploader("Upload Audio (WAV, MP3)", type=["wav", "mp3", "m4a", "ogg"])
        if audio_file:
            if st.button("ऑडियो ट्रांसक्राइब व प्रोसेस करें"):
                with st.spinner("Sarvam Saaras transcribing speech..."):
                    audio_bytes = audio_file.read()
                    stt = sarvam_client.transcribe_audio(audio_bytes, filename=audio_file.name)
                    transcript = stt.get("transcript", "")
                    st.info(f"Transcript: {transcript}")
                    res = indus_agent.process_command(transcript)
                    voice_text = res.get("hindi_answer") or res.get("voice_text", "")
                    audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                    st.session_state.latest_response = {
                        "hindi_answer": res.get("hindi_answer", voice_text),
                        "english_answer": res.get("english_answer", ""),
                        "highlight_metric": res.get("highlight_metric", ""),
                        "voice_audio_base64": audio_b64,
                        "bill": res.get("bill")
                    }
                    st.rerun()

    with col_u2:
        st.subheader("📸 मंडी पर्ची / बिल स्कैन (Sarvam Vision)")
        receipt_file = st.file_uploader("Upload Receipt / Invoice (Image, PDF, TXT)", type=["jpg", "jpeg", "png", "pdf", "txt"])
        if receipt_file:
            if st.button("पर्ची स्कैन व इनपुट करें"):
                with st.spinner("Sarvam Vision OCR parsing receipt..."):
                    file_bytes = receipt_file.read()
                    extracted = sarvam_client.parse_mandi_receipt_vision(file_bytes, filename=receipt_file.name)
                    vendor = extracted["vendor_or_customer"]
                    total = extracted["total_amount"]
                    items_sum = ", ".join([f"{i['quantity']} {i['unit']} {i['item']}" for i in extracted["items"]])
                    
                    # Create approval card
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO approvals (action_type, title, details, payload, status)
                    VALUES (?, ?, ?, ?, 'PENDING')
                    """, (
                        "INVOICE_AUDIT",
                        f"Mandi Receipt Ingested: {vendor} (₹{total:,.0f})",
                        f"Sarvam Vision parsed: {items_sum}. Total: ₹{total:,.0f}. Ready to sync inventory.",
                        json.dumps({"vendor": vendor, "items": extracted["items"], "total": total})
                    ))
                    conn.commit()
                    conn.close()

                    voice_text = f"सरवम विज़न ने {vendor} की पर्ची पढ़ ली है। कुल ₹{int(total):,} का माल इन्वेंटरी में जोड़ने के लिए इंडस अप्रूवल कार्ड तैयार है।"
                    eng_text = f"Sarvam Vision parsed invoice from {vendor} (Total ₹{int(total):,}). Created Indus Approval Card."
                    audio_b64 = sarvam_client.text_to_speech(voice_text, speaker="pooja")
                    
                    st.session_state.latest_response = {
                        "hindi_answer": voice_text,
                        "english_answer": eng_text,
                        "highlight_metric": f"{vendor}: ₹{int(total):,}",
                        "voice_audio_base64": audio_b64,
                        "bill": None
                    }
                    st.rerun()

# ----- Tab 2: Khata Ledger -----
with tab2:
    st.subheader("👥 ग्राहक खाता बही (Customer Khata Ledger)")
    customers = get_all_customers()
    if customers:
        formatted = []
        for c in customers:
            status = "₹0 चुकता (Settled)"
            if c["balance"] > 0:
                status = f"₹{int(c['balance']):,} उधार (Owed)"
            elif c["balance"] < 0:
                status = f"₹{int(abs(c['balance'])):,} जमा (Advance)"
            formatted.append({
                "Customer | ग्राहक": c["name"],
                "Phone | फ़ोन": c["phone"] or "—",
                "Credit Limit | सीमा": f"₹{int(c['credit_limit']):,}",
                "Net Balance | स्थिति": status
            })
        st.dataframe(formatted, use_container_width=True)
    else:
        st.write("No customers found.")

# ----- Tab 3: Passbook Transactions -----
with tab3:
    st.subheader("📜 लाइव लेन-देन पासबुक (Live Passbook Feed)")
    txs = get_recent_transactions(30)
    if txs:
        formatted_txs = []
        for t in txs:
            formatted_txs.append({
                "Time": t["timestamp"],
                "Customer | ग्राहक": t["customer_name"],
                "Type | प्रकार": t["type"],
                "Amount | राशि": f"₹{int(t['amount']):,}",
                "Note | विवरण": t["note"] or "—"
            })
        st.dataframe(formatted_txs, use_container_width=True)
    else:
        st.write("No transactions recorded yet.")

# ----- Tab 4: Inventory -----
with tab4:
    st.subheader("📦 गोदाम व स्टॉक नियंत्रण (Inventory & Stock)")
    inv = get_all_inventory()
    if inv:
        formatted_inv = []
        for i in inv:
            is_low = i["quantity"] <= i["reorder_level"]
            formatted_inv.append({
                "Item | सामान": i["item_name"],
                "Category | श्रेणी": i["category"],
                "Price | दर": f"₹{i['unit_price']} / {i['unit']}",
                "Available Stock | स्टॉक": f"{i['quantity']} {i['unit']}",
                "Status | स्थिति": "⚠️ कम स्टॉक | Low" if is_low else "✅ पर्याप्त | OK"
            })
        st.dataframe(formatted_inv, use_container_width=True)
    else:
        st.write("No inventory items found.")

# ----- Tab 5: All Generated Bills -----
with tab5:
    st.subheader("🧾 बनाए गए सभी डिजिटल बिल (Invoices Generated)")
    bills = get_recent_bills(20)
    if bills:
        for b in bills:
            with st.expander(f"🧾 Bill #{b['bill_no']} — {b['customer_name']} (₹{int(b['total']):,})"):
                st.write(f"**Date:** {b.get('created_at', 'Today')} | **Status:** {b['payment_status']}")
                st.table([{"Item": i["item"], "Qty": f"{i['quantity']} {i.get('unit','')}", "Rate": f"₹{i.get('rate', i['amount']/i['quantity'])}", "Amount": f"₹{i['amount']}"} for i in b["items"]])
                st.write(f"### Total: ₹{int(b['total']):,}")
    else:
        st.write("No bills generated yet. Speak to generate a bill!")

# ----- Tab 6: Indus Approvals -----
with tab6:
    st.subheader("🛡️ इंडस कोवर्क मंज़ूरी केंद्र (Human-in-the-Loop Governance)")
    st.caption("Sarvam Indus Core Principle: 'Nothing ships without your yes'")
    approvals = get_pending_approvals()
    if approvals:
        for a in approvals:
            with st.container():
                st.markdown(f"#### ⚡ {a['title']}")
                st.write(a["details"])
                col_a1, col_a2 = st.columns([1, 4])
                with col_a1:
                    if st.button(f"✅ मंज़ूर करें (Approve)", key=f"appr_{a['id']}"):
                        conn = get_connection()
                        conn.execute("UPDATE approvals SET status = 'APPROVED', resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (a["id"],))
                        conn.commit()
                        conn.close()
                        st.success(f"Approval #{a['id']} confirmed!")
                        st.rerun()
                with col_a2:
                    if st.button(f"✕ रद्द (Reject)", key=f"rej_{a['id']}"):
                        conn = get_connection()
                        conn.execute("UPDATE approvals SET status = 'REJECTED', resolved_at = CURRENT_TIMESTAMP WHERE id = ?", (a["id"],))
                        conn.commit()
                        conn.close()
                        st.warning(f"Approval #{a['id']} rejected.")
                        st.rerun()
                st.markdown("---")
    else:
        st.success("No pending approvals. All operations verified!")
