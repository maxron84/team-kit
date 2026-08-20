@echo off
rem Bahn: pwsh | Gegenstueck: vollautomatik.sh
rem T.E.A.M. - Aufrufer fuer vollautomatik.ps1. Kein Symlink: der braucht unter
rem Windows Administratorrechte. %~dp0 zeigt auf DIESEN Ordner, es entsteht
rem also keine zweite Kopie, die auseinanderlaufen koennte.
rem BL-123: pwsh wird AUFGELOEST, nicht vorausgesetzt. Steht PowerShell 7 nicht
rem im PATH dieser cmd-Sitzung, meldete diese Datei vorher nur
rem "'pwsh' is not recognized as an internal or external command" - eine
rem Meldung ueber cmd, nicht ueber das Kit. Dieselbe Falle wie bei claude:
rem Eine gescheiterte Aufloesung sieht aus wie ein kaputtes Werkzeug.
setlocal
set "TEAM_PWSH="
for %%P in (pwsh.exe) do if not defined TEAM_PWSH set "TEAM_PWSH=%%~$PATH:P"
if not defined TEAM_PWSH if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" set "TEAM_PWSH=%ProgramFiles%\PowerShell\7\pwsh.exe"
if not defined TEAM_PWSH if exist "%ProgramW6432%\PowerShell\7\pwsh.exe" set "TEAM_PWSH=%ProgramW6432%\PowerShell\7\pwsh.exe"
if not defined TEAM_PWSH if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe" set "TEAM_PWSH=%LOCALAPPDATA%\Microsoft\WindowsApps\pwsh.exe"
if not defined TEAM_PWSH goto :keinpwsh
"%TEAM_PWSH%" -NoProfile -File "%~dp0vollautomatik.ps1" %*
exit /b %ERRORLEVEL%

:keinpwsh
echo FEHLER: PowerShell 7 ^(pwsh^) ist nicht auffindbar.
echo.
echo   Das ist KEIN Fehler des Kits und KEIN Auth-Problem. Der Aufrufer
echo   findet nur den Interpreter nicht - gesucht wurde im PATH und in
echo   den ueblichen Installationsorten.
echo.
echo   Windows PowerShell 5.1 ^(powershell.exe^) genuegt NICHT. Das Kit
echo   braucht pwsh 7:
echo     winget install --id Microsoft.PowerShell --source winget
echo.
echo   Danach eine NEUE Sitzung oeffnen - PATH-Aenderungen erreichen
echo   laufende Shells nicht.
exit /b 127
