# Ensure script stops on first error
$ErrorActionPreference = "Stop"

# Get Python version
$pythonVersion = (python --version) -replace "Python ", ""
$pythonMinor = ($pythonVersion -split "\.")[1]

if ([int]$pythonMinor -gt 12) {
    Write-Host "Python version 3.$pythonMinor detected. Python 3.12 or lower is required for setup."
    Write-Host "If you have multiple versions of Python, use a specific one: `python3.12 -m venv .venv`"
    exit 1
}

# Check if Cargo is installed
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Cargo (Rust package manager) is not installed."
    Write-Host "Visit https://www.rust-lang.org/tools/install for installation instructions."
    exit 1
}

# Create virtual environment
python -m venv .venv

# Activate virtual environment
. .\.venv\Scripts\Activate.ps1

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r dev-requirements.txt

# Install pre-commit hooks
pre-commit install

Write-Host "✅ Setup completed successfully!"
