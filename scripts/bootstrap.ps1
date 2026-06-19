param(
    [string]$PythonExe = ".\.venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found at '$PythonExe'. Ensure PyCharm venv exists or pass -PythonExe."
}

Write-Host "Using interpreter: $PythonExe"
& $PythonExe --version

Write-Host "Upgrading pip..."
& $PythonExe -m pip install --upgrade pip

Write-Host "Installing project dependencies..."
& $PythonExe -m pip install -r requirements.txt

Write-Host "Running smoke test..."
& $PythonExe -m pytest -q tests/test_health.py

Write-Host "Bootstrap completed."
