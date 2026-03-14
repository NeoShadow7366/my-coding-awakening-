param(
    [int]$Port = 5000,
    [string]$OllamaUrl = 'http://localhost:11434/api/tags',
    [string]$ComfyUrl = 'http://localhost:8188/system_stats',
    [switch]$StartApp,
    [switch]$NoKillPort,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

$appUrl = "http://127.0.0.1:$Port/api/status"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$starterScript = Join-Path $PSScriptRoot 'start_app.ps1'

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
