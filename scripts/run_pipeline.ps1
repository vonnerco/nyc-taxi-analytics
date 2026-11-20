<#
    run_pipeline.ps1 - build and test the whole dbt project in one command.

    Run:
        .\scripts\run_pipeline.ps1
        .\scripts\run_pipeline.ps1 -Select "+gld_tip_behavior"
        .\scripts\run_pipeline.ps1 -Select "gold"

    Equivalent to: cd dbt_project; dbt build --profiles-dir .
    dbt build runs every model and every test; a failing test stops the run.
#>
param(
    [string]$Select = ""
)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$dbt = Join-Path $root '.venv\Scripts\dbt.exe'
if (-not (Test-Path -LiteralPath $dbt)) {
    throw "No dbt found in the project venv. Run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt"
}

$project = Join-Path $root 'dbt_project'
$dbtArgs = @('build', '--profiles-dir', '.')
if ($Select) { $dbtArgs += @('--select', $Select) }

Push-Location $project
try {
    & $dbt @dbtArgs
    if ($LASTEXITCODE -ne 0) {
        throw "dbt build failed with exit code $LASTEXITCODE"
    }
    Write-Output "run_pipeline: OK"
}
finally {
    Pop-Location
}
