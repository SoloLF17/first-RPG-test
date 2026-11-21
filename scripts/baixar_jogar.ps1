$ErrorActionPreference = "Stop"

$repo = "SoloLF17/first-RPG-test"
$baseUrl = "https://github.com/$repo/releases/latest/download"
$installDir = Join-Path $env:LOCALAPPDATA "DueloDeVeyrion"
$archive = Join-Path $env:TEMP "duelo-veyrion-windows-x64.zip"

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Invoke-WebRequest "$baseUrl/duelo-veyrion-windows-x64.zip" -OutFile $archive
if (Test-Path $installDir) {
    Get-ChildItem $installDir -Force | Remove-Item -Recurse -Force
}
Expand-Archive $archive -DestinationPath $env:TEMP -Force
Copy-Item (Join-Path $env:TEMP "DueloDeVeyrion\*") $installDir -Recurse -Force
Start-Process (Join-Path $installDir "DueloDeVeyrion.exe")
