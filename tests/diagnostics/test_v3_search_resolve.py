"""v3 search -> resolve chain test.

Usage:
    uv run python tests/diagnostics/test_v3_search_resolve.py
"""

import asyncio
import traceback

from moviebox_api.v3.constants import CustomResolutionType, SubjectType
from moviebox_api.v3.core import DownloadableFilesDetail, ItemDetails, Search, SearchV2
from moviebox_api.v3.download import resolve_media_file_to_be_downloaded
from moviebox_api.v3.http_client import MovieBoxHttpClient

TEST_QUERY = "Fight Club"


async def try_search_v1(client) -> object | None:
    print("\n[1a/3] Search (v3.core.Search, SEARCH_PATH)...")
    try:
        search = Search(client, query=TEST_QUERY, subject_type=SubjectType.MOVIES)
        results = await search.get_content_model()
        items = results.items
        print(f"  ✓ Got {len(items)} result(s) via Search.")
        return items[0] if items else None
    except Exception as e:
        print(f"  ✗ Search FAILED: {type(e).__name__}: {e}")
        return None


async def try_search_v2(client) -> object | None:
    print("\n[1b/3] Search (v3.core.SearchV2, SEARCH_PATH_V2)...")
    try:
        search = SearchV2(client, query=TEST_QUERY, subject_type=SubjectType.MOVIES)
        results = await search.get_content_model()
        items = results.items
        print(f"  ✓ Got {len(items)} result(s) via SearchV2.")
        return items[0] if items else None
    except Exception as e:
        print(f"  ✗ SearchV2 FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None


async def main():
    print("=" * 60)
    print(f"v3 SEARCH -> RESOLVE TEST — query={TEST_QUERY!r}")
    print("=" * 60)

    async with MovieBoxHttpClient() as client:
        target = await try_search_v1(client)

        if target is None:
            print("\n  Search failed — trying SearchV2 as a fallback to isolate "
                  "whether it's the SEARCH_PATH endpoint specifically that's "
                  "changed, vs a broader auth/backend break.")
            target = await try_search_v2(client)

        if target is None:
            print("\n✗ Both Search and SearchV2 failed — likely a broader issue, "
                  "not just one deprecated endpoint.")
            return

        print(f"\n  Using: {target.title} (id={target.subject_id})")

        try:
            print("\n[2/3] Item details...")
            item_details_inst = ItemDetails(client)
            details = await item_details_inst.get_content_model(target.subject_id)
            print(f"  ✓ Got item details: {details}")
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            return

        try:
            print("\n[3/3] Resolve downloadable file URL...")
            downloadable_inst = DownloadableFilesDetail(client)
            files_detail = await downloadable_inst.get_content_model(
                target.subject_id, release_date=str(target.release_date)
            )
            best = resolve_media_file_to_be_downloaded(
                CustomResolutionType.BEST, files_detail
            )
            print(f"  ✓ Resolved best media file: {str(best.url)[:80]}...")
        except Exception as e:
            print(f"  ✗ FAILED: {type(e).__name__}: {e}")
            traceback.print_exc()
            return

    print("\n✓ v3 full chain (search -> details -> resolve) functional.")


if __name__ == "__main__":
    asyncio.run(main())