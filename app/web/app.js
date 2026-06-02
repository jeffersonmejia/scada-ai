const form = document.querySelector("#chatForm");
const emptyPrompt = document.querySelector("#emptyPrompt");
let emptyState = document.querySelector("#emptyState");
const newChatButton = document.querySelector("#newChatButton");
const themeButton = document.querySelector("#themeButton");
const messages = document.querySelector("#messages");
const promptInput = document.querySelector("#prompt");
const sendButton = document.querySelector("#sendButton");
const unavailableMessage = "Lo siento, no puedo responder ahora, intenta mas tarde";
const requestTimeoutMs = 5000;
const emptyPrompts = [
  "Detectar instrucciones maliciosas",
  "Revisar comandos peligrosos",
  "Validar prompts antes del modelo",
  "Bloquear intentos de inyección",
  "Analizar una petición sospechosa"
];

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
  document.documentElement.classList.add("dark");
}

function syncThemeIcon() {
  const icon = themeButton.querySelector("ion-icon");
  const isDark = document.documentElement.classList.contains("dark");
  if (icon) {
    icon.setAttribute("name", isDark ? "sunny-outline" : "moon-outline");
  }
  themeButton.title = isDark ? "Modo claro" : "Modo oscuro";
  themeButton.setAttribute("aria-label", themeButton.title);
}

syncThemeIcon();

if (emptyPrompt) {
  let promptIndex = 0;
  setInterval(() => {
    promptIndex = (promptIndex + 1) % emptyPrompts.length;
    const currentPrompt = document.querySelector("#emptyPrompt");
    if (currentPrompt) {
      currentPrompt.textContent = emptyPrompts[promptIndex];
    }
  }, 2600);
}

function createEmptyState() {
  const section = document.createElement("section");
  section.id = "emptyState";
  section.className = "emptyState";

  const title = document.createElement("h2");
  title.textContent = "¿Qué quieres hacer hoy?";

  const prompt = document.createElement("p");
  prompt.id = "emptyPrompt";
  prompt.textContent = emptyPrompts[0];

  section.appendChild(title);
  section.appendChild(prompt);
  return section;
}

function hideEmptyState() {
  if (emptyState) {
    emptyState.remove();
    emptyState = null;
  }
}

function addMessage(role, content, meta = "") {
  hideEmptyState();
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  if (meta) {
    const small = document.createElement("span");
    small.className = "meta";
    small.textContent = meta;
    bubble.appendChild(small);
  }
  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

function addThinking() {
  const article = document.createElement("article");
  article.className = "message assistant thinking";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  for (let index = 0; index < 3; index += 1) {
    const dot = document.createElement("span");
    dot.className = "dot";
    bubble.appendChild(dot);
  }
  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return article;
}

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), requestTimeoutMs);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

async function modelsUnavailable() {
  const res = await fetchWithTimeout("/health");
  if (!res.ok) return true;

  const payload = await res.json();
  return payload.roberta_loaded !== true || payload.ollama_available !== true;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = new FormData(form).get("prompt").trim();
  if (!prompt) return;

  addMessage("user", prompt);
  promptInput.value = "";
  promptInput.style.height = "auto";
  sendButton.disabled = true;
  const thinking = addThinking();

  try {
    if (prompt.toLowerCase() === "hola" && await modelsUnavailable()) {
      thinking.remove();
      addMessage("assistant", unavailableMessage);
      return;
    }

    const res = await fetchWithTimeout("/web/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt })
    });
    const payload = await res.json();
    thinking.remove();
    const meta = payload.classification
      ? `${payload.decision} · ${payload.classification.label} · ${payload.classification.score}`
      : payload.status || `HTTP ${res.status}`;
    addMessage("assistant", payload.response || payload.message || unavailableMessage, meta);
  } catch (error) {
    thinking.remove();
    addMessage("assistant", unavailableMessage);
  } finally {
    sendButton.disabled = false;
    promptInput.focus();
  }
});

themeButton.addEventListener("click", () => {
  const isDark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
  syncThemeIcon();
});

newChatButton.addEventListener("click", () => {
  messages.replaceChildren();
  emptyState = createEmptyState();
  messages.appendChild(emptyState);
  promptInput.value = "";
  promptInput.style.height = "auto";
  sendButton.disabled = false;
  promptInput.focus();
});

promptInput.addEventListener("input", () => {
  promptInput.style.height = "auto";
  promptInput.style.height = `${Math.min(promptInput.scrollHeight, 150)}px`;
});

promptInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
