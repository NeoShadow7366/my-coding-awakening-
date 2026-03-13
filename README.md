# Local AI Inference UI

A local-first inference interface for:
- Text generation through Ollama
- Image generation through ComfyUI

Everything runs on your own machine.

## Features

- Text chat with streaming output
- Advanced text controls: seed, temperature, top-p, top-k, max tokens, negative prompt
- Image generation controls: checkpoint, sampler, seed, steps, CFG, denoise, width/height, batch
- Img2img upload flow
- Queue status panel
- Local history and gallery persistence
- Dark and light themes

## Requirements

- Python 3.10+
- Ollama running at http://localhost:11434
- ComfyUI running at http://localhost:8188

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

4. Open http://localhost:5000

## API endpoints

### Status and text
- GET /api/status
- GET /api/models
- POST /api/generate

### Image generation
- GET /api/image/models
- GET /api/image/samplers
- POST /api/image/generate
- POST /api/image/img2img
- GET /api/image/queue
- GET /api/image/view

### History
- GET /api/history
- POST /api/history

## Notes

- If ComfyUI is down, image endpoints return 503 with helpful error messages.
- If Ollama is down, text generation returns 503.
- History is stored in data/history.json.
