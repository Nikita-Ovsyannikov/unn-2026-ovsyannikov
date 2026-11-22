from typing import Any


class Fake:
    def __init__(self, attributes: dict[str, Any]) -> None:
        for key, value in attributes.items():
            setattr(self, key, value)
