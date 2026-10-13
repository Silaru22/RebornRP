# Run this script after the bot has been tested manually. It installs a per-user logon task,
# matching the local Teable infrastructure task and avoiding unnecessary administrator rights.
$ErrorActionPreference = 'Stop'

$taskName = 'RebornDiscordBot'
$runner = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'run-bot.ps1')).Path
$powerShell = (Get-Command powershell.exe).Source

$action = New-ScheduledTaskAction `
    -Execute $powerShell `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
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
    -Description 'Reborn Discord bot. Does not manage DayZ or Workshop mods.' `
    -Force

Write-Output "Scheduled task installed: $taskName"
