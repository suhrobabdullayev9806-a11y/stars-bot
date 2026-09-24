import asyncio
import sys

sys.path.insert(0, r"C:\Users\user\Documents\Default Project\stars-bot")

from src.database import Database  # noqa: E402
from src.modules.accounts import AccountsModule  # noqa: E402

DB = r"C:\Users\user\Documents\Default Project\stars-bot\data\stars.db"


async def main() -> None:
    db = Database(DB)
    await db.connect()
    rows = await db.fetch_all("SELECT * FROM accounts ORDER BY id DESC")
    print("direct fetch accounts rows:", len(rows))
    for r in rows:
        print("  ", r.get("id"), repr(r.get("title")), "status=", r.get("status"))
    mod = AccountsModule(db, bot_token="")
    for r in rows:
        try:
            sid = mod.decrypt_session(r)
            print(f"title={r.get('title')!r} session_len={len(sid) if sid else 0}")
        except Exception as exc:  # noqa: BLE001
            print(f"title={r.get('title')!r} DECRYPT_FAIL {type(exc).__name__}: {exc}")
    await db.close()


asyncio.run(main())