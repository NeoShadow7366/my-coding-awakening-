# my-coding-awakening-

A locally-hosted AI interface you run entirely on your own computer and access through your web browser. No cloud, no API keys — everything stays on your machine.

![Functional minimalism UI with dark/light mode, generative chat and sentiment classification](docs/screenshot-placeholder.png)

---

## What you can do

| Feature | Description |
|---|---|
| **Generative AI chat** | Talk with large language models (Llama 3, Mistral, Gemma, …) running locally via [Ollama](https://ollama.com) |
| **Sentiment classification** | Classify text as POSITIVE or NEGATIVE using a lightweight [DistilBERT](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english) model from Hugging Face |
| **Dark / light mode** | Follows your system preference, toggleable at any time |
| **Keyboard accessible** | Full keyboard navigation and screen-reader labels throughout |

---

## Learning concepts

**Generative AI models** produce *new content* by predicting the next token in a sequence.
They are trained on massive text corpora and can generate coherent paragraphs, answer questions, write code, and more.
Examples: GPT-4, Llama 3, Mistral.

**Discriminative models** *classify or label* existing data.
They learn the decision boundary between categories.
The DistilBERT model here is fine-tuned to decide whether a sentence is positive or negative.

---

## Quick start

### 1. Clone the repo and set up Python

```bash
git clone https://github.com/NeoShadow7366/my-coding-awakening-
cd my-coding-awakening-

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Ollama (for generative AI)

Download from **https://ollama.com** and follow the installer for your OS.

Then pull at least one model — Llama 3 is a great starting point:

```bash
ollama pull llama3
```

> **Note:** Ollama runs a local server at `http://localhost:11434`.
> Make sure it is running before you start the web app (`ollama serve`).

### 3. Start the web app

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

---

## Project structure

```
my-coding-awakening-/
├── app.py              ← Flask backend (API routes + AI integration)
├── requirements.txt    ← Python dependencies
├── templates/
│   ├── base.html       ← Shared page layout (header, footer, nav)
│   └── index.html      ← Main interface (generative + discriminative panels)
└── static/
    ├── css/style.css   ← Minimalist stylesheet with dark/light mode tokens
    └── js/main.js      ← Frontend logic (tabs, streaming chat, classification)
```

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | Health of both AI backends |
| `/api/models` | GET | List locally available Ollama models |
| `/api/generate` | POST | Stream a generative response (SSE) |
| `/api/classify` | POST | Classify text with DistilBERT |

### `POST /api/generate`

```json
{
  "model":  "llama3",
  "prompt": "Explain neural networks in simple terms.",
  "system": "You are a friendly teacher."
}
```

### `POST /api/classify`

```json
{ "text": "This is absolutely fantastic!" }
```

Response:
```json
{ "label": "POSITIVE", "score": 0.9998, "model": "distilbert-base-uncased-finetuned-sst-2-english" }
```

---

## UI/UX design principles

This interface follows **functional minimalism**:

- **Clarity first** — every element earns its place; no decorative noise.
- **Performance** — zero external CSS/JS frameworks; pure CSS variables for theming.
- **Accessibility** — semantic HTML, ARIA roles/labels, skip-to-content link, keyboard navigation, visible focus rings.
- **Responsiveness** — single-column layout on mobile, two-column (sidebar + main) on wider screens.
- **Colour tokens** — all colours and spacing are CSS custom properties, making it trivial to retheme.
