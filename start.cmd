@echo off
start "Converter" "C:\Program Files\PowerShell\7\pwsh.exe" -NoExit -ExecutionPolicy Bypass -File "%~dp0main_script.ps1"
