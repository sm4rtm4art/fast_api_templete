"""Type stub for requests_mock package."""

from typing import Any, Callable, ContextManager, Dict, Optional, Pattern, Union

class Mocker:
    """Type stub for requests_mock.Mocker.

    This class is used to mock HTTP requests in tests without making actual HTTP calls.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a new mocker."""
        ...

    def __enter__(self) -> "Mocker":
        """Context manager entry."""
        ...

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        ...

    def get(self, url: str, **kwargs: Any) -> Any:
        """Register a GET request matcher."""
        ...

    def post(self, url: str, **kwargs: Any) -> Any:
        """Register a POST request matcher."""
        ...

    def put(self, url: str, **kwargs: Any) -> Any:
        """Register a PUT request matcher."""
        ...

    def delete(self, url: str, **kwargs: Any) -> Any:
        """Register a DELETE request matcher."""
        ...

    def register_uri(
        self,
        method: str,
        url: Union[str, Pattern],
        status_code: Optional[int] = None,
        json: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        """Register a request matcher with the mock adapter."""
        ...

# Function to create a mocker outside of a context manager
def create_mocker(**kwargs: Any) -> Mocker:
    """Create a Mocker instance."""
    ...
