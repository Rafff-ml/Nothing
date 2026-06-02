/**
 * OffPad – Client-side JavaScript
 * Netflix Style & Passkey-Only Auth
 */

const API_BASE = window.location.origin;
const AUTOSAVE_INTERVAL_MS = 3000;
const SESSION_KEY = "offpad_session_v2"; // changed to invalidate old sessions

async function api(method, path, body = null) {
  const session = getSession();
  const headers = { "Content-Type": "application/json" };
  
  if (session && session.passkey) {
    headers["X-Passkey"] = session.passkey;
  }

  const options = {
    method,
    headers,
  };
  if (body) {
    options.body = JSON.stringify(body);
  }
  const res = await fetch(`${API_BASE}${path}`, options);
  const data = await res.json();
  if (!res.ok) {
    if (res.status === 429) {
      throw new Error("Too many requests. Please try again later.");
    }
    throw new Error(data.detail || "Something went wrong.");
  }
  return data;
}

function saveSession(passkey) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ passkey }));
}

function getSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function clearSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

function goToEditor() {
  window.location.href = "/editor";
}

function goHome() {
  window.location.href = "/";
}

// ===================================================================
//  HOME PAGE LOGIC
// ===================================================================

function initHomePage() {
  const initialActions = document.getElementById("initial-actions");
  const docForm = document.getElementById("doc-form");
  const btnShowOpen = document.getElementById("btn-show-open");
  const btnShowCreate = document.getElementById("btn-show-create");
  const passInput = document.getElementById("doc-passkey");
  const btnSubmit = document.getElementById("btn-submit");
  const btnCancel = document.getElementById("btn-cancel");
  const formTitle = document.getElementById("form-title");
  const toast = document.getElementById("toast");

  if (!initialActions) return;

  let currentMode = null; // 'open' or 'create'

  // Auto-login
  const session = getSession();
  if (session && session.passkey) {
    goToEditor();
    return;
  }

  function showToast(message, type = "error") {
    toast.textContent = message;
    toast.className = `toast show toast-${type}`;
    setTimeout(() => {
      toast.classList.remove("show");
    }, 4000);
  }

  function getPasskey() {
    const passkey = passInput.value.trim();
    if (!passkey) {
      showToast("Please enter a passkey.", "error");
      return null;
    }
    return passkey;
  }

  btnShowOpen.addEventListener("click", () => {
    currentMode = "open";
    formTitle.textContent = "Enter passkey to open";
    initialActions.classList.add("hidden");
    docForm.classList.remove("hidden");
    passInput.focus();
  });

  btnShowCreate.addEventListener("click", () => {
    currentMode = "create";
    formTitle.textContent = "Enter passkey to create";
    initialActions.classList.add("hidden");
    docForm.classList.remove("hidden");
    passInput.focus();
  });

  btnCancel.addEventListener("click", () => {
    currentMode = null;
    docForm.classList.add("hidden");
    initialActions.classList.remove("hidden");
    passInput.value = "";
  });

  docForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const passkey = getPasskey();
    if (!passkey) return;
    
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="spinner"></span> Processing…';
    
    try {
      if (currentMode === "open") {
        await api("POST", "/documents/login", { passkey });
        saveSession(passkey);
        goToEditor();
      } else if (currentMode === "create") {
        await api("POST", "/documents/create", { passkey });
        saveSession(passkey);
        showToast("Access granted.", "success");
        setTimeout(goToEditor, 600);
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.textContent = "Submit";
    }
  });
}

// ===================================================================
//  EDITOR PAGE LOGIC
// ===================================================================

function initEditorPage() {
  const editor = document.getElementById("editor");
  if (!editor) return;

  const saveStatusEl = document.getElementById("save-status");

  const session = getSession();
  if (!session || !session.passkey) {
    goHome();
    return;
  }

  const { passkey } = session;

  let lastSavedContent = "";
  let autoSaveTimer = null;
  let isSaving = false;

  function setSaveStatus(state, text) {
    saveStatusEl.className = `save-status ${state}`;
    saveStatusEl.innerHTML = `<span class="save-dot"></span> ${text}`;
  }

  async function loadDocument() {
    setSaveStatus("saving", "Loading…");
    try {
      const doc = await api("GET", `/documents`);
      editor.value = doc.content || "";
      lastSavedContent = editor.value;
      setSaveStatus("saved", "Saved");
    } catch (err) {
      setSaveStatus("error", "Error");
      if (err.message.includes("Invalid")) {
        clearSession();
        goHome();
      }
    }
  }

  async function saveDocument() {
    const currentContent = editor.value;
    if (currentContent === lastSavedContent) return;
    if (isSaving) return;

    isSaving = true;
    setSaveStatus("saving", "Saving…");

    try {
      await api("PUT", `/documents`, {
        content: currentContent,
      });
      lastSavedContent = currentContent;
      setSaveStatus("saved", "Saved");
    } catch (err) {
      setSaveStatus("error", "Error");
    } finally {
      isSaving = false;
    }
  }

  function startAutoSave() {
    autoSaveTimer = setInterval(saveDocument, AUTOSAVE_INTERVAL_MS);
  }

  function stopAutoSave() {
    if (autoSaveTimer) {
      clearInterval(autoSaveTimer);
      autoSaveTimer = null;
    }
  }

  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      e.preventDefault();
      saveDocument();
    }
  });

  window.addEventListener("beforeunload", () => {
    if (editor.value !== lastSavedContent) {
      saveDocument();
    }
  });

  loadDocument().then(() => {
    startAutoSave();
    editor.focus();
  });
}

document.addEventListener("DOMContentLoaded", () => {
  initHomePage();
  initEditorPage();
});
