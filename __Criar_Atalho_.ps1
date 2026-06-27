$PastaProjeto = $PSScriptRoot

$Desktop = [Environment]::GetFolderPath("Desktop")
$Atalho = Join-Path $Desktop "Hotel Python Palace.lnk"

$Destino = Join-Path $PastaProjeto "exe\menu_hotel.bat"
$Icone = Join-Path $PastaProjeto "static\ico\favicon.ico"

$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($Atalho)

$Shortcut.TargetPath = $Destino
$Shortcut.WorkingDirectory = $PastaProjeto
$Shortcut.IconLocation = $Icone
$Shortcut.Save()

Write-Host "Atalho criado em: $Atalho"
pause