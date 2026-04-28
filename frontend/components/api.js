// ===== API CONFIGURATION =====
const API_BASE = "https://aichatbot-2-vsq7.onrender.com/api";

function getToken() {
  return localStorage.getItem("healthbot_token");
}

function setToken(token) {
  localStorage.setItem("healthbot_token", token);
}

function removeToken() {
  localStorage.removeItem("healthbot_token");
  localStorage.removeItem("healthbot_user");
}

function getUser() {
  try {
    return JSON.parse(localStorage.getItem("healthbot_user") || "null");
  } catch { return null; }
}

function setUser(user) {
  localStorage.setItem("healthbot_user", JSON.stringify(user));
}

// ===== CORE FETCH WRAPPER =====
async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  // Remove Content-Type for FormData
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
    const data = await res.json().catch(() => ({}));

    if (res.status === 401) {
      removeToken();
      window.location.href = "/pages/index.html";
      return null;
    }
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    return { ok: false, status: 0, data: { error: "Network error. Is the server running?" } };
  }
}

// ===== AUTH =====
const Auth = {
  async register(payload) { return apiRequest("/auth/register", { method: "POST", body: JSON.stringify(payload) }); },
  async login(payload) { return apiRequest("/auth/login", { method: "POST", body: JSON.stringify(payload) }); }
};

// ===== USER =====
const User = {
  async get() { return apiRequest("/user/get"); },
  async edit(payload) { return apiRequest("/user/edit", { method: "PUT", body: JSON.stringify(payload) }); },
  async delete() { return apiRequest("/user/delete", { method: "DELETE" }); },
  async uploadPhoto(formData) { return apiRequest("/user/upload-photo", { method: "POST", body: formData }); }
};

// ===== CHAT =====
const Chat = {
  async send(message) { return apiRequest("/chat/send", { method: "POST", body: JSON.stringify({ message }) }); },
  async get(search = "", page = 1) { return apiRequest(`/chat/get?search=${encodeURIComponent(search)}&page=${page}`); },
  async delete(chatId) { return apiRequest(`/chat/delete/${chatId}`, { method: "DELETE" }); },
  async deleteAll() { return apiRequest("/chat/delete-all", { method: "DELETE" }); }
};

// ===== REPORT =====
const Report = {
  async upload(formData) { return apiRequest("/report/upload", { method: "POST", body: formData }); },
  async get() { return apiRequest("/report/get"); },
  async delete(reportId) { return apiRequest(`/report/delete/${reportId}`, { method: "DELETE" }); },
  async compare(r1, r2) { return apiRequest(`/report/compare?report1=${r1}&report2=${r2}`); }
};

// ===== UPLOAD =====
const Upload = {
  async create(formData) { return apiRequest("/upload/create", { method: "POST", body: formData }); },
  async get(type = "") { return apiRequest(`/upload/get${type ? "?type=" + type : ""}`); },
  async delete(uploadId) { return apiRequest(`/upload/delete/${uploadId}`, { method: "DELETE" }); }
};

// ===== EXPORT =====
async function downloadExport(type) {
  const token = getToken();
  const res = await fetch(`${API_BASE}/export/${type}`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || "Export failed");
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `chat_history.${type === "pdf" ? "pdf" : "docx"}`;
  a.click();
  URL.revokeObjectURL(url);
}

// ===== ADMIN =====
const Admin = {
  async stats() { return apiRequest("/admin/stats"); },
  async users() { return apiRequest("/admin/users"); },
  async deleteUser(id) { return apiRequest(`/admin/users/${id}`, { method: "DELETE" }); }
};

// ===== TOAST =====
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3500);
}

// ===== LOGOUT =====
function logout() {
  removeToken();
  window.location.href = "/pages/index.html";
}

// ===== AUTH GUARD =====
function requireAuth() {
  if (!getToken()) {
    window.location.href = "/pages/index.html";
    return false;
  }
  return true;
}
