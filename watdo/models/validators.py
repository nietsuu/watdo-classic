from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from watdo.errors import InvalidData

T = TypeVar("T")
N = TypeVar("N", int, float)


class DataValidator(ABC, Generic[T]):
    is_mutable = False

    def __init__(self, value: T) -> None:
        self._value: T
        self._set(value)

    @property
    def value(self) -> T:
        return self._value

    def _set(self, value: T) -> T:
        self.validate(value)
        self._value = value
        return self._value

    def set(self, value: T) -> T:
        if not self.is_mutable:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute 'set'"
            )

        return self._set(value)

    @classmethod
    @abstractmethod
    def validate(cls, value: T) -> None:
        raise NotImplementedError


class Number(Generic[N], DataValidator[N], ABC):
    is_inclusive = True
    min_val: N
    max_val: N

    @classmethod
    def validate(cls, value: N) -> None:
        if cls.is_inclusive:
            if value > cls.max_val or value < cls.min_val:
                raise InvalidData(
                    cls,
                    f"value should be from {cls.min_val} to {cls.max_val} only.",
                )
        else:
            if value >= cls.max_val or value <= cls.min_val:
                raise InvalidData(
                    cls,
                    f"value should be between {cls.min_val} and {cls.max_val} only.",
                )


class UTCOffset(Number[float]):
    is_inclusive = False
    min_val = -24
    max_val = 24
