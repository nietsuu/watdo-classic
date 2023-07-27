import json
from typing import Any, List, Optional, Dict
from redis.asyncio import Redis
from app.models import Task
from app.environ import REDISHOST, REDISPORT, REDISUSER, REDISPASSWORD


class Database:
    def __init__(self) -> None:
        self._connection: "Redis[Any]" = Redis(
            host=REDISHOST,
            port=REDISPORT,
            username=REDISUSER,
            password=REDISPASSWORD,
        )
        self._cache = DatabaseCache(self)

    async def get_user_tasks(
        self, uid: str, *, category: Optional[str] = None
    ) -> List[Task]:
        tasks = []
        tasks_data = await self._cache.lrange(f"tasks.{uid}")

        for raw_data in tasks_data:
            task = Task(**json.loads(raw_data))

            if category is not None:
                if task.category.value != category:
                    continue

            tasks.append(task)

        return tasks

    async def get_user_task(self, uid: str, title: str) -> Optional[Task]:
        for task in await self.get_user_tasks(uid):
            if task.title.value == title:
                return task

        return None

    async def add_user_task(self, uid: str, task: Task) -> None:
        await self._cache.lpush(f"tasks.{uid}", task.as_json_str())

    async def remove_user_task(self, uid: str, task: Task) -> None:
        await self._cache.lrem(f"tasks.{uid}", task.as_json_str())


class DatabaseCache:
    def __init__(self, database: Database) -> None:
        self.db = database
        self._cache: Dict[str, Any] = {}

    async def lrange(self, key: str, *, from_cache: bool = True) -> List[str]:
        if from_cache:
            cached = self._cache.get(key)

            if cached is not None:
                return cached

        data = [d.decode() for d in await self.db._connection.lrange(key, 0, -1)]
        self._cache[key] = data
        return data

    async def lpush(self, key: str, value: Any) -> None:
        await self.db._connection.lpush(key, value)

        try:
            self._cache[key].append(value)
        except KeyError:
            await self.lrange(key, from_cache=False)

    async def lrem(self, key: str, value: Any) -> None:
        await self.db._connection.lrem(key, 1, value)
        self._cache[key].remove(value)
