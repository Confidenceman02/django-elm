def alias_type(k: str) -> str:
    return f"{k[0].upper()}{k[1:]}"


def safe_capitalize(k: str) -> str:
    assert k
    if 1 < len(k):
        return f"{k[0].upper()}{k[1:]}"

    return k[0].upper()
