@echo off
rem Bahn: pwsh | Gegenstueck: frank.sh
rem T.E.A.M. - Aufrufer fuer frank.ps1. Kein Symlink: der braucht unter
rem Windows Administratorrechte. %~dp0 zeigt auf DIESEN Ordner, es entsteht
rem also keine zweite Kopie, die auseinanderlaufen koennte.
pwsh -NoProfile -File "%~dp0frank.ps1" %*
