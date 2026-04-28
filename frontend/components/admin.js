if (!requireAuth()) throw new Error("Not authenticated");

function showAdminSection(name) {
  document.querySelectorAll(".admin-section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById(`admin-section-${name}`).classList.add("active");
  document.querySelector(`[data-section="${name}"]`).classList.add("active");
  if (name === "users") loadAdminUsers();
}

async function loadStats() {
  const res = await Admin.stats();
  const grid = document.getElementById("statsGrid");
  if (!res?.ok) {
    grid.innerHTML = `<div class="stat-card"><p style="color:var(--danger)">${res?.data?.error || "Failed to load stats"}</p></div>`;
    return;
  }
  const s = res.data;
  grid.innerHTML = `
    <div class="stat-card"><div class="stat-number">${s.total_users ?? 0}</div><div class="stat-label">Total Users</div></div>
    <div class="stat-card"><div class="stat-number">${s.total_chats ?? 0}</div><div class="stat-label">Total Chats</div></div>
    <div class="stat-card"><div class="stat-number">${s.total_reports ?? 0}</div><div class="stat-label">Reports</div></div>
    <div class="stat-card"><div class="stat-number">${s.total_uploads ?? 0}</div><div class="stat-label">Uploads</div></div>`;
}

async function loadAdminUsers() {
  const tbody = document.getElementById("usersTableBody");
  tbody.innerHTML = '<tr><td colspan="7" class="loading-state">Loading...</td></tr>';
  const res = await Admin.users();
  if (!res?.ok) {
    tbody.innerHTML = `<tr><td colspan="7" style="color:var(--danger);padding:16px">${res?.data?.error || "Failed"}</td></tr>`;
    return;
  }
  const users = res.data.users || [];
  if (!users.length) { tbody.innerHTML = '<tr><td colspan="7" class="loading-state">No users found</td></tr>'; return; }
  tbody.innerHTML = users.map(u => `
    <tr>
      <td>${u.user_id}</td>
      <td>${escapeHtml(u.username)}</td>
      <td>${escapeHtml(u.email)}</td>
      <td>${u.age || "-"}</td>
      <td>${u.gender || "-"}</td>
      <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : "-"}</td>
      <td><button class="btn-danger-sm" onclick="adminDeleteUser(${u.user_id}, '${escapeHtml(u.username)}')">Delete</button></td>
    </tr>`).join("");
}

async function adminDeleteUser(id, name) {
  if (!confirm(`Delete user "${name}" and all their data?`)) return;
  const res = await Admin.deleteUser(id);
  if (res?.ok) { showToast("User deleted", "success"); loadAdminUsers(); loadStats(); }
  else showToast(res?.data?.error || "Failed", "error");
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Init
loadStats();
