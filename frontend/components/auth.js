// Redirect if already logged in
if (getToken()) window.location.href = "/frontend/dashboard.html";

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".auth-form").forEach(f => f.classList.add("hidden"));
  document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add("active");
  document.getElementById(tab === "login" ? "loginForm" : "registerForm").classList.remove("hidden");
}

function togglePassword(id) {
  const input = document.getElementById(id);
  input.type = input.type === "password" ? "text" : "password";
}

// Password strength indicator
document.getElementById("regPassword")?.addEventListener("input", function () {
  const val = this.value;
  const bar = document.getElementById("pwStrength");
  if (!val) { bar.className = "pw-strength"; return; }
  const hasUpper = /[A-Z]/.test(val);
  const hasNum = /[0-9]/.test(val);
  const hasSpecial = /[^a-zA-Z0-9]/.test(val);
  const score = (val.length >= 8 ? 1 : 0) + (hasUpper ? 1 : 0) + (hasNum ? 1 : 0) + (hasSpecial ? 1 : 0);
  bar.className = "pw-strength " + (score <= 1 ? "weak" : score <= 2 ? "medium" : "strong");
});

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById("loginBtn");
  const errEl = document.getElementById("loginError");
  errEl.classList.add("hidden");

  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;

  if (!email || !password) {
    errEl.textContent = "Please fill in all fields.";
    errEl.classList.remove("hidden");
    return;
  }

  btn.disabled = true;
  btn.querySelector(".btn-text").textContent = "Logging in...";

  const res = await Auth.login({ email, password });
  btn.disabled = false;
  btn.querySelector(".btn-text").textContent = "Login";

  if (!res || !res.ok) {
    errEl.textContent = res?.data?.error || "Login failed. Please try again.";
    errEl.classList.remove("hidden");
    return;
  }

  setToken(res.data.token);
  setUser(res.data.user);
  window.location.href = "/frontend/dashboard.html";
}

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById("registerBtn");
  const errEl = document.getElementById("registerError");
  errEl.classList.add("hidden");

  const username = document.getElementById("regUsername").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const age = document.getElementById("regAge").value;
  const gender = document.getElementById("regGender").value;

  if (!username || !email || !password) {
    errEl.textContent = "Username, email, and password are required.";
    errEl.classList.remove("hidden");
    return;
  }

  btn.disabled = true;
  btn.querySelector(".btn-text").textContent = "Creating account...";

  const res = await Auth.register({ username, email, password, age: age ? parseInt(age) : null, gender });
  btn.disabled = false;
  btn.querySelector(".btn-text").textContent = "Create Account";

  if (!res || !res.ok) {
    errEl.textContent = res?.data?.error || "Registration failed. Please try again.";
    errEl.classList.remove("hidden");
    return;
  }

  setToken(res.data.token);
  setUser(res.data.user);
  window.location.href = "/frontend/dashboard.html";
}
