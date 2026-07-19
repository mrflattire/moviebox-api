"""v1 search -> resolve chain test.

Auth already confirmed working. This tests whether the actual data shapes
(search results, item details via HTML scraping, downloadable file URLs)
still match what the Pydantic models / extractors expect. A
pydantic.ValidationError or AttributeError here, despite auth working, 
is the strongest signal of a real backend/schema change, not just an
expired key.

Usage:
    uv run python tests/diagnostics/test_v1_search_resolve.py
"""

import asyncio
import traceback

from moviebox_api.v1.constants import SubjectType
from moviebox_api.v1.core import Search
from moviebox_api.v1.extractor import JsonDetailsExtractor
from moviebox_api.v1.requests import Session

TEST_QUERY = "Fight Club"


async def main():
    print("=" * 60)
    print(f"v1 SEARCH -> RESOLVE TEST — query={TEST_QUERY!r}")
    print("=" * 60)

    session = Session()

    try:
        print("\n[1/3] Search...")
        search = Search(session=session, query=TEST_QUERY, subject_type=SubjectType.ALL)
        results = await search.get_content_model()
        items = getattr(results, "items", None) or getattr(results, "results", None)
        if not items:
            print(f"  ✗ No items found on results model. Raw: {results}")
            return
        target = items[0]
        print(f"  ✓ Got {len(items)} result(s). First: {target}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        return

    try:
        print("\n[2/3] Item details (HTML scrape + JsonDetailsExtractor)...")
        from moviebox_api.v1.core import MovieDetails
        item_details = MovieDetails(target, session=session)
        html = await item_details.get_html_content()
        extractor = JsonDetailsExtractor(html)
        print(f"  ✓ Extracted metadata keys: {list(extractor.metadata.keys())}")
        print(f"  ✓ Seasons found: {len(extractor.seasons)}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\n  This is the HTML-scraping layer specifically — if this "
              "breaks while search worked, it points at a markup/DOM "
              "structure change on the rendered page, exactly the "
              "fragility the v1 docs warn about.")
        return

    try:
        print("\n[3/3] Resolve downloadable file URL...")
        from moviebox_api.v1.download import DownloadableMovieFilesDetail
        downloadable = DownloadableMovieFilesDetail(session, target)
        detail_model = await downloadable.get_content_model()
        print(f"  ✓ Got downloadable files detail: {detail_model}")
    except Exception as e:
        print(f"  ✗ FAILED: {type(e).__name__}: {e}")
        traceback.print_exc()
        print("\n  (Constructor/method signature guessed from cross-referencing "
              "v2/v3 patterns — an AttributeError/TypeError here may just "
              "mean this needs adjusting to v1's actual signature, not "
              "necessarily a real backend break. Check the traceback.)")
        return

    print("\n✓ v1 full chain (search -> details -> resolve) functional.")


if __name__ == "__main__":
    asyncio.run(main())