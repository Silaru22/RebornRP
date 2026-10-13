# Run this script from an elevated PowerShell session after the bot has been tested manually.
$ErrorActionPreference = 'Stop'

$taskName = 'RebornDiscordBot'
$runner = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'run-bot.ps1')).Path
$powerShell = (Get-Command powershell.exe).Source

$action = New-ScheduledTaskAction `
    -Execute $powerShell `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$runner`""
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal `
    -UserId 'SYSTEM' `
    -LogonType ServiceAccount `
    -RunLevel Highest
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
