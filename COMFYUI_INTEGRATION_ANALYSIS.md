# ComfyUI Integration Analysis - Links Awakening

## 1. ComfyUI Configuration Storage & Retrieval

### Storage Mechanism
- **File Location**: `data/service_config.json` (persistent JSON file)
- **Config Key**: `comfyui_path` (string, user-provided directory/executable path)
- **Schema Field**:
  ```json
  {
    "ollama_path": "",
    "comfyui_path": "F:/ComfyUI_windows_portable",  // User-configured path
    "shared_models_path": "F:\\StabilityMatrix-win-x64\\Data\\Models",
    "civitai_api_key": "...",
    "huggingface_api_key": "...",
    "default_negative_prompt": "",
    "updated_at": "2026-03-18T14:48:48.040652+00:00"
  }
  ```

### Backend Storage Functions (app.py)
- **`_load_service_config()`** (line 385): Reads service_config.json with JSON validation and fallback to defaults
- **`_save_service_config(config: dict)`** (line 408): Persists configuration with sanitization and auto-creates Stability Matrix folder structure
- **`_default_service_config()`** (line 337): Returns empty config template
- **`_service_config_timestamp()`**: ISO 8601 UTC timestamp for updates
- **API Endpoint**: `GET/POST /api/config/services` (line 3662)

### Frontend Configuration Load/Save (main.js)
- **`loadServiceConfig()`** (line 1994): Fetches from `/api/config/services` and populates UI form
- **`saveServiceConfig(options)`** (line 2020): Posts config changes back to backend with automatic model library reload

---

## 2. Configurations Tab UI Controls & Service Management

### Path Configuration Section (templates/index.html)
Located in sidebar (lines 750-767):
- **ComfyUI Path Input** (`#config-comfyui-path`):
  - Text input with placeholder "e.g. D:/ComfyUI"
  - Browse button (`#config-comfyui-browse`)
  - Hint: "Accepts a ComfyUI folder (main.py/run.bat), or a script path."
  - Accepts both directory paths or executable paths

- **Shared Model Root Path** (`#config-models-path`):
  - Optional Stability Matrix naming root (StableDiffusion, Lora, VAE, Embeddings, ControlNet, ESRGAN)
  - Used by model browser and managed services

- **Save Controls**:
  - "Save Configuration" button (`#config-save-btn`)
  - "Migrate Legacy Model Folders" button (`#config-models-migrate-btn`)
  - Status indicators (`#config-save-status`, `#config-last-saved`)

### Service Control Buttons (lines 815-830)
#### ComfyUI Service Card
```html
<section aria-label="ComfyUI service controls">
  <h2>ComfyUI Service</h2>
  <p>Launch image backend using the configured path.</p>
  <div>
    <button id="config-comfy-start">Start</button>
    <button id="config-comfy-restart">Restart</button>
    <button id="config-comfy-stop">Stop</button>
  </div>
  <p id="config-comfy-status">Awaiting action.</p>
</section>
```

### Service Control APIs (app.py line 3740)
**Endpoint**: `POST /api/service/<service>/<action>`

Supported parameters:
- **service**: `"ollama"` or `"comfyui"`
- **action**: `"start"`, `"stop"`, or `"restart"`

**Response Format**:
```json
{
  "ok": true,
  "service": "comfyui",
  "action": "start",
  "status": "started|already-running|stopped|not-running",
  "pid": 1234
}
```

#### Start Logic
1. Check if service already running via port availability
2. Return "already-running" if reachable
3. Call `_start_configured_service(service, config)` to launch
4. Wait 0.9 seconds, check exit code
5. If process exited immediately, return error with log tail

#### Stop Logic
1. Call `_kill_process_on_port(port)` using OS-specific mechanism
   - **Windows**: PowerShell Get-NetTCPConnection + Stop-Process
   - **Linux**: lsof + kill -9
2. Fallback to stored process handle if port kill fails
3. Clear error state on success

#### Restart Logic
1. Kill existing process on port
2. Terminate stored process handle if still running
3. Call `_start_configured_service()` to relaunch

---

## 3. ComfyUI Folder Structure & Entry Points

### Expected ComfyUI Layout (from `_resolve_comfyui_launch()` line 461)

The app expects one of these folder structures:

#### **Directory Path** (Most Common)
```
ComfyUI/
├── run_nvidia_gpu.bat      [preferred if GPU available]
├── run_cpu.bat             [fallback for CPU-only]
├── run.bat                 [generic runner]
├── main.py                 [fallback if no .bat scripts]
├── models/
│   ├── checkpoints/
│   ├── loras/
│   ├── vae/
│   ├── embeddings/
│   ├── controlnet/
│   └── upscale_models/
├── input/                  [uploaded image staging]
├── output/                 [generated images]
├── python_embeded/         [optional portable Python for Windows]
│   └── python.exe
└── ... (ComfyUI source code)
```

### Startup Priority (Windows)
1. **Batch Scripts** (preferred - maintains ComfyUI's bundled environment):
   - `run_nvidia_gpu.bat` (if available)
   - `run_cpu.bat` (fallback)
   - `run.bat` (generic)
   - Launch: `cmd /c <script>` + `--enable-cors-header *`

2. **Python Direct** (if .bat unavailable):
   - Check for portable Python: `<ComfyUI>/../python_embeded/python.exe`
   - If found: `<portable_python> main.py --enable-cors-header *`
   - Fallback: `<sys.executable> main.py --enable-cors-header *`

3. **Executable Path**:
   - If user specifies `.py` file: same Python logic, cwd = file's parent
   - If user specifies `.bat` or `.cmd`: `cmd /c <path>` with args
   - If user specifies other executable: pass through with args

### Additional ComfyUI Args
- **CORS Header**: `--enable-cors-header "*"` (always added for browser compatibility)

### Service Health Check
- **Port**: 8188 (hardcoded in `SERVICE_PORTS` dict)
- **Base URL**: `COMFYUI_BASE_URL = "http://localhost:8188"` (or env override)
- **Health Paths** (from `_comfy_available()` line 146):
  1. `/system_stats` (primary health endpoint)
  2. `/queue` (fallback - more reliable on some builds)
  3. Returns True if any responds with 200

---

## 4. Version & Update Checking Logic

### Current State: **NO EXPLICIT VERSION CHECKING**

The codebase has **NO** ComfyUI version detection or update checking mechanisms.

#### Asset Versioning (NOT for ComfyUI)
- **ASSET_VERSION** (app.py line 31): `str(int(time.time()))` - only for cache-busting CSS/JS
- Used in templates for `<script src="main.js?v=<version>">`
- Purpose: Force browser refresh of static files after deployment

#### Model Versioning (Local Library Metadata Only)
- **`version_name`** field in local model metadata (line 797 in app.py)
- Only applies to locally downloaded models for user tracking
- Not related to ComfyUI version

#### Precedents in Codebase for Extension
- **Ollama Model Metadata**: Models have sidecar JSON with optional metadata
- **Local Model Metadata**: JSON sidecar files can store custom attributes
- **Service Logs**: Each service logs to `data/service_logs/<service>.log`
  - Could be extended to log version on startup

### What ComfyUI Version Info Would Need
ComfyUI exposes version info via:
1. **`/api/system`** endpoint (returns system_stats)
2. **Git repo metadata** (if cloned from git)
3. **`comfyui_version` file** or similar in root

This is NOT currently queried by the app.

---

## 5. Preflight Setup Script (`scripts/preflight.ps1`)

### Purpose
Interactive setup and health-check helper for Ollama, ComfyUI, and Flask

### Entry Points
```powershell
./scripts/preflight.ps1                    # Health check only
./scripts/preflight.ps1 -ConfigurePaths    # Interactive path setup
./scripts/preflight.ps1 -StartApp          # Launch app if engines ready
./scripts/preflight.ps1 -Json              # Machine-readable output
```

### Path Configuration (lines 87-105)
**Interactive Setup Flow** (when `-ConfigurePaths` used):
```powershell
# Load current config from data/service_config.json
$current = Load-ServiceConfig

# Prompt user for paths (press Enter to keep current)
$ollamaPrompt = "Ollama path [$($current.ollama_path)]"
$comfyPrompt = "ComfyUI path [$($current.comfyui_path)]"
$sharedPrompt = "Shared model root path [$($current.shared_models_path)]"

# Save back with Save-ServiceConfig
Save-ServiceConfig -OllamaPath $newOllama -ComfyPath $newComfy -SharedModelsPath $newShared
```

### Shared Models Root Handling (lines 64-72)
When `SharedModelsPath` configured, auto-creates:
```powershell
foreach ($name in @('StableDiffusion', 'Lora', 'VAE', 'Embeddings', 'ControlNet', 'ESRGAN')) {
    New-Item -ItemType Directory -Path (Join-Path $root $name) -Force | Out-Null
}
```

### Health Check Implementation (lines 103+)
```powershell
function Test-HttpHealth {
    param([string]$Url, [int]$TimeoutSec = 3)
    # Invoke-WebRequest with 3-second timeout (5 sec for Flask)
    # Returns @{ ok = bool; status = int; error = string }
}

# Pre-defined health endpoints:
$OllamaUrl = 'http://localhost:11434/api/tags'
$ComfyUrl = 'http://localhost:8188/system_stats'
$appUrl = "http://127.0.0.1:$Port/api/status"
```

### Status Reporting (lines 142-190)
Builds comprehensive report:
```json
{
  "repo": "/path/to/repo",
  "port": 5000,
  "endpoints": {
    "ollama": "http://localhost:11434/api/tags",
    "comfyui": "http://localhost:8188/system_stats",
    "app": "http://127.0.0.1:5000/api/status"
  },
  "checks": {
    "ollama": { "ok": bool, "status": int, "error": string },
    "comfyui": { "ok": bool, "status": int, "error": string },
    "app": { "ok": bool, "status": int, "error": string }
  },
  "summary": {
    "all_ready": bool,
    "engines_ready": bool,
    "action": "ready|app_down|services_down|starting_app",
    "message": "..."
  }
}
```

### Startup Logic (lines 196-230)
- Always checks all three services first
- If `-StartApp` flag:
  - If app already running: exit 0 (no action)
  - If engines ready: invoke `scripts/start_app.ps1` with `-Port 5000` and optional `-NoKillPort`
  - Exit code 2 if engines down but app not ready
- Without `-StartApp`: just report status, exit 0
- Exit code 2 for incomplete preflight (services down)

---

## 6. JavaScript Service Control Flow (main.js)

### Control Service Function (line 2215)
```javascript
async function controlService(service, action, statusNode, buttonGroup = []) {
  // 1. Disable all buttons in group
  // 2. POST /api/service/<service>/<action>
  // 3. Parse response (ok, status, pid)
  // 4. Update status indicator with result
  // 5. Poll /api/status for health (12 attempts, 1-sec interval)
  // 6. If started/restarted:
  //    - Check reachability on correct port (ollama: text.available, comfyui: image.available)
  //    - Update status "online" or "started but not reachable"
  // 7. Reload models/samplers for ComfyUI
  // 8. Re-enable buttons
}
```

### Status Polling Loop (lines 2240-2260)
```javascript
if ((action === 'start' || action === 'restart') && statusValue === 'started') {
  for (let i = 0; i < 12; i++) {  // 12-second max wait
    await wait(1000);
    const healthRes = await fetch('/api/status');
    const healthData = healthRes.json();
    if (healthData?.image?.available) {  // For ComfyUI
      setConfigStatusLine(statusNode, `${service}: online`, 'ok');
      break;
    }
  }
  if (!reachable) {
    showToast('started but not reachable. Verify launcher/runtime environment.', 'neg');
    appendServiceDiagnosticLogs(service);  // Surface log tail for debugging
  }
}
```

### Button Event Handlers (lines 3203+)
- `#config-comfy-start` → `controlService('comfyui', 'start', ...)`
- `#config-comfy-restart` → `controlService('comfyui', 'restart', ...)`
- `#config-comfy-stop` → `controlService('comfyui', 'stop', ...)`
- Arrow key navigation between start/stop/restart buttons (Home/End support)

---

## 7. Error Handling & Diagnostics

### Service Error Tracking
- **Backend**: `_last_service_errors` dict (app.py line 60)
  - Populated on launch failure or port kill failure
  - Cleared on successful start
  - Exposed via `/api/status` endpoint

### Service Logs
- **Location**: `data/service_logs/<service>.log`
- **Functions**:
  - `_service_log_path(service)` (line 352)
  - `_append_service_log_marker(service, message)` (line 358)
  - `_read_service_log_tail(service, max_chars=1800)` (line 366)
- **Usage**: Tail read on startup failure to expose recent errors

### Launch Failure Detection (app.py line 580)
```python
# If process exits immediately, return a useful failure instead of false "started" state
time.sleep(0.9)
exit_code = proc.poll()
if exit_code is not None:
    log_tail = _read_service_log_tail(service)
    _last_service_errors[service] = (
        f"{service} process exited immediately (code {exit_code})."
        + (f" Recent log output: {log_tail}" if log_tail else "")
    )
    raise RuntimeError("... Verify configured path and runtime dependencies.")
```

### UI Diagnostics Panel (main.js)
- Draws from service logs when user clicks "View Logs" in Configurations
- Function: `appendServiceDiagnosticLogs(service)` - fetches `/api/diagnostics/service-logs`

---

## Summary Table

| Aspect | Details |
|--------|---------|
| **Config Storage** | `data/service_config.json` (JSON file) |
| **Config Key** | `comfyui_path` (string) |
| **API Get Config** | `GET /api/config/services` |
| **API Set Config** | `POST /api/config/services` |
| **Path Picker API** | `POST /api/config/pick-path` (native dialog) |
| **Service Start** | `POST /api/service/comfyui/start` |
| **Service Stop** | `POST /api/service/comfyui/stop` |
| **Service Restart** | `POST /api/service/comfyui/restart` |
| **Health Port** | `8188` |
| **Health Endpoints** | `/system_stats` or `/queue` |
| **Process Tracking** | `_service_processes` dict (in-memory, per app session) |
| **Version Checking** | **NONE** (no implementation) |
| **Update Checking** | **NONE** (no implementation) |
| **Preflight Health** | `http://localhost:8188/system_stats` (3-sec timeout) |
| **Auto-startup Subfolder** | Stability Matrix: StableDiffusion, Lora, VAE, Embeddings, ControlNet, ESRGAN |
| **Launch Method** | Windows: `run_*.bat` scripts > `main.py` with portable Python > system Python |
| **CORS Flag** | Always passes `--enable-cors-header "*"` |

---

## UI/UX Flow

1. User navigates to **Configurations** tab
2. Sidebar shows current saved paths from `data/service_config.json`
3. User clicks **Browse** next to ComfyUI Path → native folder/file picker
4. Selected path auto-saved via `saveServiceConfig()`
5. User clicks **Restart** (or Start/Stop) → `controlService('comfyui', 'restart', ...)`
6. Backend receives `POST /api/service/comfyui/restart`
7. Kills existing process on port 8188
8. Launches new process via `_resolve_comfyui_launch(path)`
9. Polls health for 12 seconds to confirm reachability
10. If online: status → "ComfyUI: online (green)"
11. If unreachable: status → "started but not reachable" + surface logs
12. Model selectors reload on successful launch

---

## Extension Opportunities

Based on this analysis, future ComfyUI integration enhancements could include:

1. **Version Detection** → Query `/api/system` on startup, store in logs/diagnostics
2. **Update Checking** → Compare local version against known releases
3. **Custom Model Paths** → ComfyUI supports `--extra-model-paths` JSON config
4. **Performance Metrics** → Poll `/api/system` for memory/device info during generation
5. **Workflow Management** → Save/restore ComfyUI workflow templates in app config
6. **Extension Management** → List installed ComfyUI custom nodes via API
