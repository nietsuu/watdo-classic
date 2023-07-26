from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")


class SafeData(ABC, Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

        if not self._is_valid():
            raise ValueError(f"{self.__class__.__name__}: {self.value}")

    @abstractmethod
    def _is_valid(self) -> bool:
        raise NotImplementedError


class String(SafeData[str]):
    def __init__(self, value: str, *, min_len: int, max_len: int) -> None:
        self.min_len = min_len
        self.max_len = max_len
        super().__init__(value)

    def _is_valid(self) -> bool:
        val_len = len(self.value)

        if val_len > self.max_len or val_len < self.min_len:
            return False

        return True


class Boolean(SafeData[bool]):
    def _is_valid(self) -> bool:
        return True


class Number(SafeData[float]):
    def __init__(self, value: float, *, min_val: float, max_val: float) -> None:
        self.min_val = min_val
        self.max_val = max_val
        super().__init__(value)

    def _is_valid(self) -> bool:
        if self.value > self.max_val or self.value < self.min_val:
            return False

        return True