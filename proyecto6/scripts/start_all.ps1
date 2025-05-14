# Start all services in separate PowerShell windows
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_auth.ps1"
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_resource.ps1"
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_student.ps1"
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_loan.ps1"
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_notification.ps1"
Start-Process powershell -ArgumentList "-NoExit -File $PSScriptRoot\start_web.ps1"
