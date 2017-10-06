# Powershell script to automate build
..\..\..\tools\JackCompiler.bat source
Remove-Item .\build\*.vm
Move-Item .\source\*.vm .\build\
Get-Item .\build\*.vm | ForEach {Write-Host "`t$($_.Name)"}
