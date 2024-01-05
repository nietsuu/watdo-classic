from typing import TYPE_CHECKING, Any, Type
from discord.ext import commands as dc

if TYPE_CHECKING:
    from watdo.models.validators import DataValidator


class CancelCommand(dc.CommandError):
    pass


class CustomException(Exception):
    def __init__(self, message: str, *args: object) -> None:
        super().__init__(message, *args)


class InvalidData(CustomException):
    def __init__(
        self,
        cls: Type["DataValidator[Any]"],
        message: str,
        *args: object,
    ) -> None:
        super().__init__(f"{cls.__name__} {message}", *args)
