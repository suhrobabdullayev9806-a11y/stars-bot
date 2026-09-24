@echo off
rem ============================================================
rem start_bot.bat - Botni fon rejimida (oynasiz, single-instance)
rem ============================================================
cd /d "%~dp0"

rem Eski jarayonlarni to'xtatish (agar qolgan bo'lsa)
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*src.main*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe'\" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*src.main*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

rem Yangi nusxani yopiq oynada ishga tushirish (pythonw - konzolsiz)
start "" /min "%CD%\venv\Scripts\pythonw.exe" -m src.main
echo Bot ishga tushirildi (single instance).