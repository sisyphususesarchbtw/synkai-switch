$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    throw 'Create the project environment first; see README.md.'
}
if (-not (Test-Path -LiteralPath 'web/dist/index.html')) {
    & npm.cmd --prefix web run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
}
& '.venv/Scripts/python.exe' -m uvicorn synkai.api:app --host 127.0.0.1 --port 8787
