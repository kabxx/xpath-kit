from typing import Any


def xpath_str(value: Any) -> str:
    """Convert a value to its string representation for XPath, with booleans as 'true'/'false'."""
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
