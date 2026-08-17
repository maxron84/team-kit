@echo off
rem T.E.A.M. — Aufrufer fuer team-status.ps1. Kein Symlink: der braucht unter
rem Windows Administratorrechte. %~dp0 zeigt auf DIESEN Ordner, es entsteht
rem also keine zweite Kopie, die auseinanderlaufen koennte.
pwsh -NoProfile -File "%~dp0team-status.ps1" %*
