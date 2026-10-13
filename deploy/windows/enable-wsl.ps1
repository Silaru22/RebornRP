# Run from an elevated PowerShell session. This script never restarts Windows.
#Requires -Version 5.1

$ErrorActionPreference = 'Stop'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Administrator privileges are required.'
}

$features = @(
    'Microsoft-Windows-Subsystem-Linux',
    'VirtualMachinePlatform'
)

$restartRequired = $false
foreach ($featureName in $features) {
    $feature = Get-WindowsOptionalFeature -Online -FeatureName $featureName
    if ($feature.State -eq 'Enabled') {
        Write-Output "Already enabled: $featureName"
        continue
    }

    Write-Output "Enabling: $featureName"
    $result = Enable-WindowsOptionalFeature `
        -Online `
        -FeatureName $featureName `
        -All `
        -NoRestart
    if ($result.RestartNeeded) {
        $restartRequired = $true
    }
}

Write-Output "WSL feature preparation complete. Restart required: $restartRequired"
Write-Output 'This script did not restart Windows.'
