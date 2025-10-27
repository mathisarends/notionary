import asyncio
import logging
from unittest.mock import Mock, patch

import pytest

from notionary.utils.decorators import time_execution_async, time_execution_sync


@pytest.fixture
def mock_logger() -> Mock:
    return Mock(spec=logging.Logger)


@pytest.fixture
def class_with_logger(mock_logger: Mock):
    class TestClass:
        def __init__(self) -> None:
            self.logger = mock_logger

    return TestClass()


def test_time_execution_sync_logs_when_above_threshold(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_sync(min_duration_to_log=0.0)
        def slow_function() -> str:
            return "result"

        result = slow_function()

    assert result == "result"
    mock_logger.debug.assert_called_once()
    log_message = mock_logger.debug.call_args[0][0]
    assert "slow_function()" in log_message
    assert "took" in log_message


def test_time_execution_sync_does_not_log_when_below_threshold(
    mock_logger: Mock,
) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_sync(min_duration_to_log=999.0)
        def fast_function() -> str:
            return "result"

        result = fast_function()

    assert result == "result"
    mock_logger.debug.assert_not_called()


def test_time_execution_sync_uses_custom_text(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_sync(additional_text="CustomOperation", min_duration_to_log=0.0)
        def some_function() -> None:
            pass

        some_function()

    mock_logger.debug.assert_called_once()
    log_message = mock_logger.debug.call_args[0][0]
    assert "CustomOperation()" in log_message


def test_time_execution_sync_uses_instance_logger(class_with_logger) -> None:
    @time_execution_sync(min_duration_to_log=0.0)
    def method(self) -> str:
        return "result"

    result = method(class_with_logger)

    assert result == "result"
    class_with_logger.logger.debug.assert_called_once()
    log_message = class_with_logger.logger.debug.call_args[0][0]
    assert "method()" in log_message


def test_time_execution_sync_preserves_function_metadata() -> None:
    @time_execution_sync()
    def documented_function() -> str:
        return "test"

    assert documented_function.__name__ == "documented_function"


def test_time_execution_sync_passes_args_and_kwargs() -> None:
    @time_execution_sync(min_duration_to_log=999.0)
    def function_with_params(a: int, b: str, c: bool = False) -> tuple[int, str, bool]:
        return a, b, c

    result = function_with_params(42, "test", c=True)

    assert result == (42, "test", True)


@pytest.mark.asyncio
async def test_time_execution_async_logs_when_above_threshold(
    mock_logger: Mock,
) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_async(min_duration_to_log=0.0)
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
async def test_time_execution_async_does_not_log_when_below_threshold(
    mock_logger: Mock,
) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_async(min_duration_to_log=999.0)
        async def fast_async_function() -> str:
            return "result"

        result = await fast_async_function()

    assert result == "result"
    mock_logger.debug.assert_not_called()


@pytest.mark.asyncio
async def test_time_execution_async_uses_custom_text(mock_logger: Mock) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_async(additional_text="AsyncOperation", min_duration_to_log=0.0)
        async def some_async_function() -> None:
            pass

        await some_async_function()

    mock_logger.debug.assert_called_once()
    log_message = mock_logger.debug.call_args[0][0]
    assert "AsyncOperation()" in log_message


@pytest.mark.asyncio
async def test_time_execution_async_uses_instance_logger(class_with_logger) -> None:
    @time_execution_async(min_duration_to_log=0.0)
    async def async_method(self) -> str:
        return "result"

    result = await async_method(class_with_logger)

    assert result == "result"
    class_with_logger.logger.debug.assert_called_once()
    log_message = class_with_logger.logger.debug.call_args[0][0]
    assert "async_method()" in log_message


@pytest.mark.asyncio
async def test_time_execution_async_preserves_function_metadata() -> None:
    @time_execution_async()
    async def documented_async_function() -> str:
        return "test"

    assert documented_async_function.__name__ == "documented_async_function"


@pytest.mark.asyncio
async def test_time_execution_async_passes_args_and_kwargs() -> None:
    @time_execution_async(min_duration_to_log=999.0)
    async def async_function_with_params(
        a: int, b: str, c: bool = False
    ) -> tuple[int, str, bool]:
        return a, b, c

    result = await async_function_with_params(42, "test", c=True)

    assert result == (42, "test", True)


def test_time_execution_sync_strips_dashes_from_additional_text(
    mock_logger: Mock,
) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_sync(additional_text="---Operation---", min_duration_to_log=0.0)
        def some_function() -> None:
            pass

        some_function()

    log_message = mock_logger.debug.call_args[0][0]
    assert "Operation()" in log_message
    assert "---" not in log_message


@pytest.mark.asyncio
async def test_time_execution_async_strips_dashes_from_additional_text(
    mock_logger: Mock,
) -> None:
    with patch("logging.getLogger", return_value=mock_logger):

        @time_execution_async(additional_text="---AsyncOp---", min_duration_to_log=0.0)
        async def some_function() -> None:
            pass

        await some_function()

    log_message = mock_logger.debug.call_args[0][0]
    assert "AsyncOp()" in log_message
    assert "---" not in log_message
