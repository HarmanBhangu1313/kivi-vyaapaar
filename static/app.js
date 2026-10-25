// Kivi-Vyaapaar Client Application v3.5
// Upfront Hero AI Answer Card + Voice-to-Bill Generation + Auto Speech Playback

let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let lastModifiedCustomer = null;
let currentVoiceAudioBase64 = null;
let currentBillData = null;

document.addEventListener("DOMContentLoaded", () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  // Initial Data Fetch
  refreshAllData();

  // Setup Interaction Handlers
  setupMic();
  setupReceiptScanner();
  setupPresets();
  setupResetButton();
  setupTabs();
  setupVoiceReplayButton();
  setupBillModal();
});

// ----------------- Bill Modal Setup -----------------

function setupBillModal() {
  const modal = document.getElementById("invoice-modal");
  const closeBtn = document.getElementById("close-bill-modal-btn");
  const viewBillHeroBtn = document.getElementById("hero-view-bill-btn");
  const whatsappBtn = document.getElementById("bill-whatsapp-btn");

  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  viewBillHeroBtn.addEventListener("click", () => {
    if (currentBillData) {
      showInvoiceModal(currentBillData);
    }
  });

  whatsappBtn.addEventListener("click", () => {
    if (!currentBillData) return;
    const msg = `*कीवी किराना स्टोर्स - बिल #${currentBillData.bill_no}*\nग्राहक: ${currentBillData.customer_name}\nकुल राशि: ₹${currentBillData.total}\nतारीख: ${currentBillData.created_at || 'आज'}\nधन्यवाद!`;
    const url = `https://wa.me/?text=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
  });
}

function showInvoiceModal(bill) {
  currentBillData = bill;
  const modal = document.getElementById("invoice-modal");
  document.getElementById("bill-customer-name").innerText = bill.customer_name;
  document.getElementById("bill-number").innerText = bill.bill_no;
  document.getElementById("bill-date").innerText = bill.created_at || new Date().toLocaleDateString("en-IN", { day: 'numeric', month: 'short', year: 'numeric' });
  document.getElementById("bill-subtotal").innerText = `₹${bill.subtotal.toLocaleString("en-IN")}`;
  document.getElementById("bill-grand-total").innerText = `₹${bill.total.toLocaleString("en-IN")}`;

  const tbody = document.getElementById("bill-items-tbody");
  tbody.innerHTML = bill.items.map((i) => {
    return `
      <tr class="hover:bg-white/[0.02]">
        <td class="py-2 px-3 font-medium text-white">${i.item}</td>
        <td class="py-2 px-2 text-center text-slate-300 font-mono">${i.quantity} ${i.unit || ''}</td>
        <td class="py-2 px-2 text-right text-slate-400 font-mono">₹${i.rate || (i.amount / i.quantity)}</td>
        <td class="py-2 px-3 text-right text-emerald-400 font-mono font-semibold">₹${i.amount.toLocaleString("en-IN")}</td>
      </tr>
    `;
  }).join("");

  modal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

// ----------------- Tab Navigation -----------------

function setupTabs() {
  const btnBalances = document.getElementById("tab-btn-balances");
  const btnPassbook = document.getElementById("tab-btn-passbook");
  const viewBalances = document.getElementById("view-balances");
  const viewPassbook = document.getElementById("view-passbook");

  btnBalances.addEventListener("click", () => {
    btnBalances.className = "tab-btn px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-sm";
    btnPassbook.className = "tab-btn px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 text-xs font-medium flex items-center gap-1.5 transition";
    viewBalances.classList.remove("hidden");
    viewPassbook.classList.add("hidden");
  });

  btnPassbook.addEventListener("click", () => {
    btnPassbook.className = "tab-btn px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold flex items-center gap-1.5 transition shadow-sm";
    btnBalances.className = "tab-btn px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 text-xs font-medium flex items-center gap-1.5 transition";
    viewPassbook.classList.remove("hidden");
    viewBalances.classList.add("hidden");
  });
}

function setupVoiceReplayButton() {
  const replayBtn = document.getElementById("hero-replay-voice-btn");
  replayBtn.addEventListener("click", () => {
    if (currentVoiceAudioBase64) {
      playBulbulAudio(currentVoiceAudioBase64);
    } else {
      alert("No voice audio available yet. Tap the microphone or click a preset to ask!");
    }
  });
}

// ----------------- Mic & Audio Recording (Saaras v4) -----------------

function setupMic() {
  const micBtn = document.getElementById("mic-btn");
  const pulseRing = document.getElementById("pulse-ring");
  const micLabel = document.getElementById("mic-label");
  const waveContainer = document.getElementById("audio-wave-container");

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    console.warn("MediaDevices API not supported. Use demo presets.");
    micLabel.innerText = "Mic Not Supported (Use Presets)";
    return;
  }

  micBtn.addEventListener("click", async () => {
    if (!isRecording) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (e) => {
          if (e.data.size > 0) {
            audioChunks.push(e.data);
          }
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
          stream.getTracks().forEach((track) => track.stop());
          await sendAudioToKivi(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;

        // Visual Recording State
        micBtn.classList.remove("from-indigo-500", "via-indigo-600", "to-violet-700");
        micBtn.classList.add("from-rose-600", "via-red-600", "to-pink-700");
        pulseRing.classList.remove("hidden");
        waveContainer.classList.remove("hidden");
        micLabel.innerHTML = "🔴 Listening... (बोलिए, रुकने पर क्लिक करें)";
      } catch (err) {
        console.error("Microphone access error:", err);
        alert("Microphone permission denied. You can still test any command using the stage preset buttons!");
      }
    } else {
      // Stop Recording
      mediaRecorder.stop();
      isRecording = false;

      // Reset Visual State
      micBtn.classList.remove("from-rose-600", "via-red-600", "to-pink-700");
      micBtn.classList.add("from-indigo-500", "via-indigo-600", "to-violet-700");
      pulseRing.classList.add("hidden");
      waveContainer.classList.add("hidden");
      micLabel.innerHTML = "⏳ Sarvam Saaras &amp; Indus Processing...";
    }
  });
}

async function sendAudioToKivi(blob) {
  const formData = new FormData();
  formData.append("file", blob, "merchant_voice.wav");

  renderProcessingState("Sarvam Saaras transcribing speech...");

  try {
    const res = await fetch("/api/voice-command", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    handleCommandResponse(data);
  } catch (err) {
    console.error("Audio transmission error:", err);
    alert("Error communicating with Kivi engine: " + err.message);
  } finally {
    document.getElementById("mic-label").innerHTML = "🎤 बोलिए | Tap to Speak";
  }
}

// ----------------- Sarvam Vision Receipt Scanner -----------------

function setupReceiptScanner() {
  const scanBtn = document.getElementById("scan-receipt-btn");
  const fileInput = document.getElementById("receipt-file-input");

  scanBtn.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", async (e) => {
    if (!e.target.files.length) return;
    const file = e.target.files[0];

    const formData = new FormData();
    formData.append("file", file);

    renderProcessingState(`Sarvam Vision OCR analyzing: "${file.name}"`);

    try {
      const res = await fetch("/api/scan-receipt", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      handleCommandResponse(data);
    } catch (err) {
      console.error("Receipt scan error:", err);
      alert("Error scanning receipt: " + err.message);
    } finally {
      fileInput.value = "";
    }
  });
}

// ----------------- Demo Presets -----------------

function setupPresets() {
  const buttons = document.querySelectorAll(".preset-pill");
  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const prompt = btn.getAttribute("data-prompt");
      renderProcessingState(`Indus evaluating: "${prompt}"`);

      try {
        const res = await fetch("/api/text-command", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: prompt })
        });
        const data = await res.json();
        handleCommandResponse(data);
      } catch (err) {
        console.error("Preset command error:", err);
      }
    });
  });
}

function renderProcessingState(message) {
  const transcriptEl = document.getElementById("transcript-display");
  transcriptEl.innerText = `⏳ ${message}`;

  const englishBox = document.getElementById("english-transcript-box");
  englishBox.classList.add("hidden");

  const heroHindi = document.getElementById("hero-hindi-answer");
  const heroEng = document.getElementById("hero-english-answer");
  heroHindi.innerText = `⏳ ${message}`;
  heroEng.innerText = "Indus Cowork is calculating and executing...";

  const stepsContainer = document.getElementById("steps-container");
  stepsContainer.innerHTML = `
    <div class="p-3 rounded-xl bg-slate-900 border border-white/[0.08] flex items-center gap-3 animate-pulse">
      <div class="w-2.5 h-2.5 rounded-full bg-indigo-400"></div>
      <span class="text-xs text-slate-300">Indus Cowork executing sovereign workflow...</span>
    </div>
  `;
}

// ----------------- Response Handler (UPFRONT DISPLAY) -----------------

function handleCommandResponse(data) {
  if (!data.success && data.error) {
    alert("Error: " + data.error);
    return;
  }

  const agentResult = data.agent_result || {};
  const transcript = data.transcript || (data.extracted ? `Mandi Receipt: ${data.extracted.vendor_or_customer}` : "");

  // Track customer modified to highlight
  if (agentResult.action_result && agentResult.action_result.customer) {
    lastModifiedCustomer = agentResult.action_result.customer;
  }

  // 1. UPDATE UPFRONT HERO AI ANSWER CARD
  const heroCard = document.getElementById("hero-ai-answer-card");
  const heroHindi = document.getElementById("hero-hindi-answer");
  const heroEng = document.getElementById("hero-english-answer");
  const heroMetric = document.getElementById("hero-metric-badge");
  const viewBillHeroBtn = document.getElementById("hero-view-bill-btn");

  const hindiAns = data.hindi_answer || agentResult.hindi_answer || agentResult.voice_text || "कार्य संपन्न हुआ।";
  const engAns = data.english_answer || agentResult.english_answer || "Task executed successfully.";
  const metric = data.highlight_metric || agentResult.highlight_metric || "";

  heroHindi.innerText = `"${hindiAns}"`;
  heroEng.innerText = `"${engAns}"`;

  if (metric) {
    heroMetric.classList.remove("hidden");
    heroMetric.innerText = metric;
  } else {
    heroMetric.classList.add("hidden");
  }

  // Pulse animation on the Hero Card so user's eyes are drawn to it
  heroCard.classList.add("ring-4", "ring-indigo-400/50");
  setTimeout(() => {
    heroCard.classList.remove("ring-4", "ring-indigo-400/50");
  }, 1200);

  // Check if a Bill was generated!
  const bill = data.bill || agentResult.bill;
  if (bill) {
    currentBillData = bill;
    viewBillHeroBtn.classList.remove("hidden");
    showInvoiceModal(bill); // Pop open the bill right away!
  } else {
    viewBillHeroBtn.classList.add("hidden");
  }

  // 2. Update Left Column Transcript
  const transcriptEl = document.getElementById("transcript-display");
  transcriptEl.innerHTML = `<span class="text-indigo-400 font-semibold font-['Space_Grotesk']">Transcript:</span> "${transcript}"`;

  // 3. Update English Translation Box
  if (engAns) {
    const englishBox = document.getElementById("english-transcript-box");
    const englishText = document.getElementById("english-transcript-text");
    englishBox.classList.remove("hidden");
    englishText.innerText = engAns;
  }

  // 4. Render Animated Bilingual Steps
  renderIndusSteps(agentResult.steps);

  // 5. Store & Play Live Bulbul TTS Audio Upfront
  currentVoiceAudioBase64 = data.voice_audio_base64;
  if (currentVoiceAudioBase64) {
    playBulbulAudio(currentVoiceAudioBase64);
  }

  // 6. Refresh Tables & KPIs
  refreshAllData();
}

function renderIndusSteps(steps) {
  const container = document.getElementById("steps-container");
  if (!steps || steps.length === 0) {
    container.innerHTML = `<div class="text-xs text-slate-400">No steps recorded.</div>`;
    return;
  }

  container.innerHTML = steps.map((s) => {
    let statusBadge = "";
    let borderClass = "border-white/[0.06]";

    if (s.status === "COMPLETED") {
      statusBadge = `<span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">Done</span>`;
    } else if (s.status === "PENDING_APPROVAL") {
      statusBadge = `<span class="text-[10px] px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30 font-medium">Needs Approval</span>`;
      borderClass = "border-violet-500/40 bg-violet-950/20";
    }

    const title = s.title_hi ? `${s.title_hi} <span class="text-slate-400 font-normal">(${s.title_en})</span>` : s.title;

    return `
      <div class="p-2.5 rounded-xl bg-slate-900/80 border ${borderClass} flex items-start gap-2.5 transition">
        <div class="w-5 h-5 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center text-[10px] font-bold text-indigo-400 shrink-0 mt-0.5">
          ${s.step}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between">
            <h4 class="text-xs font-semibold text-slate-200">${title}</h4>
            ${statusBadge}
          </div>
          <p class="text-[11px] text-slate-400 mt-0.5">${s.desc}</p>
        </div>
      </div>
    `;
  }).join("");
}

function playBulbulAudio(base64Audio) {
  const audioIndicator = document.getElementById("audio-indicator");
  const audioEl = document.getElementById("tts-audio");
  const voiceStatus = document.getElementById("hero-voice-status");

  audioIndicator.classList.remove("hidden");
  voiceStatus.innerText = "🔊 Speaking Now...";
  voiceStatus.classList.add("text-emerald-400");

  audioEl.src = `data:audio/wav;base64,${base64Audio}`;
  audioEl.play().catch((err) => {
    console.warn("Autoplay blocked by browser policy. Click 'Listen Voice' button to play.", err);
    voiceStatus.innerText = "Click 'Listen Voice' to hear";
    voiceStatus.classList.remove("text-emerald-400");
  });

  audioEl.onended = () => {
    audioIndicator.classList.add("hidden");
    voiceStatus.innerText = "Sarvam Bulbul (Voice: Pooja)";
    voiceStatus.classList.remove("text-emerald-400");
  };
}

// ----------------- Data Refresh Helpers -----------------

async function refreshAllData() {
  await Promise.all([
    fetchKPIs(),
    fetchLedger(),
    fetchInventory(),
    fetchApprovals()
  ]);
  if (window.lucide) {
    lucide.createIcons();
  }
}

async function fetchKPIs() {
  try {
    const res = await fetch("/api/summary");
    const data = await res.json();

    document.getElementById("kpi-udhaar").innerText = `₹${data.total_udhaar.toLocaleString("en-IN")}`;
    document.getElementById("kpi-low-stock").innerText = `${data.low_stock_alerts} आइटम्स`;
    document.getElementById("kpi-volume").innerText = `₹${data.total_transaction_volume.toLocaleString("en-IN")}`;
    document.getElementById("kpi-approvals").innerText = `${data.pending_approvals_count} पेंडिंग`;
  } catch (err) {
    console.error("KPI fetch error:", err);
  }
}

async function fetchLedger() {
  try {
    const res = await fetch("/api/ledger");
    const data = await res.json();

    const tbodyBalances = document.getElementById("customers-table-body");
    const tbodyPassbook = document.getElementById("transactions-table-body");
    document.getElementById("customer-count").innerText = `${data.customers.length} ग्राहक (Customers)`;

    // 1. Populate Balances Table
    if (!data.customers.length) {
      tbodyBalances.innerHTML = `<tr><td colspan="4" class="p-4 text-center text-slate-500">कोई ग्राहक खाता मौजूद नहीं है।</td></tr>`;
    } else {
      tbodyBalances.innerHTML = data.customers.map((c) => {
        let balanceTag = "";
        if (c.balance > 0) {
          balanceTag = `<span class="px-2 py-0.5 rounded text-[11px] bg-amber-500/15 text-amber-300 font-bold border border-amber-500/25">₹${c.balance.toLocaleString("en-IN")} उधार (Owed)</span>`;
        } else if (c.balance < 0) {
          balanceTag = `<span class="px-2 py-0.5 rounded text-[11px] bg-emerald-500/15 text-emerald-300 font-bold border border-emerald-500/25">₹${Math.abs(c.balance).toLocaleString("en-IN")} जमा (Advance)</span>`;
        } else {
          balanceTag = `<span class="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-400 font-medium border border-white/10">₹0 चुकता (Settled)</span>`;
        }

        const isHighlighted = lastModifiedCustomer && c.name.toLowerCase().includes(lastModifiedCustomer.toLowerCase());
        const rowClass = isHighlighted ? "bg-indigo-600/20 ring-1 ring-indigo-400" : "hover:bg-white/[0.03]";

        return `
          <tr class="${rowClass} transition duration-300">
            <td class="py-2.5 px-3 font-medium text-white flex items-center gap-2">
              <span class="w-2 h-2 rounded-full ${c.balance > 0 ? 'bg-amber-400' : (c.balance < 0 ? 'bg-emerald-400' : 'bg-slate-500')}"></span>
              <span class="font-semibold text-slate-100">${c.name}</span>
            </td>
            <td class="py-2.5 px-3 text-slate-400">${c.phone || "—"}</td>
            <td class="py-2.5 px-3 text-slate-400">₹${c.credit_limit.toLocaleString("en-IN")}</td>
            <td class="py-2.5 px-3 text-right">${balanceTag}</td>
          </tr>
        `;
      }).join("");
    }

    // 2. Populate Passbook Transactions Feed
    if (tbodyPassbook && data.recent_transactions) {
      if (!data.recent_transactions.length) {
        tbodyPassbook.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-500">कोई हालिया लेन-देन नहीं मिला।</td></tr>`;
      } else {
        tbodyPassbook.innerHTML = data.recent_transactions.map((tx) => {
          const isJama = tx.type === "JAMA";
          const typeBadge = isJama
            ? `<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/15 text-emerald-400 border border-emerald-500/25 font-bold">जमा (JAMA)</span>`
            : `<span class="px-2 py-0.5 rounded text-[10px] bg-amber-500/15 text-amber-400 border border-amber-500/25 font-bold">उधार (UDHAAR)</span>`;

          const amountClass = isJama ? "text-emerald-400 font-bold" : "text-amber-400 font-bold";
          const time = tx.timestamp ? tx.timestamp.split(" ")[1] || tx.timestamp : "Just now";

          return `
            <tr class="hover:bg-white/[0.03] transition">
              <td class="py-2.5 px-3 text-slate-400 font-mono text-[11px]">${time}</td>
              <td class="py-2.5 px-3 font-medium text-white">${tx.customer_name}</td>
              <td class="py-2.5 px-3">${typeBadge}</td>
              <td class="py-2.5 px-3 ${amountClass}">₹${tx.amount.toLocaleString("en-IN")}</td>
              <td class="py-2.5 px-3 text-slate-400 max-w-xs truncate">${tx.note || "—"}</td>
            </tr>
          `;
        }).join("");
      }
    }

  } catch (err) {
    console.error("Ledger fetch error:", err);
  }
}

async function fetchInventory() {
  try {
    const res = await fetch("/api/inventory");
    const data = await res.json();

    const tbody = document.getElementById("inventory-table-body");
    document.getElementById("inventory-count").innerText = `${data.inventory.length} आइटम्स (Stock)`;

    if (!data.inventory.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="p-4 text-center text-slate-500">कोई स्टॉक रिकॉर्ड नहीं मिला।</td></tr>`;
      return;
    }

    tbody.innerHTML = data.inventory.map((item) => {
      const isLow = item.quantity <= item.reorder_level;
      const statusBadge = isLow
        ? `<span class="px-2 py-0.5 rounded text-[10px] bg-rose-500/15 text-rose-400 border border-rose-500/25 font-semibold">कम स्टॉक | Low</span>`
        : `<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">संतोषजनक | OK</span>`;

      return `
        <tr class="hover:bg-white/[0.02] transition">
          <td class="py-2.5 px-3 font-medium text-white">${item.item_name}</td>
          <td class="py-2.5 px-3 text-slate-400">${item.category}</td>
          <td class="py-2.5 px-3 text-slate-400">₹${item.unit_price} / ${item.unit}</td>
          <td class="py-2.5 px-3 font-semibold ${isLow ? 'text-rose-400' : 'text-slate-200'}">
            ${item.quantity} ${item.unit}
          </td>
          <td class="py-2.5 px-3 text-right">${statusBadge}</td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Inventory fetch error:", err);
  }
}

async function fetchApprovals() {
  try {
    const res = await fetch("/api/approvals");
    const data = await res.json();

    const container = document.getElementById("approvals-container");
    if (!data.approvals || !data.approvals.length) {
      container.innerHTML = `<div class="text-xs text-slate-500 text-center py-4">No pending approvals. All systems synchronized.</div>`;
      return;
    }

    container.innerHTML = data.approvals.map((appr) => {
      return `
        <div class="p-3.5 rounded-xl bg-violet-950/20 border border-violet-500/30 space-y-2 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-[10px] uppercase font-bold text-violet-300 tracking-wider">${appr.action_type}</span>
            <span class="text-[10px] text-slate-400">${appr.created_at}</span>
          </div>
          <h4 class="text-xs font-semibold text-white">${appr.title}</h4>
          <p class="text-[11px] text-slate-300">${appr.details}</p>
          <div class="flex items-center gap-2 pt-1">
            <button onclick="resolveApproval(${appr.id}, 'APPROVE')" class="flex-1 py-1.5 px-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition flex items-center justify-center gap-1.5 shadow-sm">
              <i data-lucide="check" class="w-3.5 h-3.5"></i> मंज़ूर करें | Approve
            </button>
            <button onclick="resolveApproval(${appr.id}, 'REJECT')" class="py-1.5 px-3 rounded-lg bg-white/[0.06] hover:bg-white/[0.1] text-slate-300 text-xs transition">
              रद्द | Reject
            </button>
          </div>
        </div>
      `;
    }).join("");

    if (window.lucide) {
      lucide.createIcons();
    }
  } catch (err) {
    console.error("Approvals fetch error:", err);
  }
}

async function resolveApproval(id, action) {
  try {
    const res = await fetch(`/api/approvals/${id}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    });
    const data = await res.json();
    if (data.success) {
      alert(data.execution_message || `Action ${action} successful!`);
      await refreshAllData();
    }
  } catch (err) {
    alert("Error resolving approval: " + err.message);
  }
}

function setupResetButton() {
  const btn = document.getElementById("reset-btn");
  btn.addEventListener("click", async () => {
    if (confirm("Reset demo data to initial state?")) {
      await fetch("/api/reset-data", { method: "POST" });
      await refreshAllData();
      document.getElementById("transcript-display").innerText = "Demo reset. Ready for voice interaction.";
      document.getElementById("english-transcript-box").classList.add("hidden");
      document.getElementById("hero-view-bill-btn").classList.add("hidden");
      document.getElementById("hero-hindi-answer").innerText = '"नमस्ते! माइक दबाकर किसी भी ग्राहक का बकाया, स्टॉक, या हिसाब पूछें।"';
      document.getElementById("hero-english-answer").innerText = '"Hello! Tap the microphone to check balances, inventory, or ask any business question hands-free."';
      document.getElementById("steps-container").innerHTML = `<div class="text-xs text-slate-400 text-center py-4">Indus agent idle. Ready for voice or receipt upload.</div>`;
    }
  });
}
