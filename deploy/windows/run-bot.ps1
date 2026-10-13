$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$logDirectory = Join-Path $projectRoot 'logs'
$logPath = Join-Path $logDirectory 'bot.log'

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Python environment not found: $pythonPath"
}

Set-Location -LiteralPath $projectRoot
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
# Windows PowerShell 5 surfaces a native process' stderr as an ErrorRecord. Discord.py writes
# normal warnings there, so Stop would terminate the otherwise healthy bot during startup.
$ErrorActionPreference = 'Continue'
& $pythonPath -m src.main *>> $logPath
exit $LASTEXITCODE
