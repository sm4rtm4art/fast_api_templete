from typing import Any, Callable, ContextManager, Optional, TypeVar

T = TypeVar("T", bound=Callable[..., Any])

def mock_aws(func: Optional[T] = None) -> T | ContextManager[None]:
    """Mock AWS services using moto."""
    ...
