const chatArea = document.getElementById("chatArea");
const form = document.getElementById("chatForm");
const input = document.getElementById("messageInput");
const resetBtn = document.getElementById("resetBtn");

function appendMessage(text, cls="bot") {
  const el = document.createElement("div");
  el.className = "message " + (cls === "user" ? "user" : "bot");
  // allow line breaks
  el.innerHTML = text.replace(/\n/g, "<br>");
  chatArea.appendChild(el);
  chatArea.scrollTop = chatArea.scrollHeight;
}

async function sendMessage(text) {
  appendMessage(text, "user");
  // show temporary "thinking" bubble
  const thinking = document.createElement("div");
  thinking.className = "message bot";
  thinking.id = "thinking";
  thinking.textContent = "FarmAssist is typing…";
  chatArea.appendChild(thinking);
  chatArea.scrollTop = chatArea.scrollHeight;

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text })
    });
    const data = await resp.json();
    document.getElementById("thinking").remove();

    if (resp.ok && data.reply) {
      appendMessage(data.reply, "bot");
    } else if (data.error) {
      appendMessage("Error: " + data.error, "bot");
    } else {
      appendMessage("Unknown error contacting server.", "bot");
    }
  } catch (err) {
    document.getElementById("thinking").remove();
    appendMessage("Network error: " + err.message, "bot");
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const txt = input.value.trim();
  if (!txt) return;
  input.value = "";
  sendMessage(txt);
});

resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  chatArea.innerHTML = "";
  appendMessage("Conversation reset. Ask me about your crops or soil.", "bot");
});

// initial welcome
appendMessage("Hello! I'm FarmAssist. Tell me which crop, location (if you want), and what problem you're seeing.", "bot");
