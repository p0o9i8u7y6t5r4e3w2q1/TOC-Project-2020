from typing import List


def equal(field: List[str], value: str) -> str:
# [str] join to one field
    return f"{'/'.join(field)} eq '{value}'"

def greater_or_equal(field: List[str], value: str) -> str:
# [str] join to one field
    return f"{'/'.join(field)} ge '{value}'"

def field(field: List[str]) -> str:
    return '/'.join(field)
