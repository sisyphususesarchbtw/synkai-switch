$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $taskRoot
$taskDocker = Get-Command docker -ErrorAction SilentlyContinue
$taskDockerPath = if ($taskDocker) { $taskDocker.Source } else { 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' }
& $taskDockerPath info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop first. Windows may need a restart after enabling Virtual Machine Platform.' }
& $taskDockerPath build -t synkai-runner:local runner
if ($LASTEXITCODE -ne 0) { throw 'Runner image build failed.' }
