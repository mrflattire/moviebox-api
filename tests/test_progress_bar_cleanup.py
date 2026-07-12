from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from throttlebuster.core import ThrottleBuster


class DummyStream:
    def __init__(self, headers):
        self.headers = headers

    def raise_for_status(self):
        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_run_closes_progress_bar_after_download(tmp_path):
    buster = ThrottleBuster(dir=tmp_path, tasks=1, part_dir=tmp_path)
    progress_bar = Mock()
    progress_bar.clear = Mock()
    progress_bar.close = Mock()

    stream = DummyStream({"content-length": "10"})

    with patch.object(buster.client, "stream", return_value=stream):
        with patch("throttlebuster.core.CustomTqdm", return_value=progress_bar):
            with patch.object(
                buster,
                "_downloader",
                new=AsyncMock(return_value=Mock()),
            ):
                with patch.object(
                    buster,
                    "_merge_parts",
                    new=AsyncMock(return_value=tmp_path / "done.bin"),
                ):
                    (tmp_path / "done.bin").touch()
                    saved = await buster.run(
                        url="https://example.com/file",
                        filename="test.bin",
                    )

    assert saved.saved_to == tmp_path / "done.bin"
    progress_bar.clear.assert_called_once()
    progress_bar.close.assert_called_once()


@pytest.mark.asyncio
async def test_run_closes_progress_bar_on_retry(tmp_path):
    """Test that progress bar is finalized before each retry attempt."""
    buster = ThrottleBuster(dir=tmp_path, tasks=1, part_dir=tmp_path)

    # Track progress bar instances created during retries
    progress_bars = []

    def create_progress_bar(*args, **kwargs):
        p_bar = Mock()
        p_bar.clear = Mock()
        p_bar.close = Mock()
        progress_bars.append(p_bar)
        return p_bar

    stream = DummyStream({"content-length": "10"})
    call_count = 0

    async def mock_downloader(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        # First call raises timeout to trigger retry
        if call_count == 1:
            raise httpx.ReadTimeout("timeout")
        # Second call succeeds
        return Mock()

    with patch.object(buster.client, "stream", return_value=stream):
        with patch("throttlebuster.core.CustomTqdm", side_effect=create_progress_bar):
            with patch.object(
                buster,
                "_downloader",
                new=AsyncMock(side_effect=mock_downloader),
            ):
                with patch.object(
                    buster,
                    "_merge_parts",
                    new=AsyncMock(return_value=tmp_path / "done.bin"),
                ):
                    (tmp_path / "done.bin").touch()
                    saved = await buster.run(
                        url="https://example.com/file",
                        filename="test.bin",
                        timeout_retry_attempts=1,
                    )

    assert saved.saved_to == tmp_path / "done.bin"
    # Should have created a progress bar for the initial attempt and one for the retry
    assert len(progress_bars) == 2
    # Both should be finalized
    for p_bar in progress_bars:
        p_bar.close.assert_called_once()
        p_bar.clear.assert_called_once()
