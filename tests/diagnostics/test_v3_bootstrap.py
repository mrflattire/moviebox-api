"""v3 auth/bootstrap isolation test.

v3 is the most likely place to see a rotated-key failure specifically,
since it's the only version with real HMAC request signing
(SECRET_KEY_DEFAULT/SECRET_KEY_ALT) on top of the shared x-user token
trick. A clean 403 here with token bootstrap otherwise looking sane
points at a rotated signing key, not a broader API/schema change.

Usage:
    uv run python test_v3_bootstrap.py
"""

import asyncio
import traceback

from moviebox_api.v3.http_client import MovieBoxHttpClient


async def main():
    print("=" * 60)
    print("v3 AUTH/BOOTSTRAP TEST — api3-6.aoneroom.com (signed requests)")
    print("=" * 60)

    try:
        print("\nOpening MovieBoxHttpClient (triggers _init_client -> "
              "homepage probe -> x-user token harvest, all under signed "
              "headers)...")
        async with MovieBoxHttpClient() as client:
            print(f"  ✓ Client initialized. active_base={client.active_base}")
            print(f"  ✓ runtime token present: {client._runtime_token is not None}")
            if client._runtime_token:
                print(f"    token preview: {str(client._runtime_token)[:20]}...")

    except Exception as e:
        print(f"\n  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()

        err_str = str(e).lower()
        if "403" in err_str or "forbidden" in err_str:
            print(
                "\nA 403 here most likely means the HMAC signing key "
                "(SECRET_KEY_DEFAULT/SECRET_KEY_ALT in v3/constants.py) "
                "has been rotated server-side and no longer matches. "
                "This would be a targeted fix (re-extract the key), not "
                "a full backend rewrite."
            )
        elif "all hosts exhausted" in err_str:
            print(
                "\nAll hosts in HOST_POOL failed — could mean the entire "
                "api3-6 cluster is gone/replaced, or every host is "
                "rejecting the current signing scheme uniformly."
            )
        return

    print("\n✓ v3 signed-request auth bootstrap fully functional — "
          "signing scheme still valid, key has not been rotated (or "
          "you're using an updated key already).")


if __name__ == "__main__":
    asyncio.run(main())