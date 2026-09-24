# ===================================================================
# run-24-7.ps1 - 24/7 xizmat skripti (netstat-based, TEZKOR)
# Bot = 127.0.0.1:18087 port (single-instance guard) LISTEN bo'lgan
# instansiya deb hisoblanadi. Port yo'q bo'lsa -> start_bot.bat orqali
# botni (bitta) ishga tushiradi. CIM ishlatilmaydi (sekin/osilib
# qolishiga yo'l qo'ymaydi). NHF: CIM dan farqli, netstat ~ms.
# ===================================================================

$Project = "C:\Users\user\Documents\Default Project\stars-bot"
$LogFile = Join-Path $Project "data\watchdog.log"
$Port = 18087
$BotBat = Join-Path $Project "start_bot.bat"

function Write-WatchLog {
    param([string]$Msg)
    $Line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $Msg"
    try { Add-Content -Path $LogFile -Value $Line -Encoding UTF8 } catch {}
}

function BotIsAlive {
    # Singleton portga LISTENING borligini tez tekshiramiz
    [bool](netstat -ano 2>$null | Select-String ":$Port " | Select-String "LISTENING")
}

Write-WatchLog "Watchdog ishga tushdi (PID=$PID) -> run-24-7"
$downCount = 0
while ($true) {
    try {
        if (BotIsAlive) {
            if ($downCount -gt 0) {
                Write-WatchLog "Bot tiklandi (port $Port OK)"
            }
            $downCount = 0
        } else {
            $downCount++
            Write-WatchLog "Port $Port band emas (takror $downCount) -> ishga tushirish"
            cmd.exe /c "`"$BotBat`"" | Out-Null
            Start-Sleep -Seconds 12
            if (BotIsAlive) { Write-WatchLog "Bot startdi (OK)" }
            else { Write-WatchLog "Bot hali ham portda yo'q — keyingi turda yana urinamiz" }
        }
    } catch {
        Write-WatchLog "XATO: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 12
}