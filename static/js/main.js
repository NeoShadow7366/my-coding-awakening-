/**
 * Local AI Interface — Frontend JavaScript
 *
 * Responsibilities:
 *  - Tab navigation (Generative ↔ Discriminative)
 *  - Dark / light mode toggle with localStorage persistence
 *  - Status badge polling
 *  - Generative: model list, streaming chat via Server-Sent Events
 *  - Discriminative: classification form + history
 */

'use strict';

/* ── DOM references ──────────────────────────────────────────────────────── */
const themeToggle   = document.getElementById('theme-toggle');
const statusDot     = document.getElementById('status-dot');
const statusText    = document.getElementById('status-text');
const navGenerative = document.getElementById('nav-generative');
const navDisc       = document.getElementById('nav-discriminative');
const panelGen      = document.getElementById('panel-generative');
const panelDisc     = document.getElementById('panel-discriminative');

// Generative
const modelSelect   = document.getElementById('gen-model-select');
const systemPrompt  = document.getElementById('system-prompt');
const chatMessages  = document.getElementById('chat-messages');
const chatForm      = document.getElementById('chat-form');
const chatInput     = document.getElementById('chat-input');
const sendBtn       = document.getElementById('send-btn');
const clearChat     = document.getElementById('clear-chat');

// Discriminative
const classifyForm   = document.getElementById('classify-form');
const classifyInput  = document.getElementById('classify-input');
const classifyBtn    = document.getElementById('classify-btn');
const classifyResult = document.getElementById('classify-result');
const resultLabel    = document.getElementById('result-label');
const resultBar      = document.getElementById('result-bar');
const resultScore    = document.getElementById('result-score');
const discStatus     = document.getElementById('disc-model-status');
const classifyCharCount = document.getElementById('classify-char-count');
const classifyHistory   = document.getElementById('classify-history');
const historyList       = document.getElementById('history-list');

/* ── State ───────────────────────────────────────────────────────────────── */
let isGenerating = false;

/* =========================================================================
   Theme
   ========================================================================= */
function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  // Update icon: moon for dark mode, sun for light
  const path = themeToggle.querySelector('path');
  if (theme === 'dark') {
    path.setAttribute('d', 'M12 3v1m0 16v1m8.66-9H21M3 12H2m15.07-7.07l-.71.71M6.34 17.66l-.71.71M18.37 17.66l-.71-.71M6.34 6.34l-.71-.71M12 7a5 5 0 1 0 0 10A5 5 0 0 0 12 7z');
  } else {
    path.setAttribute('d', 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z');
  }
}

(function initTheme() {
  const saved = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(saved || (prefersDark ? 'dark' : 'light'));
})();

themeToggle.addEventListener('click', () => {
  const current = document.body.getAttribute('data-theme');
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

/* =========================================================================
   Tab navigation
   ========================================================================= */
function showPanel(panel) {
  if (panel === 'generative') {
    panelGen.classList.add('active');
    panelDisc.classList.remove('active');
    panelGen.hidden = false;
    panelDisc.hidden = true;
    navGenerative.classList.add('active');
    navDisc.classList.remove('active');
    navGenerative.setAttribute('aria-selected', 'true');
    navDisc.setAttribute('aria-selected', 'false');
  } else {
    panelDisc.classList.add('active');
    panelGen.classList.remove('active');
    panelDisc.hidden = false;
    panelGen.hidden = true;
    navDisc.classList.add('active');
    navGenerative.classList.remove('active');
    navDisc.setAttribute('aria-selected', 'true');
    navGenerative.setAttribute('aria-selected', 'false');
  }
  localStorage.setItem('activePanel', panel);
}

navGenerative.addEventListener('click', (e) => { e.preventDefault(); showPanel('generative'); });
navDisc.addEventListener('click', (e) => { e.preventDefault(); showPanel('discriminative'); });

// Restore last active panel
(function initPanel() {
  const saved = localStorage.getItem('activePanel');
  showPanel(saved === 'discriminative' ? 'discriminative' : 'generative');
})();

/* =========================================================================
   Status polling
   ========================================================================= */
async function checkStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    const genOk  = data.generative?.available;
    const discOk = data.discriminative?.ready;
    const discErr = data.discriminative?.error;

    if (genOk && discOk) {
      statusDot.className = 'status-dot online';
      statusText.textContent = 'Ready';
    } else if (!genOk && !discOk) {
      statusDot.className = 'status-dot offline';
      statusText.textContent = discErr ? 'Model error' : 'Loading…';
    } else {
      statusDot.className = 'status-dot loading';
      statusText.textContent = 'Partial';
    }

    // Update discriminative sidebar status
    if (discOk) {
      discStatus.textContent = '✓ Model loaded and ready';
      discStatus.style.color = 'var(--clr-accent-pos)';
    } else if (discErr) {
      discStatus.textContent = `Error: ${discErr}`;
      discStatus.style.color = 'var(--clr-accent-neg)';
    } else {
      discStatus.textContent = 'Loading model… (first run may take a minute)';
    }

    // Populate Ollama models
    if (genOk) {
      await loadModels();
    } else {
      setModelSelectMessage('Ollama not found — install from ollama.com');
    }
  } catch {
    statusDot.className = 'status-dot offline';
    statusText.textContent = 'Offline';
  }
}

function setModelSelectMessage(msg) {
  modelSelect.innerHTML = `<option value="">${msg}</option>`;
}

async function loadModels() {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    const models = data.models || [];

    if (models.length === 0) {
      setModelSelectMessage('No models found — run: ollama pull llama3');
      return;
    }

    const currentVal = modelSelect.value;
    modelSelect.innerHTML = models
      .map(m => `<option value="${escHtml(m.name)}">${escHtml(m.name)}</option>`)
      .join('');

    // Re-select previously chosen model if still available
    if (currentVal && [...modelSelect.options].some(o => o.value === currentVal)) {
      modelSelect.value = currentVal;
    }
  } catch {
    setModelSelectMessage('Could not fetch models');
  }
}

// Poll every 5 s; immediate on load
checkStatus();
setInterval(checkStatus, 5000);

/* =========================================================================
   Generative — Chat
   ========================================================================= */

/** Create and append a message bubble, return the bubble element. */
function appendMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message message-${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatMessages.appendChild(wrapper);
  scrollToBottom();
  return bubble;
}

function appendSystemMessage(text) {
  const wrapper = document.createElement('div');
  wrapper.className = 'message message-system';
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  chatMessages.appendChild(wrapper);
  scrollToBottom();
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

clearChat.addEventListener('click', () => {
  chatMessages.innerHTML = '';
  appendSystemMessage('Conversation cleared.');
});

// Auto-resize chat input
chatInput.addEventListener('input', () => {
  chatInput.style.height = 'auto';
  chatInput.style.height = Math.min(chatInput.scrollHeight, 180) + 'px';
});

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (isGenerating) return;

  const prompt = chatInput.value.trim();
  if (!prompt) return;

  const model = modelSelect.value;
  if (!model) {
    appendSystemMessage('Please select a model first.');
    return;
  }

  chatInput.value = '';
  chatInput.style.height = 'auto';

  appendMessage('user', prompt);

  isGenerating = true;
  sendBtn.disabled = true;

  const aiBubble = appendMessage('ai', '');
  aiBubble.classList.add('streaming');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        prompt,
        system: systemPrompt.value.trim(),
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      aiBubble.textContent = `Error: ${err.error || 'Unknown error'}`;
      aiBubble.classList.remove('streaming');
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullText = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const payload = trimmed.slice(5).trim();
        if (payload === '[DONE]') break;

        try {
          const chunk = JSON.parse(payload);
          if (chunk.error) {
            aiBubble.textContent = `Error: ${chunk.error}`;
            aiBubble.classList.remove('streaming');
            return;
          }
          if (chunk.token) {
            fullText += chunk.token;
            aiBubble.textContent = fullText;
            scrollToBottom();
          }
        } catch { /* malformed chunk, skip */ }
      }
    }
  } catch (err) {
    aiBubble.textContent = `Error: ${err.message}`;
  } finally {
    aiBubble.classList.remove('streaming');
    isGenerating = false;
    sendBtn.disabled = false;
    chatInput.focus();
  }
});

// Send on Enter (Shift+Enter = newline)
chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    chatForm.requestSubmit();
  }
});

/* =========================================================================
   Discriminative — Classification
   ========================================================================= */

// Character counter
classifyInput.addEventListener('input', () => {
  classifyCharCount.textContent = `${classifyInput.value.length} / 512`;
});

classifyForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = classifyInput.value.trim();
  if (!text) return;

  classifyBtn.disabled = true;
  classifyBtn.textContent = 'Classifying…';
  classifyResult.hidden = true;

  try {
    const res = await fetch('/api/classify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || 'Classification failed');
      return;
    }

    // Show result card
    const isPos  = data.label === 'POSITIVE';
    const pct    = Math.round(data.score * 100);
    const cls    = isPos ? 'positive' : 'negative';
    const emoji  = isPos ? '😊' : '😞';

    resultLabel.textContent = `${emoji} ${data.label}`;
    resultLabel.className = `result-label ${cls}`;
    resultBar.style.width = `${pct}%`;
    resultBar.className = `result-bar ${cls}`;
    resultScore.textContent = `Confidence: ${pct}%  ·  Model: ${data.model}`;

    classifyResult.hidden = false;

    // Add to history
    addHistoryItem(text, data.label, pct);
  } catch (err) {
    alert(`Error: ${err.message}`);
  } finally {
    classifyBtn.disabled = false;
    classifyBtn.textContent = 'Classify';
  }
});

function addHistoryItem(text, label, pct) {
  const isPos = label === 'POSITIVE';
  const cls   = isPos ? 'positive' : 'negative';

  const li = document.createElement('li');
  li.className = 'history-item';
  li.innerHTML = `
    <span class="history-badge ${cls}" aria-label="${label}">${label}</span>
    <span class="history-text" title="${escHtml(text)}">${escHtml(text)}</span>
    <span class="hint">${pct}%</span>
  `;
  historyList.prepend(li);
  classifyHistory.hidden = false;
}

/* =========================================================================
   Utilities
   ========================================================================= */
function escHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
