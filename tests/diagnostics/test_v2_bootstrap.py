"""v2 auth/bootstrap isolation test.

v2 skips v1's cookie/_fetch_app_info step entirely (its Session overrides
that method to raise NotImplementedError — see v2/requests.py) and only
needs the bearer token from _fetch_user_info(). If this fails, nothing
downstream in v2 (search, item details, downloads) can work.

Usage:
    uv run python test_v2_bootstrap.py
"""

import asyncio
import traceback

from moviebox_api.v2.requests import Session


async def main():
    print("=" * 60)
    print("v2 AUTH/BOOTSTRAP TEST — h5-api.aoneroom.com")
    print("=" * 60)

    session = Session()

    try:
        print("\nCalling _fetch_user_info() (bearer token via x-user header)...")
        user_info = await session._fetch_user_info()
        print(f"  ✓ Got user_info: token={str(user_info.token)[:20]}...")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\nStopping — token bootstrap is a hard prerequisite for everything else.")
        return

    print("\n[verify] Confirming ensure_cookies_are_assigned() short-circuits correctly...")
    try:
        result = await session.ensure_cookies_are_assigned()
        print(f"  ✓ ensure_cookies_are_assigned() returned: {result}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print("\n✓ v2 auth bootstrap fully functional.")


if __name__ == "__main__":
    asyncio.run(main())