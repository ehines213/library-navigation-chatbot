(function () {
  const cfg = window.LNC_CONFIG || {};
  const backendUrl = String(cfg.backendUrl || "").replace(/\/+$/, "");
  const apiKey = String(cfg.apiKey || "");

  if (!backendUrl) {
    console.error("Missing backendUrl in LNC_CONFIG");
    return;
  }

  const btn = document.createElement("button");
  btn.id = "lnc-chatbot-button";
  btn.type = "button";
  btn.textContent = "Need help finding something?";

  const panel = document.createElement("div");
  panel.id = "lnc-chatbot-panel";
  panel.innerHTML = [
    '<div id="lnc-chatbot-header">',
      '<div>Navigation Assistant</div>',
      '<button id="lnc-chatbot-close" type="button">✕</button>',
    '</div>',
    '<div id="lnc-chatbot-messages"></div>',
    '<form id="lnc-chatbot-form">',
      '<input id="lnc-chatbot-input" type="text" placeholder="Ask: hours, library card, printing..." />',
      '<button type="submit">Send</button>',
    '</form>'
  ].join("");

  document.body.appendChild(btn);
  document.body.appendChild(panel);

  const closeBtn = document.getElementById("lnc-chatbot-close");
  const messagesEl = document.getElementById("lnc-chatbot-messages");
  const form = document.getElementById("lnc-chatbot-form");
  const input = document.getElementById("lnc-chatbot-input");

  function addMsg(role, text, links) {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${role}:</strong> ${text}`;
    messagesEl.appendChild(div);

    if (Array.isArray(links)) {
      links.forEach(l => {
        const a = document.createElement("a");
        a.href = l.url;
        a.target = "_blank";
        a.textContent = l.title || l.url;
        messagesEl.appendChild(a);
      });
    }
  }

  btn.onclick = () => {
    panel.style.display = "block";
    if (!messagesEl.dataset.welcome) {
      messagesEl.dataset.welcome = "1";
      addMsg("Bot", "Hi! Ask me about hours, printing, events, or library cards.");
    }
  };

  closeBtn.onclick = () => panel.style.display = "none";

  form.onsubmit = async (e) => {
    e.preventDefault();
    const msg = input.value.trim();
    if (!msg) return;
    input.value = "";

    addMsg("You", msg);

    try {
      const res = await fetch(`${backendUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": apiKey
        },
        body: JSON.stringify({ message: msg })
      });

      const data = await res.json();
      addMsg("Bot", data.reply, data.links);
    } catch (err) {
      addMsg("Bot", "Chat service unavailable.");
      console.error(err);
    }
  };
})();

