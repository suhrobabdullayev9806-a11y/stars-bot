import asyncio
import sys

sys.path.insert(0, r"C:\Users\user\Documents\Default Project\stars-bot")

from src.database import Database  # noqa: E402
from src.modules.accounts import AccountsModule  # noqa: E402
from dotenv import dotenv_values  # noqa: E402

cfg = dotenv_values(r"C:\Users\user\Documents\Default Project\stars-bot\.env")
TOKEN = cfg.get("BOT_TOKEN", "")
DB = r"C:\Users\user\Documents\Default Project\stars-bot\data\stars.db"


async def main() -> None:
    db = Database(DB)
    await db.connect()
    mod = AccountsModule(db, bot_token=TOKEN)
    rows = await db.fetch_all("SELECT * FROM accounts ORDER BY id DESC")
    if not rows:
        print("NO_ACCOUNTS")
        await db.close()
        return
    for r in rows:
        sid = mod.decrypt_session(r)
        ok, msg = await mod._sender.test_session(sid) if sid and len(sid) > 20 else (False, "short_session")
        print(f"#{r['id']} '{r['title']}' len={len(sid) if sid else 0} test={ok} msg={msg}")
        if not ok:
            await mod.remove(r["id"])
            print(f"  -> o'chirildi (yaroqsiz)")
    await db.close()


asyncio.run(main())