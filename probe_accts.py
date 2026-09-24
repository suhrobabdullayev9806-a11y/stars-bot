import asyncio
import sys
sys.path.insert(0, r"C:\Users\user\Documents\Default Project\stars-bot")
from dotenv import load_dotenv

load_dotenv(r"C:\Users\user\Documents\Default Project\stars-bot\.env")

from src.config import load_settings  # noqa: E402
from src.app import App  # noqa: E402


async def main() -> None:
    cfg = load_settings()
    app = App(cfg)
    await app.connect()
    rows = await app.accounts.list_all()
    print("accounts:")
    for r in rows:
        sid = app.accounts.decrypt_session(r)
        print(
            f"  #{r['id']} '{r['title']}' status={r['status']} "
            f"session_len={len(sid) if sid else 0}"
        )
    print("\ntest_connection #1:")
    print(await app.accounts.test_connection(rows[0]["id"]))
    print("\ntest_connection #2:")
    print(await app.accounts.test_connection(rows[1]["id"]))
    await app.close()


asyncio.run(main())