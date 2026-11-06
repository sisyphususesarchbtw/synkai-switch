$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
& '.venv/Scripts/python.exe' -m synkai --config .local/switch/runtime-config.json
