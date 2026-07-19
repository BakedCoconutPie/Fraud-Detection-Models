param(
    [Parameter(Mandatory=$true)]
    [string]$DataDir,

    [ValidateSet("original16", "all")]
    [string]$Subset = "original16",

    [string]$OutDir = "outputs\pastetrace_original16",

    [double]$Threshold = 0.5
)

$ErrorActionPreference = "Stop"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

& $Python "src\pastetrace_if_xgb_shap.py" `
    --data $DataDir `
    --subset $Subset `
    --out $OutDir `
    --threshold $Threshold
