
# ============================================================
# NeuroShield AI - PERF-03
# Video Extraction Failure Handling
# ============================================================

$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8000"

$invalidVideo = "https://www.youtube.com/watch?v=00000000000"
$validVideo = "https://www.youtube.com/watch?v=oovO2w5LhsM"

$controlledFailure = $false
$backendOperational = $false
$recoverySuccessful = $false

function Get-AnalysisResult {

    param(
        [string]$VideoUrl
    )

    $body = @{
        youtube_url = $VideoUrl
    } | ConvertTo-Json

    $job = Invoke-RestMethod `
        -Uri "$baseUrl/analyze-video" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body

    for ($i = 1; $i -le 60; $i++) {

        $response = Invoke-RestMethod `
            -Uri "$baseUrl/analysis-status/$($job.job_id)" `
            -Method Get

        if ($response.status -in @(
            "complete", "completed", "failed", "error"
        )) {
            return $response
        }

        Start-Sleep -Seconds 2
    }

    throw "Analysis did not finish within the polling limit."
}

Clear-Host

Write-Host ""
Write-Host "================================================================="
Write-Host "                     NeuroShield AI - PERF-03"
Write-Host "                  Video Extraction Failure Handling"
Write-Host "================================================================="

Write-Host ""
Write-Host "[1/3] UNAVAILABLE VIDEO TEST"
Write-Host "-----------------------------------------------------------------"

try {

    $response = Get-AnalysisResult -VideoUrl $invalidVideo

    Write-Host "Analysis Status : $($response.status)"
    Write-Host "Error Message   : $($response.error)"

    $controlledFailure = (
        $response.status -in @("failed", "error") -and
        -not [string]::IsNullOrWhiteSpace($response.error)
    )

    Write-Host "Controlled Error : $controlledFailure"

} catch {

    Write-Host "Request Error    : $($_.Exception.Message)"
}

Write-Host ""
Write-Host "[2/3] BACKEND AVAILABILITY CHECK"
Write-Host "-----------------------------------------------------------------"

try {

    $health = Invoke-RestMethod `
        -Uri "$baseUrl/model-status" `
        -Method Get

    $backendOperational = ($health.model_loaded -eq $true)

    Write-Host "Backend Reachable : True"
    Write-Host "Model Loaded      : $($health.model_loaded)"
    Write-Host "Model Type        : $($health.model_type)"
    Write-Host "Expected Features : $($health.feature_count)"

} catch {

    Write-Host "Backend Reachable : False"
    Write-Host "Error             : $($_.Exception.Message)"
}

Write-Host ""
Write-Host "[3/3] VALID VIDEO RECOVERY CHECK"
Write-Host "-----------------------------------------------------------------"

try {

    $response = Get-AnalysisResult -VideoUrl $validVideo

    $recoverySuccessful = (
        $response.status -in @("complete", "completed")
    )

    Write-Host "Analysis Status : $($response.status)"
    Write-Host "Recovery        : $recoverySuccessful"

    if ($recoverySuccessful) {
        Write-Host "Analysis Source : $($response.result.analysis_source)"
    }

} catch {

    Write-Host "Recovery Error  : $($_.Exception.Message)"
}

Write-Host ""
Write-Host "================================================================="
Write-Host "                         TEST SUMMARY"
Write-Host "================================================================="

Write-Host ""

Write-Host ("Controlled Failure Handling : " + $(if ($controlledFailure) { "PASS" } else { "FAIL" }))
Write-Host ("Backend Remains Operational : " + $(if ($backendOperational) { "PASS" } else { "FAIL" }))
Write-Host ("Valid Video Recovery        : " + $(if ($recoverySuccessful) { "PASS" } else { "FAIL" }))

Write-Host ""
Write-Host "-----------------------------------------------------------------"

if (
    $controlledFailure -and
    $backendOperational -and
    $recoverySuccessful
) {
    Write-Host "OVERALL TEST STATUS : PASS" -ForegroundColor Green
} else {
    Write-Host "OVERALL TEST STATUS : REQUIRES REVIEW" -ForegroundColor Yellow
}

Write-Host "================================================================="
Write-Host ""
