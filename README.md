# 🌟 Kivi-Vyaapaar (कीवी व्यापार)
### Voice-First Autonomous AI Coworker for Bharat MSMEs & Mandi Merchants
*Built for the Sarvam AI Hackathon / Campus Tour @ IIT BHU & IIT Madras*

---

## 💡 The Core Problem: Why Bharat Can't Use Silicon Valley AI
Over **63 million MSMEs, Kirana stores, and Mandi merchants** across India manage daily finances, customer credit (*udhaar*), and supplier orders manually in paper diaries (*bahi-khata*). 

Existing ERP and accounting tools (like Zoho or Tally) fail them because:
1. They require **typing in English** with complex nested menus.
2. Merchants think and speak in **code-mixed vernacular** (Hindi + English, Bhojpuri + Hindi, Tanglish).
3. Western LLMs hallucinate Indian units (*peti*, *bori*, *tin*, *udhaar*, *jama*) and lack real-time sovereign action-taking.

---

## 🚀 The Solution: Kivi + Indus by Sarvam AI

**Kivi-Vyaapaar** merges Sarvam's two flagship technologies into a unified autonomous business assistant:

```
[ Ambient Microphone / PC ]
          │
          ▼ (Audio Stream)
[ Kivi Voice-In: Sarvam Saaras v4 ] ── Transcribes code-mixed Indic speech ('codemix' mode)
          │
          ▼ (Transcript)
[ Indus Cowork: sarvam-105b ] ─────── Autonomous task planning & multi-step execution
          ├── Tool 1: Khata Ledger (Credits, Debits & Balances)
          ├── Tool 2: Inventory & Low-Stock Alerts
          ├── Tool 3: Vendor WhatsApp PO Dispatch
          └── Governance: Human-in-the-Loop Approval Cards ("Nothing ships without your yes")
          │
          ▼ (Speech Audio)
[ Kivi Voice-Out: Sarvam Bulbul v3 ] ── Expressive, natural Hindi/Indic voice response
```

1. **Kivi (Ambient Voice Layer)**:
   - Powered by **Sarvam Saaras (`saaras:v4`)** in `mode="codemix"`.
   - Transcribes spoken sentences like: *"Ramesh ji ne 20 packet basmati rice liya, 1200 cash diya aur balance udhaar likh lo"*.
   - Speaks back naturally using **Sarvam Bulbul (`bulbul:v3`)** with regional inflection and respectful Hindi phrasing.

2. **Indus (Sovereign Agentic Cowork Brain)**:
   - Powered by **`sarvam-105b`** via Sarvam's OpenAI-compatible V2 endpoint.
   - Operates as an **autonomous AI teammate**:
     - Classifies merchant intent and extracts entities (quantities, prices, customer names, units).
     - Calls local accounting and inventory tools.
     - Enforces **Indus Cowork Human-in-the-Loop Governance**: High-value credits or supplier purchase orders generate verifiable **Approval Cards** with full audit logs.

---

## ⚡ Quick Start

### 1. Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `requests`, `python-dotenv`, `python-multipart`

### 2. Configure Environment (Optional but Recommended)
Copy `.env.example` to `.env` and insert your Sarvam API Key:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
```
> **Note:** The application includes an offline/resilient fallback engine. Even if you don't enter an API key, all voice workflows, Indus agent steps, and UI tables work seamlessly during practice sessions!

### 3. Launch the Server
```bash
./run.sh
```
Or directly via Python:
```bash
python3 -m uvicorn main:app --reload --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 🎤 The 3-Minute Winning Pitch Script for IIT BHU

Here is your exact pitch structure to deliver to Sarvam engineers and judges:

### Minute 0:00 - 0:45: The Hook & Varanasi Context
> *"Good afternoon everyone. Walking through Godowlia or Vishwanath Gali here in Varanasi, every single Kirana store and saree trader has a bahi-khata diary. They don't use Tally or SAP—not because they can't afford software, but because software demands typing in English.*  
> *Today, we built **Kivi-Vyaapaar**: the world's first ambient, voice-first AI coworker for Indian merchants, built natively on Sarvam Kivi and Indus."*

### Minute 0:45 - 2:00: Live Demo (The "Aha!" Moment)
1. **Show Code-Switching with Kivi & Saaras:**
   - Click the mic (or preset) and speak:  
     *"Ramesh ji ne 20 packets basmati rice aur 5 kg mustard oil liya, 1200 cash diya aur balance udhaar likh lo."*
   - Point to the screen:  
     *"Notice how Sarvam Saaras handles the mix of Hindi and English words. There is zero latency friction."*
2. **Show Indus Cowork Agentic Execution:**
   - Point to the animated Indus steps on the left:  
     *"Indus didn't just summarize text. It planned 4 steps: identified the customer Ramesh Kirana, separated the cash from the credit, updated the ledger table in real time, and reconciled stock."*
   - Listen to the audio:  
     *"Sarvam Bulbul speaks back immediately in natural Hindi with the exact updated balance."*
3. **Showcase Human-in-the-Loop Governance:**
   - Trigger a supplier order:  
     *"Suresh Wholesalers ko WhatsApp order bhejo 10 tin Refined Oil ke liye."*
   - Highlight the **Approval Card**:  
     *"Following Sarvam Indus Cowork's core philosophy—'Nothing ships without your yes'—Indus drafted the PO, calculated the ₹18,500 estimate, and waits for merchant approval before sending the message."*

### Minute 2:00 - 3:00: Why Sarvam Won This
> *"Silicon Valley models like GPT-4 fail on Indian dialects, code-mixing, and vernacular business units. By uniting Kivi's ambient voice computing with Indus's sovereign agentic planning, we bring AI to the 60 million merchants who power Bharat's GDP.*  
> *Thank you, and we welcome your questions!"*

---

## 📂 Project Structure

```
kivi-vyaapaar/
├── main.py              # FastAPI server & REST API
├── sarvam_client.py     # Sarvam Saaras (STT), Bulbul (TTS), 105B (Indus) client
├── indus_agent.py       # Autonomous Agentic Cowork engine & tool calling
├── database.py          # SQLite store for Ledger, Inventory, Approvals & Audit logs
├── static/
│   ├── index.html       # Modern, responsive merchant dashboard
│   ├── app.js           # Voice recording, audio player & real-time updates
│   └── style.css        # Animations & waveform styles
├── run.sh               # One-click startup script
└── README.md            # Hackathon pitch & documentation
```
