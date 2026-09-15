<#
.SYNOPSIS
    Development environment bootstrap for Windows. Idempotent; safe to re-run.
.DESCRIPTION
    Installs the package with development tooling, installs pre-commit hooks if available,
    and verifies the offline core. Requests no credentials and contacts no cloud service.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "==> Python" -ForegroundColor Cyan
python --version

Write-Host "==> Installing the package with development tooling" -ForegroundColor Cyan
python -m pip install --upgrade pip | Out-Null
python -m pip install -e ".[dev]"

if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    Write-Host "==> Installing pre-commit hooks" -ForegroundColor Cyan
    pre-commit install --install-hooks
}

Write-Host "==> Verifying the offline core" -ForegroundColor Cyan
python -m dbmodernize.cli version

Write-Host @"

Ready.

  python -m dbmodernize.cli validate-repo
  python -m dbmodernize.cli validate-scenario scenarios

Note for Windows: all file I/O in this repository is forced to UTF-8 with LF endings.
The default cp1252 codec and CRLF endings would make generated artifacts differ between
contributors and break snapshot comparison.

This toolkit produces plans and evidence. It does not migrate, deploy, or cut over
anything, and it has no cloud credentials.
"@ -ForegroundColor Green
