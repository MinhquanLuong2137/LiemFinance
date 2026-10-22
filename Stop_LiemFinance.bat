@echo off
setlocal
set "LIEMFINANCE_SCRIPT=%~dp0LiemFinance.py"

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$target = [IO.Path]::GetFullPath($env:LIEMFINANCE_SCRIPT); $processes = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -ieq 'pythonw.exe' -and $_.CommandLine -and $_.CommandLine.IndexOf($target, [StringComparison]::OrdinalIgnoreCase) -ge 0 }); if ($processes.Count -eq 0) { Write-Output 'No LiemFinance server process found.'; exit 0 }; foreach ($process in $processes) { Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop; Write-Output ('Stopped LiemFinance process ' + $process.ProcessId) }"
if errorlevel 1 (
    echo Failed to stop LiemFinance.
    exit /b 1
)

echo LiemFinance stopped.
