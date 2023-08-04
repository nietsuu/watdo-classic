import math
import json
from abc import ABC
from typing import cast, Dict, Any, Optional
from dateutil import rrule
from watdo import dt
from watdo.safe_data import SafeData, String, Boolean, Timestamp, UTCOffsetHour


class Model(ABC):
    def __init__(self, *, utc_offset_hour: float, created_at: float) -> None:
        self.utc_offset_hour = UTCOffsetHour(utc_offset_hour)
        self.created_at = Timestamp(created_at)

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue

            if value is None:
                continue

            if not isinstance(value, SafeData):
                t = type(value).__name__
                raise TypeError(f"\"{key}\": '{t}' should be 'SafeData'")

    def as_json(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {}

        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue

            if value is None:
                res[key] = value
            else:
                res[key] = value.value

        return res

    def as_json_str(self, *, indent: Optional[int] = None) -> str:
        return json.dumps(self.as_json(), indent=indent)

    @property
    def date_created(self) -> dt.datetime:
        return dt.fromtimestamp(self.created_at.value, self.utc_offset_hour.value)


class Task(Model):
    def __init__(
        self,
        *,
        title: str,
        category: str,
        is_important: bool,
        utc_offset_hour: float,
        due: Optional[float | str],
        description: Optional[str] = None,
        has_reminder: bool = True,
        last_done: Optional[float] = None,
        next_reminder: Optional[float] = None,
        created_at: float,
    ) -> None:
        self.title = String(title, min_len=1, max_len=200)
        self.category = String(category, min_len=0, max_len=50)
        self.is_important = Boolean(is_important)
        self.due: Optional[Timestamp | String]
        self.description = (
            String(description, min_len=0, max_len=1000) if description else None
        )
        self.has_reminder = Boolean(has_reminder)
        self.last_done = Timestamp(last_done) if last_done else None
        self.next_reminder = Timestamp(next_reminder) if next_reminder else None

        if due is None:
            self.due = None
        elif isinstance(due, float):
            self.due = Timestamp(due)
        elif isinstance(due, str):
            self.due = String(due, min_len=7, max_len=math.inf)
            tz = dt.utc_offset_hour_to_tz(utc_offset_hour)
            dtstart = rrule.rrulestr(due)._dtstart.replace(tzinfo=tz)  # type: ignore[union-attr]
            self._rrule = rrule.rrulestr(due.split("\n")[1], dtstart=dtstart)

        super().__init__(utc_offset_hour=utc_offset_hour, created_at=created_at)

    @property
    def rrule(self) -> rrule.rrule:
        if isinstance(self._rrule, rrule.rrule):
            return self._rrule

        raise TypeError(self._rrule)

    @property
    def due_date(self) -> Optional[dt.datetime]:
        if self.due is None:
            return None

        due = self.due.value

        if isinstance(due, float):
            return dt.fromtimestamp(due, self.utc_offset_hour.value)

        return self._rrule.after(self.last_done_date or self.date_created)

    @property
    def last_done_date(self) -> Optional[dt.datetime]:
        if self.last_done is None:
            return None

        return dt.fromtimestamp(self.last_done.value, self.utc_offset_hour.value)

    @property
    def is_recurring(self) -> bool:
        if self.due is None:
            return False

        return isinstance(self.due.value, str)

    @property
    def is_done(self) -> bool:
        if not self.is_recurring:
            return self.last_done is not None

        if self.last_done is None:
            return False

        if self.next_reminder is None:
            return self.last_done is not None

        return cast(dt.datetime, self.due_date).timestamp() == self.next_reminder.value


class User(Model):
    def __init__(self, *, utc_offset_hour: float, created_at: float) -> None:
        super().__init__(utc_offset_hour=utc_offset_hour, created_at=created_at)
