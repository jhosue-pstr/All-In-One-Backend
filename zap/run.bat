@echo off
:: Lanzador simple - delega todo a PowerShell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
