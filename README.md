# 🌾 Kivi-Vyaapaar (कीवी व्यापार)
### Voice-First Sovereign AI Coworker for Bharat MSMEs & Mandi Merchants
*Built natively on Sarvam AI Sovereign Stack: Kivi + Indus + Saaras v4 + Bulbul v3*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://kivi-vyaapaar-kjjyqzfwjp2susnkm5tkik.streamlit.app/)
[![Sarvam AI](https://img.shields.io/badge/Powered%20By-Sarvam%20AI-orange.svg)](https://sarvam.ai)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

🔗 **Live Cloud App**: **[[[https://kivi-vyaapaar-kjjyqzfwjp2susnkm5tkik.streamlit.app/](https://kivi-vyaapaar-kjjyqzfwjp2susnkm5tkik.streamlit.app/](https://kivi-vyaapaar-2ukx7nytbbdkcxxuyv6vmr.streamlit.app/))](https://kivi-vyaapaar-2ukx7nytbbdkcxxuyv6vmr.streamlit.app/)**

---

## 💡 The Problem: Why Bharat Can't Use Silicon Valley AI
Over **63 million MSMEs, Kirana stores, and Mandi merchants** across India manage daily business, customer credit (*udhaar*), and supplier billing manually in paper diaries (*bahi-khata*).

Existing enterprise accounting tools (Tally, Zoho, Vyapar) fail Bharat's shopkeepers because:
1. **Language Barrier:** They require typing in English with complicated nested menus.
2. **Code-Mixed Dialects:** Indian merchants think and speak in code-mixed vernacular (Hindi + English, Hinglish, regional dialects like *"हरमन बंगू का 500 जमा करो"* or *"2 पैकेट चावल 650"*).
3. **Western LLMs Hallucinate:** US-centric AI models struggle with Indian commercial units (*peti*, *bori*, *tin*, *udhaar*, *jama*, *parcha*) and lack sovereign real-time action taking.

---

## 🚀 The Sovereign Solution: Kivi-Vyaapaar
**Kivi-Vyaapaar** is an ambient, voice-first autonomous coworker designed from the ground up on **Sarvam's sovereign Indic AI stack**:

```
[ 🎙️ Merchant Live Voice / Mobile Mic ]
                   │
                   ▼ (Audio Stream)
[ 🗣️ Sarvam Saaras v4 ] ────────────── Transcribes code-mixed Indic speech ('codemix' mode)
                   │
                   ▼ (Bilingual Transcript)
[ 🧠 Sarvam 105B / Indus Cowork ] ──── Autonomous planning, tool calling & database RAG
                   ├── Tool 1: Khata Ledger (Credits, Debits, Balances & Passbook)
                   ├── Tool 2: Voice-to-Bill Generator (Line items, Totals, Tax)
                   ├── Tool 3: Inventory Reconciler (Deducts stock automatically)
                   ├── Tool 4: Sarvam Vision (Handwritten Mandi receipts & parchis)
                   └── Tool 5: General Business Knowledge (GST rates, advice, FAQs)
                   │
                   ▼ (Voice Audio)
[ 📢 Sarvam Bulbul v3 ] ────────────── Natural Indic speech response (Speaker: Pooja)
```

---

## 🌟 Key Features

### 1. 🎯 Upfront Hero AI Answer Card
No digging through nested tabs. When a merchant asks:
- *"हरमन बंगू का बकाया कितना है?"*
- *"Refined Oil का स्टॉक कितना बचा है?"*
- *"किराना सामान पर GST दर क्या है?"*

The answer appears immediately **front-and-center** in bold bilingual cards (Hindi + English) with key numerical metrics highlighted, and automatically speaks aloud via **Sarvam Bulbul v3**.

### 2. 🧾 Voice-to-Bill Generation (आवाज़ से पक्का बिल)
Merchants can simply dictate customer purchases in natural language:
> *"हरमन बंगू के लिए बिल बनाएं: 2 पैकेट चावल 650, 3 किलो तेल 145 और 5 किलो आटा 220"*

**What Kivi-Vyaapaar does automatically:**
- Itemizes products, rates, quantities, and sub-totals.
- Calculates GST and grand total.
- Automatically deducts purchased items from inventory stock.
- Posts the transaction to the customer's Khata ledger.
- Generates a **printable digital invoice** with direct **WhatsApp Share** link.
- Confirms the transaction in spoken Hindi via Bulbul TTS.

### 3. 📖 Real-Time Khata Ledger & Live Passbook Feed
- **Customer Balances:** Clear view of Udhaar (credit owed) vs Advance (jama).
- **Audit Passbook:** Every voice transaction is timestamped with audit trails and notes.
- **Hindi Numeral Parsing:** Understands Devanagari numerals and spoken terms like *"हज़ार"* (1,000), *"सौ"* (100), *"लाख"* (1,00,000).

### 4. 📦 Godown & Inventory Tracker
- Live stock counting across essential grocery categories (Grains, Oils, Dairy, Spices).
- Automatic low-stock warnings with visual alert badges.
- Stock is automatically deducted when bills are generated.

### 5. 📸 Sarvam Vision Mandi Parcha Scanner
- Upload handwritten mandi receipts, paper bills, or mandi parchis.
- Extracts vendor names, line items, rates, and totals.
- Reconciles receipts directly into store accounts.

---

## 🛠️ The Sarvam Sovereign AI Stack

| Component | Model / Engine | Purpose in Kivi-Vyaapaar |
| :--- | :--- | :--- |
| **STT (Speech-to-Text)** | `saaras:v4` (`mode="codemix"`) | Real-time code-mixed Hindi/English speech recognition from browser microphone |
| **TTS (Text-to-Speech)** | `bulbul:v3` (Speaker: `pooja`) | Ultra-natural Indic voice response directly to the merchant |
| **LLM / Indus Agent** | `sarvam-105b-conversations` | Sovereign multi-step agentic planning, entity extraction, and live database RAG |
| **Vision OCR** | Sarvam Document & Vision API | Mandi handwritten receipt and invoice parsing |

---

## 🚀 Live Demo & Deployment

### 🌐 Live Cloud Link
👉 **[Open Kivi-Vyaapaar on Streamlit Cloud](https://kivi-vyaapaar-kjjyqzfwjp2susnkm5tkik.streamlit.app/)**

### 💻 Running Locally

#### 1. Clone the Repository
```bash
git clone https://github.com/HarmanBhangu1313/kivi-vyaapaar.git
cd kivi-vyaapaar
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Configure API Key
Create a `.env` file in the root directory:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
```

#### 4. Run the Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

#### 5. (Optional) Run the Full-Stack FastAPI Server
```bash
python3 -m uvicorn main:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** for the animated HTML5/FastAPI web interface.

---

## 🎤 3-Minute Hackathon Pitch Script (IIT BHU)

### Minute 0:00 – 0:45: The Hook & Bharat Reality
> *"Good afternoon, judges! Walking through the busy lanes of Vishwanath Gali and Godowlia here in Varanasi, every single Kirana shopkeeper and mandi trader runs their life on paper bahi-khatas. They don't use Tally or SAP—not because they can't afford software, but because software forces them to type in English.*  
> *Today, we present **Kivi-Vyaapaar**: the sovereign, voice-first autonomous AI coworker for Indian merchants, built natively on Sarvam AI."*

### Minute 0:45 – 2:00: Live Demo
1. **Live Voice Mic Input:**
   - Tap the microphone and say:  
     *"हरमन बंगू के लिए बिल बनाएं: 2 पैकेट चावल 650 और 3 किलो तेल 145"*
2. **Watch the Sovereign Stack at Work:**
   - **Sarvam Saaras v4** transcribes the code-mixed Hindi speech seamlessly.
   - **Sarvam 105B / Indus** extracts products, rates, calculates totals, deducts stock, and logs the customer khata.
   - A digital printable bill pops up with a 1-click **WhatsApp** sharing link.
   - **Sarvam Bulbul v3** speaks the confirmation back in natural Hindi.
3. **Upfront Answer Query:**
   - Ask: *"बंगू का बकाया amount बताएं"*
   - The upfront Hero Card highlights the exact balance instantly without needing to search through ledger tables.

### Minute 2:00 – 3:00: The Sovereign Advantage
> *"Western models fail on Indian units, code-mixed dialects, and regional trade practices. By unifying Kivi's ambient voice computing with Indus's sovereign reasoning, Kivi-Vyaapaar unlocks AI for the 63 million MSMEs that power Bharat's GDP.*  
> *Thank you!"*

---

## 📂 Project Architecture

```
kivi-vyaapaar/
├── streamlit_app.py     # Streamlit Cloud production dashboard with native mic input
├── main.py              # FastAPI REST server & full-stack web backend
├── sarvam_client.py     # Unified Sarvam API client (Saaras, Bulbul, 105B, Vision)
├── indus_agent.py       # Indus Cowork agentic engine with live DB context (RAG)
├── database.py          # SQLite persistence for Khata, Ledger, Inventory & Bills
├── requirements.txt     # Cloud dependencies (Streamlit, FastAPI, Uvicorn, Requests)
├── static/
│   ├── index.html       # High-tech Obsidian theme web app
│   ├── app.js           # MediaRecorder live mic stream & audio player
│   └── style.css        # Responsive styling & glowing waveforms
├── run.sh               # One-click startup shell script
└── README.md            # Comprehensive project documentation
```

---

## 📜 License
Distributed under the **MIT License**. See `LICENSE` for more information.

Built with ❤️ for **Sarvam AI Hackathon @ IIT BHU**.
