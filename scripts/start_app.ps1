param(
    [int]$Port = 5000,
    [switch]$NoKillPort
)

$ErrorActionPreference = 'Stop'

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$pythonExe = Join-Path $repoRoot '.venv\Scripts\python.exe'
$appFile = Join-Path $repoRoot 'app.py'

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
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if (-not $proc) { continue }
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Output "Stopped PID $procId ($($proc.ProcessName)) on port $Port"
        }
        catch {
            Write-Warning ("Could not stop PID {0} on port {1}: {2}" -f $procId, $Port, $_.Exception.Message)
        }
    }
}

Write-Output "Starting app on http://127.0.0.1:$Port"
& $pythonExe $appFile
