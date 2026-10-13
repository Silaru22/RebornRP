$ErrorActionPreference = 'Stop'

$taskName = 'RebornInfrastructure'
$runner = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'run-infrastructure.ps1')).Path
$powerShell = (Get-Command powershell.exe).Source
$currentUser = [Security.Principal.WindowsIdentity]::GetCurrent().Name

$action = New-ScheduledTaskAction `
    -Execute $powerShell `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $currentUser
$principal = New-ScheduledTaskPrincipal `
    -UserId $currentUser `
    -LogonType Interactive `
    -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 20 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description 'Keeps the resource-limited Reborn WSL2 infrastructure running.' `
    -Force

Start-ScheduledTask -TaskName $taskName
Write-Output "Scheduled task installed and started: $taskName"
