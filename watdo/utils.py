def truncate(string: str, size: int) -> str:
    str_len = len(string)

    if str_len <= size + 2:
        return string

    return string[:size] + ".."
