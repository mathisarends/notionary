import asyncio
import logging
from unittest.mock import Mock, patch

import pytest

from notionary.utils.decorators import timed


@pytest.fixture
def mock_logger() -> Mock:
    return Mock(spec=logging.Logger)


@pytest.mark.asyncio
async def test_timed_logs_when_above_threshold(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @timed(min_duration_to_log=0.0)
        async def slow_async_function() -> str:
            await asyncio.sleep(0.01)
            return "result"

        result = await slow_async_function()

    assert result == "result"
    mock_logger.debug.assert_called_once()
    log_message = mock_logger.debug.call_args[0][0]
    assert "slow_async_function()" in log_message
    assert "took" in log_message


@pytest.mark.asyncio
async def test_timed_does_not_log_when_below_threshold(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @timed(min_duration_to_log=999.0)
        async def fast_async_function() -> str:
            return "result"

        result = await fast_async_function()

    assert result == "result"
    mock_logger.debug.assert_not_called()


@pytest.mark.asyncio
async def test_timed_uses_custom_text(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @timed(additional_text="AsyncOperation", min_duration_to_log=0.0)
        async def some_async_function() -> None:
            pass

        await some_async_function()

    mock_logger.debug.assert_called_once()
    log_message = mock_logger.debug.call_args[0][0]
    assert "AsyncOperation()" in log_message


@pytest.mark.asyncio
async def test_timed_preserves_function_metadata() -> None:
    @timed()
    async def documented_async_function() -> str:
        return "test"

    assert documented_async_function.__name__ == "documented_async_function"


@pytest.mark.asyncio
async def test_timed_passes_args_and_kwargs() -> None:
    @timed(min_duration_to_log=999.0)
    async def async_function_with_params(
        a: int, b: str, c: bool = False
    ) -> tuple[int, str, bool]:
        return a, b, c

    result = await async_function_with_params(42, "test", c=True)

    assert result == (42, "test", True)


@pytest.mark.asyncio
async def test_timed_strips_dashes_from_additional_text(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @timed(additional_text="---AsyncOp---", min_duration_to_log=0.0)
        async def some_function() -> None:
            pass

        await some_function()

    log_message = mock_logger.debug.call_args[0][0]
    assert "AsyncOp()" in log_message
    assert "---" not in log_message
