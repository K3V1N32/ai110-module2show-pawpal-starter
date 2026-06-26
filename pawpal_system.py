from __future__ import annotations
from enum import Enum
from typing import Generator


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


class Task:
    def __init__(
        self,
        name: str,
        pet_name: str,
        start_time: int,
        total_blocks: int,
        priority: Priority,
        preference: bool = False,
        daily: bool = False,
        day: str | None = None,
    ) -> None:
        if not daily and day is None:
            raise ValueError("day is required when daily is False")
        self.name = name
        self.pet_name = pet_name
        self.start_time = start_time
        self.total_blocks = total_blocks
        self.priority = priority
        self.preference = preference
        self.daily = daily
        self.day = day
        self.is_complete = False

    def toggle_complete(self) -> None:
        raise NotImplementedError()

    def toggle_preference(self) -> None:
        raise NotImplementedError()

    def toggle_daily(self) -> None:
        raise NotImplementedError()

    def set_priority(self, priority: Priority) -> None:
        raise NotImplementedError()

    def set_day(self, day: str) -> None:
        raise NotImplementedError()

    def set_start_time(self, start: int) -> None:
        raise NotImplementedError()

    def set_total_blocks(self, total: int) -> None:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        raise NotImplementedError()


class Pet:
    def __init__(self, name: str, species: str) -> None:
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        raise NotImplementedError()

    def remove_task(self, task: Task) -> None:
        raise NotImplementedError()

    def get_tasks(self, filter: str | None = None) -> list[Task]:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        raise NotImplementedError()


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []
        self.availability: dict[str, list[bool]] = {
            day: [True] * 24 for day in DAYS
        }

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError()

    def remove_pet(self, pet: Pet) -> None:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        raise NotImplementedError()


class Scheduler:
    def __init__(self, id: int, owner: Owner) -> None:
        self.id = id
        self.owner = owner
        self.weekly_plan: dict[str, list[Task]] = {day: [] for day in DAYS}
        self.plan_explanation: list[str] = []

    def get_tasks(self, pet: Pet | None = None) -> list[Task]:
        raise NotImplementedError()

    def get_sorted_tasks(
        self, sort_type: str = "time", sort_order: str = "ascending"
    ) -> list[Task]:
        raise NotImplementedError()

    def generate_schedule(self) -> Generator:
        # Yields {"conflict": True, "task1": Task, "task2": Task} when a
        # high-priority tie requires user input. Caller resolves by sending
        # back the chosen Task via generator.send(chosen_task).
        # Final yield: {"conflict": False, "final_schedule": dict[str, list[Task]]}
        raise NotImplementedError()

    def get_pet_happiness(self, pet: Pet) -> int:
        raise NotImplementedError()

    def to_dict(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, data: dict) -> Scheduler:
        raise NotImplementedError()


class Storage:
    def __init__(self) -> None:
        self.schedulers: list[Scheduler] = []

    def save(self, scheduler: Scheduler) -> None:
        raise NotImplementedError

    def load(self) -> list[Scheduler]:
        raise NotImplementedError
