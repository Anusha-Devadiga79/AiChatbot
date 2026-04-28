// Auth guard
if (!requireAuth()) throw new Error("Not authenticated");

let currentUser = null;
let attachedFile = null;

// ===== INIT =====
async function init() {
  const res = await User.get();
  if (!res || !res.ok) { logout(); return; }
  currentUser = res.data.user;
  document.getElementById("sidebarName").textContent = currentUser.username;
  document.getElementById("sidebarEmail").textContent = currentUser.email;
  if (currentUser.profile_photo) {
    document.getElementById("sidebarAvatar").innerHTML = `<img src="${currentUser.profile_photo}" style="width:100%;height:100%;object-fit:cover;border-radius:50%"/>`;
  }
  loadProfileForm();
}

// ===== SECTION NAVIGATION =====
function showSection(name) {
  document.querySelectorAll(".content-section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById(`section-${name}`).classList.add("active");
  document.querySelector(`[data-section="${name}"]`).classList.add("active");

  if (name === "history") loadChatHistory();
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

// ===== CHAT =====
function quickSymptom(text) {
  document.getElementById("chatInput").value = text;
  sendMessage();
}

function handleChatKey(e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

function handleFileAttach(e) {
  const file = e.target.files[0];
  if (!file) return;
  attachedFile = file;
  const el = document.getElementById("attachedFile");
  el.innerHTML = `📎 ${file.name} <span onclick="removeAttachment()" style="cursor:pointer;margin-left:8px">✕</span>`;
  el.classList.remove("hidden");
}

function removeAttachment() {
  attachedFile = null;
  document.getElementById("attachedFile").classList.add("hidden");
  document.getElementById("chatFileInput").value = "";
}

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const message = input.value.trim();
  if (!message && !attachedFile) return;

  const sendBtn = document.getElementById("sendBtn");
  sendBtn.disabled = true;

  // Clear welcome screen
  const welcome = document.querySelector(".chat-welcome");
  if (welcome) welcome.remove();

  // Add user bubble (show image preview if image)
  const isImage = attachedFile && attachedFile.type.startsWith("image/");
  if (isImage) {
    const reader = new FileReader();
    reader.onload = e => appendBubble("user", message, e.target.result);
    reader.readAsDataURL(attachedFile);
  } else {
    const msgText = message || `[File: ${attachedFile?.name}]`;
    appendBubble("user", msgText);
  }
  input.value = "";

  const typingId = showTyping();

  let res;
  if (attachedFile) {
    // Always use FormData for file uploads (images + PDFs)
    const fd = new FormData();
    if (message) fd.append("message", message);
    fd.append("files", attachedFile);

    const token = getToken();
    try {
      const response = await fetch(`${API_BASE}/chat/send`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: fd
      });
      const data = await response.json().catch(() => ({}));
      res = { ok: response.ok, data };
    } catch (err) {
      res = { ok: false, data: { error: "Network error" } };
    }
  } else {
    // Text message
    res = await Chat.send(message || `Analyzing uploaded file: ${attachedFile?.name}`);
  }

  removeTyping(typingId);

  if (res?.ok) {
    appendBubble("bot", res.data.response);
  } else {
    appendBubble("bot", res?.data?.error || "Something went wrong. Please try again.");
  }

  removeAttachment();
  sendBtn.disabled = false;
  scrollChat();
}

function appendBubble(role, text, imageDataUrl) {
  const container = document.getElementById("chatMessages");
  const isUser = role === "user";
  const time = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  const div = document.createElement("div");
  div.className = `chat-bubble ${isUser ? "user" : "bot"}`;

  let contentHtml = "";
  if (imageDataUrl) {
    contentHtml += `<img src="${imageDataUrl}" class="chat-image-preview" alt="uploaded image"/>`;
  }
  if (text) {
    contentHtml += `<div class="bubble-text">${isUser ? escapeHtml(text) : formatBotMessage(text)}</div>`;
  }

  div.innerHTML = `
    <div class="bubble-avatar ${isUser ? "user-av" : "bot-av"}">${isUser ? "👤" : "🏥"}</div>
    <div class="bubble-content">
      ${contentHtml}
      <div class="bubble-time">${time}</div>
    </div>`;
  container.appendChild(div);
  scrollChat();
}

function formatBotMessage(text) {
  // Convert markdown-like formatting to HTML
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function showTyping() {
  const container = document.getElementById("chatMessages");
  const div = document.createElement("div");
  div.className = "chat-bubble bot";
  div.id = "typing-" + Date.now();
  div.innerHTML = `<div class="bubble-avatar bot-av">🏥</div>
    <div class="bubble-content"><div class="typing-indicator">
      <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
    </div></div>`;
  container.appendChild(div);
  scrollChat();
  return div.id;
}

function removeTyping(id) {
  document.getElementById(id)?.remove();
}

function scrollChat() {
  const c = document.getElementById("chatMessages");
  c.scrollTop = c.scrollHeight;
}

// ===== CHAT HISTORY =====
async function loadChatHistory(search = "") {
  const list = document.getElementById("chatHistoryList");
  list.innerHTML = '<div class="loading-state">Loading...</div>';
  const res = await Chat.get(search);
  if (!res?.ok) { list.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>Failed to load history</p></div>'; return; }
  const chats = res.data.chats || [];
  if (!chats.length) { list.innerHTML = '<div class="empty-state"><div class="empty-icon">💬</div><p>No chat history yet</p></div>'; return; }
  
  // Group chats by date
  const groupedByDate = {};
  chats.forEach(c => {
    const date = new Date(c.timestamp);
    const dateKey = date.toLocaleDateString([], { year: 'numeric', month: 'long', day: 'numeric' });
    if (!groupedByDate[dateKey]) groupedByDate[dateKey] = [];
    groupedByDate[dateKey].push(c);
  });
  
  // Build HTML with collapsible date groups
  let html = '';
  Object.entries(groupedByDate).forEach(([dateKey, dateChatList], index) => {
    const groupId = `date-group-${index}`;
    html += `
      <div class="date-group">
        <div class="date-header" onclick="toggleDateGroup('${groupId}')">
          <span class="date-toggle">▶</span>
          <span class="date-label">📅 ${dateKey}</span>
          <span class="date-count">(${dateChatList.length})</span>
        </div>
        <div class="date-chats" id="${groupId}" style="display: none;">`;
    
    dateChatList.forEach(c => {
      html += `
        <div class="history-item" id="chat-${c.chat_id}">
          <div class="history-item-header">
            <div class="history-msg">💬 ${escapeHtml(c.message)}</div>
            <div class="history-time">${new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
          </div>
          <div class="history-response" id="resp-${c.chat_id}">${escapeHtml(c.response)}</div>
          <div class="history-actions">
            <button class="btn-sm expand" onclick="toggleExpand('resp-${c.chat_id}', this)">Show more</button>
            <button class="btn-sm delete" onclick="deleteChat(${c.chat_id})">🗑 Delete</button>
          </div>
        </div>`;
    });
    
    html += '</div></div>';
  });
  list.innerHTML = html;
}

function toggleDateGroup(groupId) {
  const group = document.getElementById(groupId);
  const header = group.previousElementSibling;
  const toggle = header.querySelector('.date-toggle');
  
  if (group.style.display === 'none') {
    group.style.display = 'block';
    toggle.textContent = '▼';
  } else {
    group.style.display = 'none';
    toggle.textContent = '▶';
  }
}

function toggleExpand(id, btn) {
  const el = document.getElementById(id);
  const isExpanded = el.classList.contains('expanded');
  el.classList.toggle('expanded', !isExpanded);
  btn.textContent = isExpanded ? "Show more" : "Show less";
}

let searchTimeout;
function searchChats() {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => loadChatHistory(document.getElementById("searchChats").value), 400);
}

async function deleteChat(id) {
  window.chatToDelete = id;
  document.getElementById('deleteMessage').textContent = 'Are you sure you want to delete this chat? This action cannot be undone.';
  document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
  document.getElementById('deleteModal').classList.add('hidden');
  window.chatToDelete = null;
}

async function confirmDelete() {
  const id = window.chatToDelete;
  if (!id) return;
  closeDeleteModal();
  const res = await Chat.delete(id);
  if (res?.ok) { document.getElementById(`chat-${id}`)?.remove(); showToast("Chat deleted", "success"); }
  else showToast(res?.data?.error || "Failed to delete", "error");
}

async function deleteAllChats() {
  document.getElementById('deleteConfirmInput').value = '';
  document.getElementById('deleteAllBtn').disabled = true;
  document.getElementById('deleteAllModal').classList.remove('hidden');
}

function closeDeleteAllModal() {
  document.getElementById('deleteAllModal').classList.add('hidden');
  document.getElementById('deleteConfirmInput').value = '';
  document.getElementById('deleteAllBtn').disabled = true;
}

function onDeleteConfirmInput() {
  document.getElementById('deleteAllBtn').disabled = document.getElementById('deleteConfirmInput').value !== 'DELETE';
}

async function confirmDeleteAll() {
  const res = await Chat.deleteAll();
  if (res?.ok) { loadChatHistory(); closeDeleteAllModal(); showToast("All chats deleted", "success"); }
  else showToast(res?.data?.error || "Failed", "error");
} 

// ===== REPORTS =====
let reportSlots = { previous: null, current: null }; // { id, name, analysis, text }
let summaryRawText = "";
let isSpeaking = false;

async function handleReportUpload(event, slot) {
  const file = event.target.files[0];
  if (!file) return;

  const statusEl = document.getElementById(slot === 'previous' ? 'prevUploadStatus' : 'currUploadStatus');
  const boxEl = document.getElementById(slot === 'previous' ? 'prevUploadBox' : 'currUploadBox');

  statusEl.innerHTML = `<span class="upload-status uploading">⏳ Uploading...</span>`;
  boxEl.classList.add('uploading');

  const fd = new FormData();
  fd.append("file", file);

  const res = await Report.upload(fd);

  boxEl.classList.remove('uploading');

  if (res?.ok) {
    reportSlots[slot] = {
      id: res.data.report_id,
      name: file.name,
      analysis: res.data.analysis || "",
      text: res.data.extracted_text || ""
    };
    statusEl.innerHTML = `<span class="upload-status success">✅ ${escapeHtml(file.name)}</span>`;
    boxEl.classList.add('uploaded');
    showToast(`${slot === 'previous' ? 'Previous' : 'Current'} report uploaded`, 'success');
  } else {
    statusEl.innerHTML = `<span class="upload-status error">❌ ${res?.data?.error || 'Upload failed'}</span>`;
    showToast('Upload failed', 'error');
  }

  // Show compare button if both slots filled
  const bothReady = reportSlots.previous && reportSlots.current;
  document.getElementById('compareBar').style.display = bothReady ? 'flex' : 'none';

  event.target.value = '';
}

async function runReportComparison() {
  if (!reportSlots.previous || !reportSlots.current) {
    showToast('Upload both reports first', 'error');
    return;
  }

  const btn = document.querySelector('.btn-compare');
  btn.disabled = true;
  btn.textContent = '⏳ Analyzing...';

  try {
    const res = await Report.compare(reportSlots.previous.id, reportSlots.current.id);

    if (res?.ok) {
      const { ai_summary, analysis1, analysis2 } = res.data;

      document.getElementById('prevReportText').innerHTML = formatReportText(analysis1 || reportSlots.previous.text);
      document.getElementById('currReportText').innerHTML = formatReportText(analysis2 || reportSlots.current.text);

      // Render AI summary with rich formatting
      const summaryHtml = formatAiSummary(ai_summary || '');
      document.getElementById('reportSummaryText').innerHTML = summaryHtml;

      // Store plain text for TTS / export
      summaryRawText = ai_summary || '';

      document.getElementById('reportCompareResult').classList.remove('hidden');
      document.getElementById('reportCompareResult').scrollIntoView({ behavior: 'smooth' });
    } else {
      showToast(res?.data?.error || 'Comparison failed', 'error');
    }
  } catch (err) {
    showToast('Error: ' + err.message, 'error');
  }

  btn.disabled = false;
  btn.textContent = '⚖️ Compare Reports & Generate Summary';
}

function formatAiSummary(text) {
  if (!text) return '<em>No summary available</em>';

  // Escape HTML first
  let html = escapeHtml(text);

  // Disclaimer line → styled box
  html = html.replace(
    /(⚠️[^\n]+)/g,
    '<div class="summary-disclaimer">$1</div>'
  );

  // Bold section headers like **Potential Health Risks:**
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

  // Risk lines: "Name: Risk level - explanation"
  html = html.replace(
    /^([\w\s\/]+):\s*(Low|Medium|High|Critical|Moderate)[\/\s]*(Low|Medium|High|Critical|Moderate)?\s*[-–]\s*(.+)$/gim,
    (_, name, r1, r2, desc) => {
      const level = (r2 || r1).toLowerCase();
      const badge = `<span class="risk-badge risk-${level}">${r1}${r2 ? '/' + r2 : ''}</span>`;
      return `<div class="summary-risk-item"><span class="risk-name">${name.trim()}</span>${badge}<span class="risk-desc">${desc}</span></div>`;
    }
  );

  // Bullet points
  html = html.replace(/^[•\-]\s+(.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul class="summary-list">$1</ul>');

  // Line breaks
  html = html.replace(/\n{2,}/g, '</p><p class="summary-para">');
  html = html.replace(/\n/g, '<br>');
  html = '<p class="summary-para">' + html + '</p>';

  return html;
}

function formatReportText(text) {
  if (!text) return '<em>No analysis available</em>';
  return escapeHtml(text).replace(/\n/g, '<br>');
}

async function translateReportSummary() {
  const lang = document.getElementById('reportTranslateLang').value;
  if (!lang) return;

  // Only translate the AI Health Summary box
  const summaryText = document.getElementById('reportSummaryText')?.innerText || '';
  if (!summaryText.trim()) { showToast('No summary to translate', 'error'); return; }

  showToast('Translating...', 'info');

  try {
    const token = getToken();
    const res = await fetch(`${API_BASE}/health/translate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: summaryText, target_language: lang })
    });

    if (res.ok) {
      const data = await res.json();
      const translated = data.translated_text || data.translated || '';
      document.getElementById('reportSummaryText').innerHTML = formatReportText(translated);
      summaryRawText = translated;
      showToast(`Translated to ${data.target_language_name || lang}`, 'success');
    } else {
      showToast('Translation failed', 'error');
    }
  } catch (err) {
    showToast('Translation error', 'error');
  }
}

function transcriptSummary() {
  if (!summaryRawText) { showToast('No summary to read', 'error'); return; }

  if (isSpeaking) {
    window.speechSynthesis.cancel();
    isSpeaking = false;
    document.querySelector('.btn-transcript').textContent = '🎙️ Read Aloud';
    return;
  }

  const utterance = new SpeechSynthesisUtterance(summaryRawText);
  utterance.rate = 0.9;
  utterance.onend = () => {
    isSpeaking = false;
    document.querySelector('.btn-transcript').textContent = '🎙️ Read Aloud';
  };
  window.speechSynthesis.speak(utterance);
  isSpeaking = true;
  document.querySelector('.btn-transcript').textContent = '⏹️ Stop';
}

async function exportReportSummary(format) {
  if (!reportSlots.current?.id) { showToast('No report to export', 'error'); return; }

  // Only export the AI Health Summary (translated if applicable)
  const summaryText = document.getElementById('reportSummaryText')?.innerText || '';
  if (!summaryText.trim()) { showToast('No summary to export', 'error'); return; }

  showToast(`Exporting ${format.toUpperCase()}...`, 'info');

  const lang      = document.getElementById('reportTranslateLang')?.value || '';
  const langNames = { es:'Spanish', fr:'French', de:'German', hi:'Hindi', ar:'Arabic', zh:'Chinese', pt:'Portuguese', ta:'Tamil', te:'Telugu' };

  try {
    const token = getToken();
    const ext = format === 'pdf' ? 'pdf' : 'docx';
    const res = await fetch(`${API_BASE}/export/report/${format}/${reportSlots.current.id}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        summary:  summaryText,
        language: langNames[lang] || 'English'
      })
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `health_summary_${new Date().toISOString().slice(0,10)}.${ext}`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Download started', 'success');
    } else {
      const err = await res.json().catch(() => ({}));
      showToast(err.error || 'Export failed', 'error');
    }
  } catch (err) {
    showToast('Export error: ' + err.message, 'error');
  }
}

function closeCompareResult() {
  document.getElementById('reportCompareResult').classList.add('hidden');
}

// ===== PROFILE =====
function loadProfileForm() {
  if (!currentUser) return;
  document.getElementById("profileUsername").value = currentUser.username || "";
  document.getElementById("profileEmail").value = currentUser.email || "";
  document.getElementById("profileAge").value = currentUser.age || "";
  document.getElementById("profileGender").value = currentUser.gender || "";
  if (currentUser.profile_photo) {
    document.getElementById("profilePhoto").innerHTML = `<img src="${currentUser.profile_photo}" style="width:100%;height:100%;object-fit:cover;border-radius:50%"/>`;
  }
}

async function updateProfile(e) {
  e.preventDefault();
  const msgEl = document.getElementById("profileMsg");
  msgEl.classList.add("hidden");
  const payload = {
    username: document.getElementById("profileUsername").value.trim(),
    age: parseInt(document.getElementById("profileAge").value) || null,
    gender: document.getElementById("profileGender").value
  };
  const res = await User.edit(payload);
  if (res?.ok) {
    currentUser = { ...currentUser, ...res.data.user };
    setUser(currentUser);
    document.getElementById("sidebarName").textContent = currentUser.username;
    msgEl.textContent = "Profile updated successfully!";
    msgEl.className = "success-msg";
    msgEl.classList.remove("hidden");
    setTimeout(() => msgEl.classList.add("hidden"), 3000);
  } else {
    msgEl.textContent = res?.data?.error || "Update failed";
    msgEl.className = "error-msg";
    msgEl.classList.remove("hidden");
  }
}

async function uploadProfilePhoto(e) {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("photo", file);
  const res = await User.uploadPhoto(fd);
  if (res?.ok) {
    const path = res.data.path;
    document.getElementById("profilePhoto").innerHTML = `<img src="${path}" style="width:100%;height:100%;object-fit:cover;border-radius:50%"/>`;
    document.getElementById("sidebarAvatar").innerHTML = `<img src="${path}" style="width:100%;height:100%;object-fit:cover;border-radius:50%"/>`;
    showToast("Photo updated", "success");
  } else showToast(res?.data?.error || "Upload failed", "error");
}

async function deleteAccount() {
  if (!confirm("Are you sure you want to delete your account? This cannot be undone.")) return;
  if (!confirm("This will permanently delete all your data. Continue?")) return;
  const res = await User.delete();
  if (res?.ok) { removeToken(); window.location.href = "/frontend/index.html"; }
  else showToast(res?.data?.error || "Failed to delete account", "error");
}

// ===== EXPORT =====
async function exportData(type) {
  showToast(`Preparing ${type.toUpperCase()} export...`, "info");
  try {
    await downloadExport(type);
    showToast("Download started!", "success");
  } catch (err) {
    showToast(err.message || "Export failed", "error");
  }
}

// ===== HELPERS =====
function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function formatDate(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

// ===== START =====
init();
