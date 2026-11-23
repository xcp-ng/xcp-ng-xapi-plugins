from typing import Any, List

class Failure(Exception):
    params: List[str]
    def __init__(self, code: str, params: List[str]) -> None: ...

def dispatch(session: Any, fn: str, args: Any) -> str: ...
