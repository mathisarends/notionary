import logging
from unittest.mock import AsyncMock, patch

import pytest

from notionary.shared.decorators import singleton, timed, with_retry


class TestTimed:
    @pytest.mark.asyncio
    async def test_returns_result(self) -> None:
        @timed()
        async def func() -> int:
            return 42

        result = await func()
        assert result == 42

    @pytest.mark.asyncio
    async def test_logs_when_exceeding_threshold(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        @timed(min_duration_to_log=0.0)
        async def func() -> str:
            return "done"

        with caplog.at_level(logging.DEBUG):
            await func()
        assert len(caplog.records) == 1

    @pytest.mark.asyncio
    async def test_does_not_log_below_threshold(self) -> None:
        @timed(min_duration_to_log=9999.0)
        async def func() -> str:
            return "done"

        with patch("notionary.shared.decorators.logging") as mock_logging:
            mock_logger = mock_logging.getLogger.return_value
            await func()
            mock_logger.debug.assert_not_called()

    @pytest.mark.asyncio
    async def test_uses_additional_text_in_log(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        @timed(additional_text="my-label", min_duration_to_log=0.0)
        async def func() -> None:
            pass

        with caplog.at_level(logging.DEBUG):
            await func()
        assert any("my-label" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_uses_function_name_when_no_additional_text(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        @timed(min_duration_to_log=0.0)
        async def my_function() -> None:
            pass

        with caplog.at_level(logging.DEBUG):
            await my_function()
        assert any("my_function" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_preserves_function_name(self) -> None:
        @timed()
        async def my_func() -> None:
            pass

        assert my_func.__name__ == "my_func"

    @pytest.mark.asyncio
    async def test_passes_arguments_through(self) -> None:
        @timed()
        async def add(a: int, b: int) -> int:
            return a + b

        result = await add(3, 4)
        assert result == 7


class TestWithRetry:
    @pytest.mark.asyncio
    async def test_returns_result_on_success(self) -> None:
        @with_retry(max_retries=3)
        async def func() -> str:
            return "ok"

        result = await func()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_retries_on_exception_and_succeeds(self) -> None:
        call_count = 0

        @with_retry(max_retries=2, initial_delay=0.0)
        async def func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("temporary failure")
            return "recovered"

        result = await func()
        assert result == "recovered"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_raises_after_max_retries_exceeded(self) -> None:
        @with_retry(max_retries=2, initial_delay=0.0)
        async def func() -> None:
            raise RuntimeError("always fails")

        with pytest.raises(RuntimeError, match="always fails"):
            await func()

    @pytest.mark.asyncio
    async def test_total_attempts_equals_max_retries_plus_one(self) -> None:
        call_count = 0

        @with_retry(max_retries=3, initial_delay=0.0)
        async def func() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await func()

        assert call_count == 4

    @pytest.mark.asyncio
    async def test_does_not_retry_unlisted_exception(self) -> None:
        call_count = 0

        @with_retry(max_retries=3, initial_delay=0.0, retry_on_exceptions=(TypeError,))
        async def func() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("not retried")

        with pytest.raises(ValueError, match="not retried"):
            await func()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retries_only_listed_exception(self) -> None:
        call_count = 0

        @with_retry(max_retries=2, initial_delay=0.0, retry_on_exceptions=(ValueError,))
        async def func() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("retried")

        with pytest.raises(ValueError):
            await func()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_sleeps_between_retries(self) -> None:
        @with_retry(max_retries=1, initial_delay=1.0, backoff_factor=2.0)
        async def func() -> None:
            raise RuntimeError("fail")

        with patch(
            "notionary.utils.decorators.asyncio.sleep", new_callable=AsyncMock
        ) as mock_sleep:
            with pytest.raises(RuntimeError):
                await func()
            mock_sleep.assert_called_once_with(1.0)

    @pytest.mark.asyncio
    async def test_applies_backoff_factor(self) -> None:
        @with_retry(max_retries=2, initial_delay=1.0, backoff_factor=3.0)
        async def func() -> None:
            raise RuntimeError("fail")

        with (
            patch(
                "notionary.utils.decorators.asyncio.sleep", new_callable=AsyncMock
            ) as mock_sleep,
            pytest.raises(RuntimeError),
        ):
            await func()

        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert delays == [1.0, 3.0]


class TestSingleton:
    def test_same_instance_returned(self) -> None:
        @singleton
        class MyService:
            pass

        a = MyService()
        b = MyService()
        assert a is b

    def test_init_called_only_once(self) -> None:
        init_count = 0

        @singleton
        class Counter:
            def __init__(self) -> None:
                nonlocal init_count
                init_count += 1

        Counter()
        Counter()
        Counter()
        assert init_count == 1

    def test_state_preserved_across_instances(self) -> None:
        @singleton
        class Config:
            def __init__(self) -> None:
                self.value = 0

        a = Config()
        a.value = 99
        b = Config()
        assert b.value == 99

    def test_different_singleton_classes_are_independent(self) -> None:
        @singleton
        class ServiceA:
            pass

        @singleton
        class ServiceB:
            pass

        assert ServiceA() is not ServiceB()

    def test_isinstance_check_still_works(self) -> None:
        @singleton
        class MyThing:
            pass

        instance = MyThing()
        assert isinstance(instance, MyThing)
