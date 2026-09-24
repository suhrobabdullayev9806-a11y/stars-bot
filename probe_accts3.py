import asyncio
import sys

sys.path.insert(0, r"C:\Users\user\Documents\Default Project\stars-bot")

from src.database import Database  # noqa: E402
from src.modules.accounts import AccountsModule  # noqa: E402
from dotenv import load_dotenv, dotenv_values

load_dotenv(r"C:\Users\user\Documents\Default Project\stars-bot\.env")
cfg = dotenv_values(r"C:\Users\user\Documents\Default Project\stars-bot\.env")

DB = r"C:\Users\user\Documents\Default Project\stars-bot\data\stars.db"
TOKEN = cfg.get("BOT_TOKEN", "")


async def main() -> None:
    db = Database(DB)
    await db.connect()
    mod = AccountsModule(db, bot_token=TOKEN)
    rows = await db.fetch_all("SELECT * FROM accounts ORDER BY id DESC")
    for r in rows:
        sid = mod.decrypt_session(r)
        valid = sid and len(sid) > 20 and " " not in sid
        print(
            f"#{r['id']} '{r['title']}' valid={bool(valid)} session_len={len(sid) if sid else 0}"
        )
        if valid:
            print("  test_connection:", await mod.test_connection(r["id"]))
    await db.close()


asyncio.run(main())