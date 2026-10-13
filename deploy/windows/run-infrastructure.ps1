$ErrorActionPreference = 'Stop'

$wsl = (Get-Command wsl.exe).Source
& $wsl `
    -d 'Ubuntu-24.04' `
    -u root `
    -- /usr/local/sbin/reborn-infrastructure
exit $LASTEXITCODE
