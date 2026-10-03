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
rem BL-276: Die Rollen schreiben UTF-8; eine cmd-Konsole zeigt per Vorgabe
rem die OEM-Codepage (850) und malt daraus Zeichensalat - auch in der
rem Handlungsanweisung eines roten Gates. Umgestellt wird nur, wenn eine
rem Konsole antwortet, und danach auf den ALTEN Wert zurueck: chcp ueberlebt
rem setlocal, eine blank umgestellte Shell bliebe nach dem Lauf verstellt.
set "TEAM_CP="
for /f "tokens=2 delims=:." %%C in ('chcp 2^>nul') do set "TEAM_CP=%%C"
if defined TEAM_CP set "TEAM_CP=%TEAM_CP: =%"
if defined TEAM_CP chcp 65001 >nul 2>&1
"%TEAM_PWSH%" -NoProfile -File "%~dp0vollautomatik.ps1" %*
set "TEAM_RC=%ERRORLEVEL%"
if defined TEAM_CP chcp %TEAM_CP% >nul 2>&1
exit /b %TEAM_RC%

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
