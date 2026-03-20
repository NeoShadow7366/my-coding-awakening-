param(
    [int]$Port = 5000,
    [string]$OllamaUrl = 'http://localhost:11434/api/tags',
    [string]$ComfyUrl = 'http://localhost:8188/system_stats',
    [switch]$StartApp,
    [switch]$RestartAndSmoke,
    [int]$WaitTimeoutSec = 45,
    [switch]$OpenBrowser,
    [switch]$ConfigurePaths,
    [switch]$NoKillPort,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

$appUrl = "http://127.0.0.1:$Port/api/status"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$starterScript = Join-Path $PSScriptRoot 'start_app.ps1'
$restartScript = Join-Path $PSScriptRoot 'restart_and_wait.ps1'
$smokeScript = Join-Path $PSScriptRoot 'smoke_check.ps1'
$configPath = Join-Path $repoRoot 'data\service_config.json'

function Load-ServiceConfig {
    if (-not (Test-Path $configPath)) {
        return @{
            ollama_path = ''
            comfyui_path = ''
            shared_models_path = ''
            updated_at = ''
        }
    }

    try {
        $raw = Get-Content -Path $configPath -Raw | ConvertFrom-Json
    }
    catch {
        return @{
            ollama_path = ''
            comfyui_path = ''
            shared_models_path = ''
            updated_at = ''
        }
    }

    return @{
        ollama_path = [string]$raw.ollama_path
        comfyui_path = [string]$raw.comfyui_path
        shared_models_path = [string]$raw.shared_models_path
        updated_at = [string]$raw.updated_at
    }
}

function Save-ServiceConfig {
    param(
        [string]$OllamaPath,
        [string]$ComfyPath,
        [string]$SharedModelsPath
    )

    $parent = Split-Path -Parent $configPath
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $payload = [ordered]@{
        ollama_path = ([string]$OllamaPath).Trim()
        comfyui_path = ([string]$ComfyPath).Trim()
        shared_models_path = ([string]$SharedModelsPath).Trim()
        updated_at = (Get-Date).ToUniversalTime().ToString('o')
    }

    $payload | ConvertTo-Json -Depth 6 | Set-Content -Path $configPath -Encoding UTF8

    if (-not [string]::IsNullOrWhiteSpace($SharedModelsPath)) {
        $root = ([string]$SharedModelsPath).Trim()
        New-Item -ItemType Directory -Path $root -Force | Out-Null
        foreach ($name in @('StableDiffusion', 'Lora', 'VAE', 'Embeddings', 'ControlNet', 'ESRGAN')) {
            New-Item -ItemType Directory -Path (Join-Path $root $name) -Force | Out-Null
        }
    }
}

if ($ConfigurePaths) {
    if ($Json) {
        throw 'Cannot run -ConfigurePaths with -Json because path setup is interactive.'
    }

    $current = Load-ServiceConfig
    Write-Host "\n=== Path Configuration ===" -ForegroundColor Cyan
    Write-Host "Press Enter to keep current values." -ForegroundColor DarkGray

    $ollamaPrompt = "Ollama path [$($current.ollama_path)]"
    $comfyPrompt = "ComfyUI path [$($current.comfyui_path)]"
    $sharedPrompt = "Shared model root path [$($current.shared_models_path)]"

    $newOllama = Read-Host $ollamaPrompt
    $newComfy = Read-Host $comfyPrompt
    $newShared = Read-Host $sharedPrompt

    if ([string]::IsNullOrWhiteSpace($newOllama)) { $newOllama = $current.ollama_path }
    if ([string]::IsNullOrWhiteSpace($newComfy)) { $newComfy = $current.comfyui_path }
    if ([string]::IsNullOrWhiteSpace($newShared)) { $newShared = $current.shared_models_path }

    Save-ServiceConfig -OllamaPath $newOllama -ComfyPath $newComfy -SharedModelsPath $newShared
    Write-Host "Saved path configuration to $configPath" -ForegroundColor Green
}

if ($RestartAndSmoke) {
    if (-not (Test-Path $restartScript)) {
        throw "Missing restart helper: $restartScript"
    }
    if (-not (Test-Path $smokeScript)) {
        throw "Missing smoke-check helper: $smokeScript"
    }

    if (-not $Json) {
        Write-Host "\n=== Restart + Smoke Guardrail ===" -ForegroundColor Cyan
    }

    $restartArgs = @{ Port = $Port; TimeoutSec = $WaitTimeoutSec }
    if ($NoKillPort) {
        $restartArgs.NoKillPort = $true
    }
    if ($OpenBrowser) {
        $restartArgs.OpenBrowser = $true
    }

    & $restartScript @restartArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    $smokeArgs = @{ Port = $Port }
    if ($Json) {
        $smokeArgs.Json = $true
    }
    & $smokeScript @smokeArgs
    exit $LASTEXITCODE
}

function Test-HttpHealth {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [int]$TimeoutSec = 3
    )

    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $TimeoutSec
        return @{
            ok = ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300)
            status = $resp.StatusCode
            error = ''
        }
    }
    catch {
        return @{
            ok = $false
            status = 0
            error = $_.Exception.Message
        }
    }
}

function Write-Check {
    param(
        [string]$Name,
        [hashtable]$Result
    )

    if ($Result.ok) {
        Write-Host ("[OK]   {0} ({1})" -f $Name, $Result.status) -ForegroundColor Green
        return
    }

    $err = $Result.error
    if ([string]::IsNullOrWhiteSpace($err)) {
        $err = 'unreachable'
    }
    Write-Host ("[FAIL] {0} ({1})" -f $Name, $err) -ForegroundColor Red
}

function Build-Report {
    param(
        [hashtable]$Ollama,
        [hashtable]$Comfy,
        [hashtable]$App,
        [bool]$AllReady,
        [bool]$EnginesReady,
        [string]$Action,
        [string]$Message
    )

    [ordered]@{
        repo = [string]$repoRoot
        port = $Port
        endpoints = [ordered]@{
            ollama = $OllamaUrl
            comfyui = $ComfyUrl
            app = $appUrl
        }
        checks = [ordered]@{
            ollama = [ordered]@{ ok = [bool]$Ollama.ok; status = [int]$Ollama.status; error = [string]$Ollama.error }
            comfyui = [ordered]@{ ok = [bool]$Comfy.ok; status = [int]$Comfy.status; error = [string]$Comfy.error }
            app = [ordered]@{ ok = [bool]$App.ok; status = [int]$App.status; error = [string]$App.error }
        }
        summary = [ordered]@{
            all_ready = [bool]$AllReady
            engines_ready = [bool]$EnginesReady
            action = [string]$Action
            message = [string]$Message
        }
        timestamp = (Get-Date).ToString('o')
    }
}

function Emit-Report {
    param([hashtable]$Report)
    if ($Json) {
        $Report | ConvertTo-Json -Depth 8
    }
}

if (-not $Json) {
    Write-Host "\n=== Local AI Preflight ===" -ForegroundColor Cyan
    Write-Host "Repo: $repoRoot"
    Write-Host "App endpoint: $appUrl"
}

$ollama = Test-HttpHealth -Url $OllamaUrl
$comfy = Test-HttpHealth -Url $ComfyUrl
$app = Test-HttpHealth -Url $appUrl -TimeoutSec 5

if (-not $Json) {
    Write-Check -Name 'Ollama' -Result $ollama
    Write-Check -Name 'ComfyUI' -Result $comfy
    Write-Check -Name 'Flask app' -Result $app
}

$allReady = $ollama.ok -and $comfy.ok -and $app.ok
$enginesReady = $ollama.ok -and $comfy.ok

if ($StartApp) {
    if ($app.ok) {
        $report = Build-Report -Ollama $ollama -Comfy $comfy -App $app -AllReady $allReady -EnginesReady $enginesReady -Action 'none' -Message 'App is already running. No startup action needed.'
        Emit-Report -Report $report
        if (-not $Json) {
            Write-Host "\nApp is already running. No startup action needed." -ForegroundColor Yellow
        }
    }
    else {
        if (-not (Test-Path $starterScript)) {
            throw "Missing startup helper: $starterScript"
        }

        $report = Build-Report -Ollama $ollama -Comfy $comfy -App $app -AllReady $allReady -EnginesReady $enginesReady -Action 'starting_app' -Message 'Launching app via scripts/start_app.ps1.'
        Emit-Report -Report $report
        if (-not $Json) {
            Write-Host "\nLaunching app via scripts/start_app.ps1 ..." -ForegroundColor Cyan
        }
        if ($NoKillPort) {
            & $starterScript -Port $Port -NoKillPort
        }
        else {
            & $starterScript -Port $Port
        }
        exit $LASTEXITCODE
    }
}

if ($allReady) {
    $report = Build-Report -Ollama $ollama -Comfy $comfy -App $app -AllReady $allReady -EnginesReady $enginesReady -Action 'ready' -Message 'Preflight complete: all services ready.'
    Emit-Report -Report $report
    if (-not $Json) {
        Write-Host "\nPreflight complete: all services ready." -ForegroundColor Green
    }
    exit 0
}

if ($enginesReady -and -not $app.ok) {
    $report = Build-Report -Ollama $ollama -Comfy $comfy -App $app -AllReady $allReady -EnginesReady $enginesReady -Action 'app_down' -Message 'Engines are ready, app is not running. Use -StartApp to launch.'
    Emit-Report -Report $report
    if (-not $Json) {
        Write-Host "\nEngines are ready, app is not running. Use -StartApp to launch." -ForegroundColor Yellow
    }
    exit 2
}

$report = Build-Report -Ollama $ollama -Comfy $comfy -App $app -AllReady $allReady -EnginesReady $enginesReady -Action 'services_down' -Message 'Preflight incomplete: one or more required services are unavailable.'
Emit-Report -Report $report
if (-not $Json) {
    Write-Host "\nPreflight incomplete: one or more required services are unavailable." -ForegroundColor Red
}
exit 1
