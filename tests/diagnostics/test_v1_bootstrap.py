"""v1 auth/bootstrap isolation test.

Tests ONLY the cookie+token bootstrap (_fetch_user_info + _fetch_app_info)
against h5.aoneroom.com. If this fails, nothing downstream in v1 (search,
item details, downloads) can possibly work — no point testing further
until this passes.

Usage:
    uv run python test_v1_bootstrap.py
"""

import asyncio
import traceback

from moviebox_api.v1.requests import Session


async def main():
    print("=" * 60)
    print("v1 AUTH/BOOTSTRAP TEST — h5.aoneroom.com")
    print("=" * 60)

    session = Session()

    try:
        print("\n[1/2] Calling _fetch_user_info() (bearer token via x-user header)...")
        user_info = await session._fetch_user_info()
        print(f"  ✓ Got user_info: token={str(user_info.token)[:20]}...")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\nStopping — token bootstrap is a hard prerequisite for everything else.")
        return

    try:
        print("\n[2/2] Calling _fetch_app_info() (cookie bootstrap)...")
        app_info = await session._fetch_app_info()
        print(f"  ✓ Got app_info: {app_info}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\nToken bootstrap worked but cookie bootstrap failed — "
              "partial breakage, worth isolating which v1 features need "
              "cookies vs just the bearer token.")
        return

    print("\n[verify] Checking session cookies...")
    account_cookie = session._client.cookies.get("account")
    token_cookie = session._client.cookies.get("token")
    print(f"  account cookie: {'present' if account_cookie else 'MISSING'}")
    print(f"  token cookie:   {'present' if token_cookie else 'MISSING'}")

    if account_cookie and token_cookie:
        print("\n✓ v1 auth bootstrap fully functional.")
    else:
        print("\n✗ Bootstrap calls succeeded but expected cookies are missing "
              "— possible silent schema change in the response.")


if __name__ == "__main__":
    asyncio.run(main())