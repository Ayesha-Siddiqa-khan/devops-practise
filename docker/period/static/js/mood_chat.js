const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatStatus = document.getElementById("chat-status");
const chatResetBtn = document.getElementById("chat-reset");

function addBubble(role, text) {
  if (!chatWindow) {
    return;
  }

  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role === "user" ? "chat-user" : "chat-assistant"}`;

  const lines = String(text).split("\n").filter(Boolean);
  for (const line of lines) {
    const p = document.createElement("p");
    p.textContent = line;
    bubble.appendChild(p);
  }

  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadHistory() {
  try {
    const response = await fetch("/chat/history");
    if (!response.ok) {
      return;
    }
    const payload = await response.json();
    const messages = payload.messages || [];

    if (messages.length > 0 && chatWindow) {
      chatWindow.innerHTML = "";
      messages.forEach((msg) => addBubble(msg.role, msg.text));
    }
  } catch (_err) {
    // Silent fallback for initial page load.
  }
}

if (chatForm && chatInput) {
  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = chatInput.value.trim();
    if (!message) {
      return;
    }

    addBubble("user", message);
    chatInput.value = "";
    chatInput.focus();

    if (chatStatus) {
      chatStatus.textContent = "Thinking of a gentle response...";
    }

    try {
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error("Chat API unavailable");
      }

      const payload = await response.json();
      addBubble("assistant", payload.reply || "I am here with you.");

      if (chatStatus) {
        chatStatus.textContent = payload.disclaimer || "This support chat is educational and non-diagnostic.";
        chatStatus.className = payload.urgent
          ? "text-xs text-rose-700 mt-2"
          : "text-xs text-slate-500 mt-2";
      }
    } catch (_error) {
      addBubble(
        "assistant",
        "I had a small connection issue. Please try again in a moment.\nYou are not alone, and I am here to support you."
      );
      if (chatStatus) {
        chatStatus.textContent = "Temporary issue while sending your message.";
        chatStatus.className = "text-xs text-rose-700 mt-2";
      }
    }
  });

  loadHistory();
}

if (chatResetBtn && chatWindow) {
  chatResetBtn.addEventListener("click", async () => {
    try {
      const response = await fetch("/chat/reset", { method: "POST" });
      if (!response.ok) {
        throw new Error("Unable to clear chat");
      }

      chatWindow.innerHTML = "";
      addBubble("assistant", "Hi, I am here with you.\nHow are you feeling today?");
      if (chatStatus) {
        chatStatus.textContent = "Chat reset. You can start a fresh conversation.";
        chatStatus.className = "text-xs text-slate-500 mt-2";
      }
    } catch (_err) {
      if (chatStatus) {
        chatStatus.textContent = "Could not clear chat right now. Please try again.";
        chatStatus.className = "text-xs text-rose-700 mt-2";
      }
    }
  });
}
