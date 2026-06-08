$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Assert-LastExit($Message) {
  if ($LASTEXITCODE -ne 0) { throw $Message }
}

Write-Host "0/5 Stopping old AI-Mcode process and cleaning output..."
Get-Process AI-Mcode -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500
Remove-Item "$Root\dist\AI-Mcode.exe" -Force -ErrorAction SilentlyContinue
Remove-Item "$Root\dist\app" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "1/5 Building React frontend..."
Push-Location "$Root\frontend"
npm run build
Assert-LastExit "React build failed"
Pop-Location

Write-Host "2/5 Installing PyInstaller if needed..."
& "..\.venv\Scripts\python.exe" -m pip install pyinstaller
Assert-LastExit "PyInstaller install failed"

Write-Host "3/5 Building AI-Mcode.exe..."
& "..\.venv\Scripts\python.exe" -m PyInstaller --clean --noconfirm AI-Mcode.spec
Assert-LastExit "PyInstaller build failed"

Write-Host "4/5 Preparing portable app folder..."
$AppDir = Join-Path $Root "dist\app"
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
Copy-Item "$Root\dist\AI-Mcode.exe" "$AppDir\AI-Mcode.exe" -Force

Write-Host "5/5 Building installer if Inno Setup exists..."
$ProgramFilesX86 = [Environment]::GetFolderPath("ProgramFilesX86")
$ProgramFiles = [Environment]::GetFolderPath("ProgramFiles")
$IsccCandidates = @(
  (Join-Path $ProgramFilesX86 "Inno Setup 6\ISCC.exe"),
  (Join-Path $ProgramFiles "Inno Setup 6\ISCC.exe")
)
$Iscc = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($Iscc) {
  & $Iscc "$Root\AI-Mcode-installer.iss"
  Assert-LastExit "Installer build failed"
} else {
  Write-Host "Inno Setup not found. Portable exe is ready at dist\AI-Mcode.exe."
}

Write-Host "Done."
Write-Host "EXE: $Root\dist\AI-Mcode.exe"
Write-Host "Portable app: $Root\dist\app\AI-Mcode.exe"
Write-Host "Installer: $Root\installer-dist\AI-Mcode-Setup.exe"
