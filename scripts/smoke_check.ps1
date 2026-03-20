param(
    [int]$Port = 5000,
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

$baseUrl = "http://127.0.0.1:$Port"
$healthUrl = "$baseUrl/api/healthz"
$statusUrl = "$baseUrl/api/status"
$indexUrl = "$baseUrl/"

function Invoke-Check {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    try {
        & $Action
        return [ordered]@{ name = $Name; ok = $true; error = '' }
    }
    catch {
        return [ordered]@{ name = $Name; ok = $false; error = $_.Exception.Message }
    }
}

$checks = @()

$checks += Invoke-Check -Name 'healthz' -Action {
    $h = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 15
    if ($h.ok -ne $true) { throw 'healthz ok flag is false' }
    if (-not $h.app.template_version) { throw 'healthz missing app.template_version' }
}

$checks += Invoke-Check -Name 'status' -Action {
    $s = Invoke-RestMethod -Uri $statusUrl -TimeoutSec 15
    if ($null -eq $s.text.available) { throw 'status missing text.available' }
    if ($null -eq $s.image.available) { throw 'status missing image.available' }
}

$checks += Invoke-Check -Name 'index-diagnostics-anchor' -Action {
    $html = Invoke-WebRequest -UseBasicParsing -Uri $indexUrl -TimeoutSec 5
    if ($html.Content -notmatch 'id="diag-backend-health"') {
        throw 'index missing diag-backend-health anchor'
    }
}

$ok = ($checks | Where-Object { -not $_.ok }).Count -eq 0
$report = [ordered]@{
    port = $Port
    base_url = $baseUrl
    ok = $ok
    checks = $checks
    timestamp = (Get-Date).ToUniversalTime().ToString('o')
}

if ($Json) {
    $report | ConvertTo-Json -Depth 8
}
else {
    foreach ($check in $checks) {
        if ($check.ok) {
            Write-Host ("[OK]   {0}" -f $check.name) -ForegroundColor Green
        }
        else {
            Write-Host ("[FAIL] {0}: {1}" -f $check.name, $check.error) -ForegroundColor Red
        }
    }
    if ($ok) {
        Write-Host "Smoke check passed." -ForegroundColor Green
    }
    else {
        Write-Host "Smoke check failed." -ForegroundColor Red
    }
}

if ($ok) { exit 0 }
exit 1
