param(
    [Parameter(Mandatory=$true)]
    [string]$DataDir
)

$ErrorActionPreference = "Stop"

.\scripts\run_if_xgb_shap.ps1 `
    -DataDir $DataDir `
    -Subset original16 `
    -OutDir "outputs\pastetrace_original16"

.\scripts\run_if_xgb_shap.ps1 `
    -DataDir $DataDir `
    -Subset all `
    -OutDir "outputs\pastetrace_all19"
