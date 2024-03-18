"""Decorator utils."""

from __future__ import annotations

from collections.abc import Callable
import functools
from time import sleep
from typing import Any, TypeVar

from pyesef.log import LOGGER

RT = TypeVar("RT")


def retry(
    num_attempts: int = 3,
    exc: type[BaseException] = Exception,
    log: bool = False,
    sleeptime: int = 1,
) -> Callable[[Callable[..., RT]], Callable[..., RT]]:
    """Retry function."""

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        """Create a decorator."""

        @functools.wraps(func)
        def func_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Wrap the function."""
            last_exception = None  # Initialize last_exception variable
            for i in range(num_attempts):
                try:
                    return func(*args, **kwargs)
                except exc as err:
                    last_exception = err  # Update last_exception
                    if i == num_attempts - 1:
                        raise
                    if log:
                        LOGGER.warning(
                            f"Failed with error {err}, trying again",
                        )
                    sleep(sleeptime)

            # If all attempts fail, raise the last caught exception
            if last_exception is not None:
                raise last_exception  # Raise the last caught exception

            raise ValueError(
                "No exception occurred"
            )  # Handle case where no exception was caught

        return func_wrapper

    return decorator
