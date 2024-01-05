import time


def ms_now() -> float:
    return time.time_ns() / 1_000_000
