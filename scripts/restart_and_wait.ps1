param(
    [int]$Port = 5000,
    [int]$TimeoutSec = 45,
    [switch]$NoKillPort,
    [switch]$OpenBrowser
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
$appFile = Join-Path $repoRoot 'app.py'
$healthUrl = "http://127.0.0.1:$Port/api/healthz"

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe. Activate/create the .venv first."
}
if (-not (Test-Path $appFile)) {
    throw "App entrypoint not found at $appFile."
}

if (-not $NoKillPort) {
    $listeners = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($procId in $listeners) {
        if (-not $procId) { continue }
        if ($procId -eq $PID) { continue }
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Output "Stopped PID $procId on port $Port"
        }
        catch {
            Write-Warning ("Could not stop PID {0}: {1}" -f $procId, $_.Exception.Message)
        }
    }
}

Write-Output "Starting app in background on http://127.0.0.1:$Port"
$proc = Start-Process -FilePath $pythonExe -ArgumentList @("`"$appFile`"") -WorkingDirectory $repoRoot -PassThru

$deadline = (Get-Date).AddSeconds([Math]::Max(5, $TimeoutSec))
$ready = $false
while ((Get-Date) -lt $deadline) {
    if ($proc.HasExited) {
        throw "App process exited early with code $($proc.ExitCode)."
    }

    try {
        $resp = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 15
        if ($resp.ok -eq $true) {
            $tmpl = [string]$resp.app.template_version
            $started = [string]$resp.app.started_at
            Write-Output "Backend healthy. template=$tmpl started_at=$started pid=$($proc.Id)"
            $ready = $true
            break
        }
    }
    catch {
    }

    Start-Sleep -Milliseconds 700
}

if (-not $ready) {
    throw "Timed out waiting for $healthUrl after $TimeoutSec seconds."
}

if ($OpenBrowser) {
    Start-Process "http://127.0.0.1:$Port/" | Out-Null
}
