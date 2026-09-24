@echo off
rem ============================================================
rem autostart_bot.cmd - Windows Startup papkasiga qo'yiladi.
rem Har safar tizimga kirganda botni (24/7 watchdog) yashirin
rem ishga tushiradi. MUTLAQ YO'L ishlatiladi (Startup papkasidan
rem nusxa o'qilganda ham to'g'ri ishlashi uchun).
rem ============================================================
set "PROJECT=C:\Users\user\Documents\Default Project\stars-bot"
start "" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%PROJECT%\run-24-7.ps1"