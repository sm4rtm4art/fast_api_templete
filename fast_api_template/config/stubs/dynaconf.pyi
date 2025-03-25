from typing import Any, Dict, List, Optional

class Dynaconf:
    def __init__(
        self,
        settings_files: Optional[List[str]] = None,
        validators: Optional[List[Any]] = None,
        envvar_prefix: Optional[str] = None,
        includes: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

class Validator:
    def __init__(
        self,
        name: str,
        default: Any = None,
        cast: Optional[str] = None,
        is_in: Optional[List[Any]] = None,
        required: bool = False,
        when: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None: ...
