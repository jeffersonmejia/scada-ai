const form = document.querySelector("#chatForm");
const healthButton = document.querySelector("#healthButton");
const themeButton = document.querySelector("#themeButton");
const messages = document.querySelector("#messages");
const promptInput = document.querySelector("#prompt");
const sendButton = document.querySelector("#sendButton");
const unavailableMessage = "Lo siento, en este momento no puedo responder. Intenta más tarde.";

const savedTheme = localStorage.getItem("theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
if (savedTheme === "dark" || (!savedTheme && prefersDark)) {
  document.documentElement.classList.add("dark");
}

function addMessage(role, content, meta = "") {
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
    const res = await fetch("/web/chat", {
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

healthButton.addEventListener("click", async () => {
  const res = await fetch("/health");
  const payload = await res.json();
  addMessage(
    "assistant",
    `Estado: ${payload.status}`,
    `RoBERTa: ${payload.roberta_loaded} · Ollama: ${payload.ollama_available}`
  );
});

themeButton.addEventListener("click", () => {
  const isDark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("theme", isDark ? "dark" : "light");
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
