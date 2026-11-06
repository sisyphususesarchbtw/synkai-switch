param([Parameter(Mandatory=$true)][string]$AuthFile)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$python = Join-Path $taskRoot '.venv/Scripts/python.exe'
& $python -m synkai.setup prepare
if ($LASTEXITCODE -ne 0) { throw 'Local setup failed.' }
& docker compose -p synkai-switch --env-file .local/switch/.env -f .local/switch/compose.yaml --profile collab --profile gateway up -d
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop, then retry.' }
Write-Host 'Waiting for the bundled Switch setup. The first pull can take several minutes.'
& docker compose -p synkai-switch --env-file .local/switch/.env -f .local/switch/compose.yaml --profile collab --profile gateway wait setup
if ($LASTEXITCODE -ne 0) { throw 'Switch setup did not finish. Inspect compose logs setup.' }
& docker build -t synkai-runner:local runner
if ($LASTEXITCODE -ne 0) { throw 'Verifier image build failed.' }
& docker build -t synkai-coder:local coding-worker
if ($LASTEXITCODE -ne 0) { throw 'Coding image build failed.' }
& $python -m synkai.setup connect --auth-file $AuthFile
if ($LASTEXITCODE -ne 0) { throw 'Agent connection failed.' }
Write-Host 'Ready. Start scripts/start-live.ps1 and scripts/start.ps1 in separate terminals. Private sign-in details: .local/switch/login.txt'
