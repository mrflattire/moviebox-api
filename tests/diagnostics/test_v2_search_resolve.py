"""v2 search -> resolve chain test.

Usage:
    uv run python tests/diagnostics/test_v2_search_resolve.py
"""

import asyncio
import traceback

from moviebox_api.v2.constants import SubjectType
from moviebox_api.v2.core import ItemDetails, Search
from moviebox_api.v2.download import DownloadableSingleFilesDetail
from moviebox_api.v2.requests import Session

TEST_QUERY = "Fight Club"


async def main():
    print("=" * 60)
    print(f"v2 SEARCH -> RESOLVE TEST — query={TEST_QUERY!r}")
    print("=" * 60)

    session = Session()

    try:
        print("\n[1/3] Search...")
        search = Search(session=session, query=TEST_QUERY, subject_type=SubjectType.MOVIES)
        results = await search.get_content_model()
        items = results.items
        if not items:
            print(f"  ✗ No items found. Raw: {results}")
            return
        target = items[0]
        print(f"  ✓ Got {len(items)} result(s). First: {target.title} (id={target.subjectId})")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    try:
        print("\n[2/3] Item details...")
        item_details_inst = ItemDetails(session)
        details = await item_details_inst.get_content_model(target)
        print(f"  ✓ Got item details: {details}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    try:
        print("\n[3/3] Resolve downloadable file URL...")
        downloadable = DownloadableSingleFilesDetail(session, target)
        detail_model = await downloadable.get_content_model()
        print(f"  ✓ Got downloadable files detail: {detail_model}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    print("\n✓ v2 full chain (search -> details -> resolve) functional.")


if __name__ == "__main__":
    asyncio.run(main())