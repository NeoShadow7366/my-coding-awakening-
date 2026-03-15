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
- Queue controls: failed-only filter, auto-retry policy, clear failed, and clear done
- Toast notifications for queue actions (cancel, retry, clear)
- Local history and gallery persistence
- Dark and light themes

## Release notes

### v0.4.0-queue-stability

- Added queue UX polish with toast notifications and clear-done action.
- Added backend regression coverage including SSE streaming tests.
- Added accessibility improvements for queue controls and toast announcements.
- Fixed queue summary counting to remain stable during rapid cancel/retry transitions.
- Added ComfyUI custom model-path support via extra model paths configuration.

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

On Windows PowerShell, you can use the startup helper to clear port 5000 listeners and launch the app with the project venv:

```powershell
./scripts/start_app.ps1
```

To run a quick readiness check for Ollama, ComfyUI, and Flask:

```powershell
./scripts/preflight.ps1
```

To run an interactive path setup step (Ollama, ComfyUI, and shared model root path):

```powershell
./scripts/preflight.ps1 -ConfigurePaths
```

To run the same checks and launch the app only if Flask is down:

```powershell
./scripts/preflight.ps1 -StartApp
```

To emit machine-readable readiness output:

```powershell
./scripts/preflight.ps1 -Json
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
- Service paths (including shared model root path) are stored in data/service_config.json.
- To deduplicate persisted image history rows, run:

```powershell
& ".venv/Scripts/python.exe" "./scripts/cleanup_history.py" --dry-run
```
