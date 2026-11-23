from typing import Any

class YumBase:
    preconf: Any
    repos: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
