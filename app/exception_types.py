exception_types = {
    "DUP_VAL_ON_INDEX": "UNIQUE_VIOLATION",
    "ZERO_DIVIDE": "DIVISION_BY_ZERO"
}

def match_exception_type(code: str) -> bool:
    if code in exception_types:
        return True
    return False