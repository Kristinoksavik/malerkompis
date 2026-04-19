/**
 * static/js/chat.js — Malerkompis Chat
 * Håndterer chat-boblen og API-kall til /api/chat
 */

let chatMessages = []; // Samtalehistorikk (sendes med hver gang)
let chatOpen = false;

function toggleChat() {
  chatOpen = !chatOpen;
  const panel = document.getElementById("chat-panel");
  panel.classList.toggle("hidden", !chatOpen);
  if (chatOpen) {
    document.getElementById("chat-input").focus();
  }
}

async function sendMessage() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  addMessage("user", text);

  // Legg til i historikk
  chatMessages.push({ role: "user", content: text });

  // Vis "skriver..."-indikator
  const loadingId = addMessage("assistant", "...", true);

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: chatMessages,
        language: localStorage.getItem("lang") || "no"
      })
    });

    const data = await response.json();

    // Fjern loading
    removeMessage(loadingId);

    if (data.error) {
      addMessage("assistant", "Beklager, noe gikk galt. Prøv igjen.");
    } else {
      chatMessages.push({ role: "assistant", content: data.reply });
      addMessage("assistant", data.reply);
    }
  } catch (err) {
    removeMessage(loadingId);
    addMessage("assistant", "Kunne ikke koble til. Sjekk internettforbindelsen.");
  }
}

function addMessage(role, text, isLoading = false) {
  const container = document.getElementById("chat-messages");
  const id = "msg-" + Date.now();
  const div = document.createElement("div");
  div.id = id;
  div.className = "chat-msg " + role;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

// Send med Enter-tast
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("chat-input")?.addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });
});
