"""
Indus Agentic Cowork Engine for Kivi-Vyaapaar.
Integrates Sarvam 105B with live database context (RAG) to:
1. Generate complete Digital Invoices / Bills with line items and pricings
2. Update customer ledger & deduct purchased stock from inventory
3. Answer direct customer balance queries upfront (e.g. "बंगू का बकाया amount बताएं")
4. Answer stock & inventory queries (e.g. "Oil ka stock kitna hai?")
5. Execute ledger transactions & updates (e.g. "हज़ार रुपये जमा करें")
6. Answer General Knowledge & Merchant queries (e.g. GST rates, business advice)
7. Generate upfront clear bilingual answers + natural Bulbul speech
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from database import get_connection, get_all_customers, get_all_inventory, save_bill
from sarvam_client import SarvamClient

class IndusAgent:
    def __init__(self, sarvam_client: SarvamClient):
        self.client = sarvam_client

    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Main entry point for processing merchant voice/text commands.
        Handles bill generation, actions, balance queries, stock queries, and general knowledge.
        """
        steps = []
        tools_executed = []
        
        # Ingestion Step
        steps.append({
            "step": 1,
            "title_hi": "कीवी कोड-मिक्स इनपुट",
            "title_en": "Kivi Code-Mixed Ingestion",
            "desc": f"Transcribed speech: \"{text}\"",
            "status": "COMPLETED"
        })

        # Fetch current database context for RAG
        customers = get_all_customers()
        inventory = get_all_inventory()
        cust_context = ", ".join([f"{c['name']}: ₹{c['balance']}" for c in customers])
        inv_context = ", ".join([f"{i['item_name']}: {i['quantity']} {i['unit']}" for i in inventory])

        # Analyze intent with live context
        intent_data = self._classify_with_context(text, cust_context, inv_context)
        intent = intent_data.get("intent", "GENERAL_KNOWLEDGE")

        steps.append({
            "step": 2,
            "title_hi": "इंडस टास्क प्लानिंग",
            "title_en": "Indus Task Planning",
            "desc": f"Intent: {intent} → Target: {intent_data.get('target', 'Merchant Assistant')}",
            "status": "COMPLETED"
        })

        action_result = {}
        human_approval_created = False
        hindi_answer = ""
        english_answer = ""
        highlight_metric = ""
        bill_data = None

        # Branch by Intent
        if intent == "GENERATE_BILL":
            # Voice-to-Bill Generation (Calculate line items, deduct stock, update khata)
            result = self._execute_generate_bill_tool(intent_data, text)
            tools_executed.append({"tool": "digital_billing_engine", "output": result})
            action_result = result
            bill_data = result.get("bill")
            hindi_answer = result["voice_response"]
            english_answer = result["english_response"]
            highlight_metric = f"Bill #{bill_data['bill_no']}: ₹{int(bill_data['total']):,}"

        elif intent == "QUERY_BALANCE":
            # Direct Balance Query
            result = self._execute_balance_query(intent_data, text)
            tools_executed.append({"tool": "khata_lookup_tool", "output": result})
            hindi_answer = result["hindi_answer"]
            english_answer = result["english_answer"]
            highlight_metric = result.get("highlight_metric", "")

        elif intent == "QUERY_STOCK":
            # Stock Query
            result = self._execute_stock_query(intent_data, text)
            tools_executed.append({"tool": "inventory_lookup_tool", "output": result})
            hindi_answer = result["hindi_answer"]
            english_answer = result["english_answer"]
            highlight_metric = result.get("highlight_metric", "")

        elif intent == "RECORD_KHATA":
            # Record Ledger Transaction
            result = self._execute_khata_tool(intent_data, original_text=text)
            tools_executed.append({"tool": "khata_ledger_tool", "output": result})
            action_result = result
            human_approval_created = result.get("approval_needed", False)
            hindi_answer = result["voice_response"]
            english_answer = result["english_response"]
            highlight_metric = f"{result['customer']}: ₹{int(abs(result['new_balance'])):,} {'उधार' if result['new_balance'] > 0 else 'जमा'}"

        elif intent == "INVENTORY_UPDATE":
            result = self._execute_inventory_tool(intent_data)
            tools_executed.append({"tool": "inventory_stock_tool", "output": result})
            action_result = result
            hindi_answer = result["voice_response"]
            english_answer = result["english_response"]
            highlight_metric = f"{result['item']}: {int(result['total_quantity'])} {result['unit']}"

        elif intent == "VENDOR_ORDER":
            result = self._execute_vendor_order_tool(intent_data)
            tools_executed.append({"tool": "vendor_dispatch_tool", "output": result})
            action_result = result
            human_approval_created = True
            hindi_answer = result["voice_response"]
            english_answer = result["english_response"]
            highlight_metric = f"Order: {result['item']} (Est. ₹{int(result['estimated_cost']):,})"

        elif intent == "DAILY_SUMMARY":
            result = self._execute_summary_tool()
            tools_executed.append({"tool": "business_analytics_tool", "output": result})
            action_result = result
            hindi_answer = result["voice_response"]
            english_answer = result["english_response"]
            highlight_metric = f"बाज़ार उधार: ₹{int(result['total_udhaar']):,}"

        else: # GENERAL_KNOWLEDGE / Conversational
            result = self._execute_general_knowledge(text, cust_context, inv_context)
            tools_executed.append({"tool": "sarvam_knowledge_tool", "output": result})
            hindi_answer = result["hindi_answer"]
            english_answer = result["english_answer"]
            highlight_metric = result.get("highlight_metric", "Sarvam Indic Intelligence")

        # Step 3 & 4 logs
        steps.append({
            "step": 3,
            "title_hi": "टूल निष्पादन",
            "title_en": "Tool Calling & System Execution",
            "desc": f"Executed: {', '.join([t['tool'] for t in tools_executed])}",
            "status": "COMPLETED"
        })

        if human_approval_created:
            steps.append({
                "step": 4,
                "title_hi": "इंडस कोवर्क मंज़ूरी अनिवार्य",
                "title_en": "Indus Governance Check (Approval Card Created)",
                "desc": "Action flagged for merchant confirmation: 'Nothing ships without your yes.'",
                "status": "PENDING_APPROVAL"
            })
        else:
            steps.append({
                "step": 4,
                "title_hi": "बिल व खाता सिंक",
                "title_en": "Bill Generated & Ledger Synchronized",
                "desc": "Direct result generated, inventory deducted, and record saved in database.",
                "status": "COMPLETED"
            })

        # Save to DB Audit Log
        self._save_audit_log(
            transcript=text,
            intent=intent,
            plan_steps=json.dumps(steps),
            tools_executed=json.dumps(tools_executed),
            summary=f"{hindi_answer} | {english_answer}"
        )

        return {
            "transcript": text,
            "intent": intent,
            "steps": steps,
            "tools_executed": tools_executed,
            "action_result": action_result,
            "bill": bill_data,
            "human_approval_created": human_approval_created,
            "hindi_answer": hindi_answer,
            "english_answer": english_answer,
            "highlight_metric": highlight_metric,
            "voice_text": hindi_answer
        }

    def _classify_with_context(self, text: str, cust_context: str, inv_context: str) -> Dict[str, Any]:
        """
        Classifies intent with live context using Sarvam 105B or heuristic fallback.
        """
        lower = text.lower()
        dev = text.strip()

        # Check for Bill Generation Intent (e.g. "बिल बनाएं", "bill banao", "generate bill", "invoice")
        is_bill_request = any(k in lower or k in dev for k in [
            "बिल बनाएं", "बिल बनाओ", "bill banao", "generate bill", "create bill", "invoice banao", "parcha banao", "बिल निकालो"
        ])
        if is_bill_request:
            return {"intent": "GENERATE_BILL", "target": "Voice-to-Bill Generation"}

        # Check for Balance Query (e.g. "बकाया बताएं", "kitna balance hai", "amount batao")
        is_query_balance = any(k in lower or k in dev for k in [
            "बकाया", "amount बताएं", "amount batao", "kitna baaki", "kitna balance", "balance batao", "hisaab kitna"
        ]) and not any(k in lower or k in dev for k in ["जमा करें", "jama", "udhaar likho", "लिखो", "add"])

        if is_query_balance:
            target = "हरमन बंगू"
            if "ramesh" in lower or "रमेश" in dev:
                target = "Ramesh Kirana"
            elif "gupta" in lower or "गुप्ता" in dev:
                target = "Gupta Ji Chai Wale"
            elif "varanasi" in lower or "मिठाई" in dev:
                target = "Varanasi Sweets Corner"
            elif "pandey" in lower or "पांडे" in dev:
                target = "Pandey Ji (Assi Ghat)"
            elif "bangu" in lower or "बंगू" in dev or "हरमन" in dev:
                target = "हरमन बंगू"
            return {"intent": "QUERY_BALANCE", "customer_name": target, "target": f"Check Balance: {target}"}

        # Check for Stock Query
        is_query_stock = any(k in lower or k in dev for k in [
            "stock kitna", "kitna bacha", "स्टॉक कितना", "कितना बचा", "kitni bachi", "quantity kitni"
        ]) and not any(k in lower or k in dev for k in ["add", "जोड़ो", "डालो"])

        if is_query_stock:
            item = "Refined Oil 15L Tin"
            if "rice" in lower or "chawal" in lower or "चावल" in dev:
                item = "Basmati Rice 10kg"
            elif "wheat" in lower or "aata" in lower or "गेहूं" in dev:
                item = "Wheat Flour (Aashirvaad 10kg)"
            elif "sugar" in lower or "cheeni" in lower or "चीनी" in dev:
                item = "Sugar (Madhur)"
            elif "tea" in lower or "chai" in lower or "चाय" in dev:
                item = "Tata Tea Gold 500g"
            return {"intent": "QUERY_STOCK", "item_name": item, "target": f"Check Stock: {item}"}

        # LLM Classification
        if self.client.is_live:
            system_prompt = (
                "You are Indus Cowork, an AI teammate for Indian Merchants. Analyze the user's spoken command.\n"
                f"CURRENT DATABASE CONTEXT:\n- Customers: {cust_context}\n- Inventory: {inv_context}\n\n"
                "Respond ONLY with a valid JSON object without markdown:\n"
                "{\n"
                "  \"intent\": \"GENERATE_BILL\" | \"RECORD_KHATA\" | \"INVENTORY_UPDATE\" | \"VENDOR_ORDER\" | \"DAILY_SUMMARY\" | \"QUERY_BALANCE\" | \"QUERY_STOCK\" | \"GENERAL_KNOWLEDGE\",\n"
                "  \"customer_name\": string or null,\n"
                "  \"amount\": number or null,\n"
                "  \"type\": \"JAMA\" | \"UDHAAR\" | null,\n"
                "  \"item_name\": string or null,\n"
                "  \"quantity\": number or null,\n"
                "  \"unit\": string or null,\n"
                "  \"vendor_name\": string or null\n"
                "}\n"
                "Convert Hindi numbers: हज़ार=1000, दो हज़ार=2000, पांच सौ=500."
            )
            raw = self.client.query_indus_llm(text, system_prompt)
            if raw:
                try:
                    clean = re.sub(r"```json|```", "", raw).strip()
                    parsed = json.loads(clean)
                    if parsed.get("intent"):
                        if parsed.get("amount") is not None:
                            parsed["amount"] = float(parsed["amount"])
                        return parsed
                except Exception:
                    pass

        # Fallback to Khata
        if any(w in lower or w in dev for w in ["jama", "जमा", "udhaar", "उधार", "khata", "खाते"]):
            return {
                "intent": "RECORD_KHATA",
                "customer_name": "हरमन बंगू" if any(k in dev or k in lower for k in ["हरमन", "बंगू", "bangu"]) else "Ramesh Kirana",
                "amount": 1000.0 if any(k in dev for k in ["हज़ार", "हजार"]) else 500.0,
                "type": "JAMA" if any(k in dev or k in lower for k in ["जमा", "jama"]) else "UDHAAR",
                "target": "Customer Ledger Transaction"
            }

        return {"intent": "GENERAL_KNOWLEDGE", "target": "General Merchant Knowledge"}

    # ----------------- Voice-to-Bill Tool -----------------

    def _execute_generate_bill_tool(self, data: Dict[str, Any], query_text: str) -> Dict[str, Any]:
        """
        Generates structured bill with line items, deducts inventory stock, and updates customer ledger.
        """
        customer = "हरमन बंगू"
        items = []
        total_amount = 0.0

        # Extract structured bill using Sarvam 105B
        if self.client.is_live:
            system_prompt = (
                "You are an Indian Kirana billing engine. Extract customer name and all purchased line items with pricings from this spoken command.\n"
                "If rate/price is not stated, estimate reasonable kirana rates in INR.\n"
                "Respond ONLY with a valid JSON object without markdown:\n"
                "{\n"
                "  \"customer_name\": string (e.g. 'हरमन बंगू'),\n"
                "  \"items\": [\n"
                "    {\"item\": string, \"quantity\": number, \"unit\": string, \"rate\": number, \"amount\": number}\n"
                "  ],\n"
                "  \"total_amount\": number\n"
                "}"
            )
            raw = self.client.query_indus_llm(query_text, system_prompt)
            if raw:
                try:
                    clean = re.sub(r"```json|```", "", raw).strip()
                    parsed = json.loads(clean)
                    if parsed.get("customer_name"):
                        customer = parsed["customer_name"].strip()
                    if parsed.get("items"):
                        items = parsed["items"]
                        total_amount = float(parsed.get("total_amount", sum(i["amount"] for i in items)))
                except Exception as e:
                    print(f"[Bill parse error] {e}")

        # Fallback items if parsing missed line items
        if not items:
            items = [
                {"item": "बासमती राइस (Basmati Rice 10kg)", "quantity": 2, "unit": "bags", "rate": 650.0, "amount": 1300.0},
                {"item": "सरसों का तेल (Mustard Oil 1L)", "quantity": 3, "unit": "packets", "rate": 145.0, "amount": 435.0},
                {"item": "चीनी (Sugar Madhur)", "quantity": 5, "unit": "kg", "rate": 44.0, "amount": 220.0}
            ]
            total_amount = 1955.0

        # Generate unique bill number
        bill_no = f"KV-{int(datetime.now().timestamp()) % 100000}"

        conn = get_connection()
        cursor = conn.cursor()

        # 1. Update/Create Customer
        row = cursor.execute("SELECT * FROM customers WHERE name LIKE ? OR name = ?", (f"%{customer}%", customer)).fetchone()
        if not row:
            cursor.execute("INSERT INTO customers (name, phone, balance, credit_limit) VALUES (?, '9800000000', ?, 15000.0)", (customer, total_amount))
            customer_id = cursor.lastrowid
            new_balance = total_amount
        else:
            customer_id = row["id"]
            customer = row["name"]
            new_balance = row["balance"] + total_amount
            cursor.execute("UPDATE customers SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_balance, customer_id))

        # 2. Deduct Purchased Items from Inventory
        for item in items:
            qty = float(item.get("quantity", 1))
            name_kw = item.get("item", "").split()[0]
            cursor.execute("""
            UPDATE inventory SET quantity = MAX(0, quantity - ?), updated_at = CURRENT_TIMESTAMP 
            WHERE item_name LIKE ?
            """, (qty, f"%{name_kw}%"))

        # 3. Insert Ledger Transaction
        cursor.execute("""
        INSERT INTO transactions (customer_id, customer_name, type, amount, note)
        VALUES (?, ?, 'UDHAAR', ?, ?)
        """, (customer_id, customer, total_amount, f"Bill #{bill_no}: {len(items)} items"))

        conn.commit()
        conn.close()

        # 4. Save to Bills table
        bill_record = save_bill(
            bill_no=bill_no,
            customer_name=customer,
            items=items,
            subtotal=total_amount,
            tax=0.0,
            total=total_amount,
            payment_status="UDHAAR"
        )

        voice_response = (
            f"जी मालिक, {customer} का ₹{int(total_amount):,} का डिजिटल बिल तैयार है। "
            f"कुल {len(items)} सामान जोड़े गए हैं और गोदाम से स्टॉक काट लिया गया है।"
        )
        english_response = (
            f"Digital Invoice #{bill_no} generated for {customer}. "
            f"Total: ₹{int(total_amount):,} ({len(items)} line items). Inventory and customer khata updated."
        )

        return {
            "bill": bill_record,
            "customer": customer,
            "items": items,
            "total_amount": total_amount,
            "new_balance": new_balance,
            "voice_response": voice_response,
            "english_response": english_response,
            "approval_needed": False
        }

    # ----------------- Query Handlers -----------------

    def _execute_balance_query(self, data: Dict[str, Any], query_text: str) -> Dict[str, Any]:
        target_name = data.get("customer_name", "हरमन बंगू")
        conn = get_connection()
        row = conn.execute("SELECT * FROM customers WHERE name LIKE ? OR name = ?", (f"%{target_name}%", target_name)).fetchone()
        conn.close()

        if row:
            name = row["name"]
            bal = row["balance"]
            if bal > 0:
                hindi_ans = f"{name} का वर्तमान कुल बकाया ₹{int(bal):,} उधार है।"
                eng_ans = f"{name}'s current balance is ₹{int(bal):,} in credit (Owed to shop)."
                metric = f"{name}: ₹{int(bal):,} उधार"
            elif bal < 0:
                hindi_ans = f"{name} का ₹{int(abs(bal)):,} अग्रिम (Advance) जमा है, कोई बकाया नहीं है।"
                eng_ans = f"{name} has an advance payment of ₹{int(abs(bal)):,}. No pending dues."
                metric = f"{name}: ₹{int(abs(bal)):,} जमा (Advance)"
            else:
                hindi_ans = f"{name} का पूरा खाता चुकता है, वर्तमान बकाया ₹0 है।"
                eng_ans = f"{name}'s account is fully settled. Current balance is ₹0."
                metric = f"{name}: ₹0 चुकता"
        else:
            hindi_ans = f"ग्राहक {target_name} का खाता नहीं मिला। क्या आप नया खाता बनाना चाहते हैं?"
            eng_ans = f"No customer account found for {target_name}. Would you like to create one?"
            metric = f"{target_name}: Not Found"

        return {
            "hindi_answer": hindi_ans,
            "english_answer": eng_ans,
            "highlight_metric": metric,
            "approval_needed": False
        }

    def _execute_stock_query(self, data: Dict[str, Any], query_text: str) -> Dict[str, Any]:
        item_target = data.get("item_name", "Refined Oil 15L Tin")
        conn = get_connection()
        row = conn.execute("SELECT * FROM inventory WHERE item_name LIKE ?", (f"%{item_target}%",)).fetchone()
        conn.close()

        if row:
            item = row["item_name"]
            qty = int(row["quantity"])
            unit = row["unit"]
            is_low = qty <= row["reorder_level"]
            status_txt = " (कम स्टॉक चेतावनी!)" if is_low else " (स्टॉक पर्याप्त है)"
            hindi_ans = f"{item} का वर्तमान उपलब्ध स्टॉक {qty} {unit} है{status_txt}।"
            eng_ans = f"Current stock for {item} is {qty} {unit} ({'Low Stock Alert!' if is_low else 'Optimal Stock'})."
            metric = f"{item}: {qty} {unit}"
        else:
            hindi_ans = f"आइटम {item_target} गोदाम में नहीं मिला।"
            eng_ans = f"Item {item_target} not found in inventory."
            metric = f"{item_target}: Not Found"

        return {
            "hindi_answer": hindi_ans,
            "english_answer": eng_ans,
            "highlight_metric": metric,
            "approval_needed": False
        }

    def _execute_general_knowledge(self, query: str, cust_context: str, inv_context: str) -> Dict[str, Any]:
        if self.client.is_live:
            system_prompt = (
                "You are Kivi-Vyaapaar AI, an expert assistant for Indian merchants in Varanasi.\n"
                f"SHOP CONTEXT:\n- Customers: {cust_context}\n- Inventory: {inv_context}\n\n"
                "Answer the user's question directly, accurately, and politely in 1-2 lines in conversational Hindi.\n"
                "Also provide a 1-line English translation.\n"
                "Respond ONLY with valid JSON:\n"
                "{\n"
                "  \"hindi_answer\": \"string in Hindi\",\n"
                "  \"english_answer\": \"string in English\",\n"
                "  \"highlight_metric\": \"concise 3-4 word highlight\"\n"
                "}"
            )
            raw = self.client.query_indus_llm(query, system_prompt)
            if raw:
                try:
                    clean = re.sub(r"```json|```", "", raw).strip()
                    parsed = json.loads(clean)
                    return {
                        "hindi_answer": parsed.get("hindi_answer", ""),
                        "english_answer": parsed.get("english_answer", ""),
                        "highlight_metric": parsed.get("highlight_metric", "Sarvam Indic Knowledge"),
                        "approval_needed": False
                    }
                except Exception:
                    pass

        lower = query.lower()
        if "gst" in lower:
            hindi = "किराना सामान जैसे खाद्यान्न और दालों पर आमतौर पर 0% या 5% GST लगता है, जबकि ब्रांडेड एडिबल ऑयल पर 5% GST लागू है।"
            eng = "Unbranded food grains attract 0% GST, while packaged edible oils generally attract 5% GST."
            metric = "GST: 0% - 5% on Staples"
        elif "sarvam" in lower:
            hindi = "सरवम एआई (Sarvam AI) भारत का पहला संप्रभु एआई प्लेटफॉर्म है, जिसे डॉ. विवेक राघवन और डॉ. प्रत्यूष कुमार ने शुरू किया है।"
            eng = "Sarvam AI is India's sovereign AI company co-founded by Dr. Vivek Raghavan and Dr. Pratyush Kumar."
            metric = "Sarvam Sovereign AI"
        else:
            hindi = f"नमस्ते! मैं कीवी व्यापार का इंडस कोवर्क असिस्टेंट हूँ। आप बिल बनाने, खाता बैलेंस, या स्टॉक की जानकारी पूछ सकते हैं।"
            eng = "Hello! I am your Indus AI Coworker. Ask me to generate bills, check balances, or inventory stock."
            metric = "Kivi AI Assistant"

        return {
            "hindi_answer": hindi,
            "english_answer": eng,
            "highlight_metric": metric,
            "approval_needed": False
        }

    # ----------------- Tool Implementations -----------------

    def _execute_khata_tool(self, data: Dict[str, Any], original_text: str = "") -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()

        customer = data.get("customer_name") or "हरमन बंगू"
        customer = customer.strip()
        amount = float(data.get("amount", 1000.0))
        tx_type = data.get("type", "JAMA")
        notes = original_text or data.get("notes", "Voice recorded transaction")

        row = cursor.execute("SELECT * FROM customers WHERE name = ? OR name LIKE ?", (customer, f"%{customer}%")).fetchone()
        
        if not row:
            initial_balance = amount if tx_type == "UDHAAR" else -amount
            cursor.execute(
                "INSERT INTO customers (name, phone, balance, credit_limit) VALUES (?, '9800000000', ?, 15000.0)",
                (customer, initial_balance)
            )
            customer_id = cursor.lastrowid
            current_balance = 0.0
            new_balance = initial_balance
            credit_limit = 15000.0
        else:
            customer_id = row["id"]
            customer = row["name"]
            current_balance = row["balance"]
            credit_limit = row["credit_limit"]
            delta = amount if tx_type == "UDHAAR" else -amount
            new_balance = current_balance + delta

        approval_needed = False
        approval_id = None
        if tx_type == "UDHAAR" and (amount >= 5000 or new_balance > credit_limit):
            approval_needed = True
            cursor.execute("""
            INSERT INTO approvals (action_type, title, details, payload, status)
            VALUES (?, ?, ?, ?, 'PENDING')
            """, (
                "LARGE_CREDIT",
                f"Credit Approval: {customer} (₹{amount:,.0f})",
                f"Requested credit of ₹{amount:,.0f}. Current balance: ₹{current_balance:,.0f}. New balance: ₹{new_balance:,.0f}.",
                json.dumps({"customer": customer, "customer_id": customer_id, "amount": amount, "type": tx_type, "note": notes})
            ))
            approval_id = cursor.lastrowid
            voice_response = f"{customer} के लिए ₹{int(amount)} का उधार का प्रस्ताव तैयार है। इंडस ने मंज़ूरी कार्ड बना दिया है।"
            english_response = f"Large credit request of ₹{int(amount):,} for {customer} flagged. Indus created an approval card."
        else:
            cursor.execute("UPDATE customers SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_balance, customer_id))
            cursor.execute("""
            INSERT INTO transactions (customer_id, customer_name, type, amount, note)
            VALUES (?, ?, ?, ?, ?)
            """, (customer_id, customer, tx_type, amount, notes))

            if tx_type == "JAMA":
                bal_hi = f"अब कुल बकाया ₹{int(new_balance):,} है।" if new_balance > 0 else f"खाता चुकता हो गया (अग्रिम ₹{int(abs(new_balance)):,})।"
                bal_en = f"Remaining balance is ₹{int(new_balance):,}." if new_balance > 0 else f"Account settled (Advance ₹{int(abs(new_balance)):,})."
                voice_response = f"जी मालिक, {customer} के खाते में ₹{int(amount):,} जमा कर लिए गए हैं। {bal_hi}"
                english_response = f"Done! Credited ₹{int(amount):,} for {customer}. {bal_en}"
            else:
                voice_response = f"जी मालिक, {customer} के खाते में ₹{int(amount):,} का उधार दर्ज कर लिया गया है। नया बकाया ₹{int(new_balance):,} है।"
                english_response = f"Done! Recorded ₹{int(amount):,} credit for {customer}. Updated balance is ₹{int(new_balance):,}."

        conn.commit()
        conn.close()

        return {
            "customer_id": customer_id,
            "customer": customer,
            "amount": amount,
            "type": tx_type,
            "old_balance": current_balance,
            "new_balance": new_balance,
            "approval_needed": approval_needed,
            "approval_id": approval_id,
            "voice_response": voice_response,
            "english_response": english_response
        }

    def _execute_inventory_tool(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()

        item_name = data.get("item_name", "Basmati Rice 10kg")
        qty = float(data.get("quantity", 10.0))
        unit = data.get("unit", "bags")

        row = cursor.execute("SELECT * FROM inventory WHERE item_name LIKE ?", (f"%{item_name}%",)).fetchone()
        if row:
            new_qty = row["quantity"] + qty
            cursor.execute("UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_qty, row["id"]))
            item_display = row["item_name"]
            unit_display = row["unit"]
        else:
            new_qty = qty
            cursor.execute("INSERT INTO inventory (item_name, quantity, unit, unit_price) VALUES (?, ?, ?, 500.0)",
                           (item_name, qty, unit))
            item_display = item_name
            unit_display = unit

        conn.commit()
        conn.close()

        voice_response = f"स्टॉक अपडेट हो गया! {item_display} के {int(qty)} {unit_display} जोड़ दिए गए हैं। अब कुल स्टॉक {int(new_qty)} {unit_display} है।"
        english_response = f"Stock updated! Added {int(qty)} {unit_display} of {item_display}. Total now: {int(new_qty)} {unit_display}."

        return {
            "item": item_display,
            "added_quantity": qty,
            "total_quantity": new_qty,
            "unit": unit_display,
            "approval_needed": False,
            "voice_response": voice_response,
            "english_response": english_response
        }

    def _execute_vendor_order_tool(self, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()

        vendor = data.get("vendor_name", "Suresh Oil Wholesalers (Mandi)")
        item = data.get("item_name", "Refined Oil 15L Tin")
        qty = float(data.get("quantity", 10.0))
        unit = data.get("unit", "tin")
        est_cost = qty * 1850.0

        cursor.execute("""
        INSERT INTO approvals (action_type, title, details, payload, status)
        VALUES (?, ?, ?, ?, 'PENDING')
        """, (
            "VENDOR_ORDER",
            f"WhatsApp Order: {item} to {vendor}",
            f"Purchase order for {int(qty)} {unit} of {item} (Est. ₹{est_cost:,.0f}). Ready to dispatch to supplier.",
            json.dumps({"vendor": vendor, "item": item, "quantity": qty, "unit": unit, "est_cost": est_cost})
        ))
        approval_id = cursor.lastrowid
        conn.commit()
        conn.close()

        voice_response = f"{vendor} के लिए {int(qty)} {unit} {item} का व्हाट्सएप ऑर्डर तैयार है। लागत ₹{int(est_cost):,} है। आपके हां कहते ही भेज दिया जाएगा।"
        english_response = f"Drafted WhatsApp PO for {int(qty)} {unit} of {item} to {vendor} (Est. ₹{int(est_cost):,}). Awaiting your approval."

        return {
            "vendor": vendor,
            "item": item,
            "quantity": qty,
            "unit": unit,
            "estimated_cost": est_cost,
            "approval_needed": True,
            "approval_id": approval_id,
            "voice_response": voice_response,
            "english_response": english_response
        }

    def _execute_summary_tool(self) -> Dict[str, Any]:
        conn = get_connection()
        total_udhaar = conn.execute("SELECT COALESCE(SUM(balance), 0) FROM customers WHERE balance > 0").fetchone()[0]
        low_stock_rows = conn.execute("SELECT item_name, quantity, unit FROM inventory WHERE quantity <= reorder_level").fetchall()
        tx_stats = conn.execute("""
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(CASE WHEN type = 'UDHAAR' THEN amount ELSE 0 END), 0) as total_udhaar_today,
                COALESCE(SUM(CASE WHEN type = 'JAMA' THEN amount ELSE 0 END), 0) as total_jama_today
            FROM transactions
        """).fetchone()
        conn.close()

        low_stock_items = [f"{r['item_name']} ({int(r['quantity'])} {r['unit']})" for r in low_stock_rows]
        low_stock_msg_hi = f"सावधान: {len(low_stock_items)} सामान कम स्टॉक में हैं।" if low_stock_items else "सभी सामान का स्टॉक ठीक है।"
        low_stock_msg_en = f"Alert: {len(low_stock_items)} items are below reorder level." if low_stock_items else "All inventory stock is optimal."

        voice_response = (
            f"व्यापार सारांश: बाज़ार में कुल उधार ₹{int(total_udhaar):,} है। "
            f"आज ₹{int(tx_stats['total_jama_today']):,} जमा हुए और ₹{int(tx_stats['total_udhaar_today']):,} का उधार दिया गया। "
            f"{low_stock_msg_hi}"
        )
        english_response = (
            f"Business Summary: Total market credit owed is ₹{int(total_udhaar):,}. "
            f"Today's cash collected: ₹{int(tx_stats['total_jama_today']):,}, new credit issued: ₹{int(tx_stats['total_udhaar_today']):,}. "
            f"{low_stock_msg_en}"
        )

        return {
            "total_udhaar": total_udhaar,
            "today_jama": tx_stats["total_jama_today"],
            "today_udhaar": tx_stats["total_udhaar_today"],
            "low_stock_items": low_stock_items,
            "approval_needed": False,
            "voice_response": voice_response,
            "english_response": english_response
        }

    def _save_audit_log(self, transcript: str, intent: str, plan_steps: str, tools_executed: str, summary: str):
        try:
            conn = get_connection()
            conn.execute("""
            INSERT INTO audit_logs (voice_transcript, agent_intent, plan_steps, tools_executed, result_summary)
            VALUES (?, ?, ?, ?, ?)
            """, (transcript, intent, plan_steps, tools_executed, summary))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Audit Log Error] {e}")
