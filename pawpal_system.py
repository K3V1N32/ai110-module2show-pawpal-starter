from __future__ import annotations
import json
import os
import random
from enum import Enum
from typing import Generator


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

DAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

PATH = "data/schedulers.json"

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

    def __repr__ (self) -> str:
        """Return a human-readable summary of the task including schedule, priority, and status."""
        if self.daily:
            return f"The task {self.name} for {self.pet_name} is scheduled daily at {self.start_time}:00 for {self.total_blocks} hour(s) with priority {self.priority.name}. Preference: {self.preference}. Completion status: {'Complete' if self.is_complete else 'Incomplete'}."
        else:
            return f"The task {self.name} for {self.pet_name} is scheduled for {self.day} at {self.start_time}:00 for {self.total_blocks} hour(s) with priority {self.priority.name}. Preference: {self.preference}. Completion status: {'Complete' if self.is_complete else 'Incomplete'}."

    def toggle_complete(self) -> None:
        """Flip the task's completion status between complete and incomplete."""
        self.is_complete = not self.is_complete

    def toggle_preference(self) -> None:
        """Flip whether this task is marked as a preferred time slot."""
        self.preference = not self.preference

    def toggle_daily(self) -> None:
        """Toggle between daily recurrence and single-day scheduling; requires set_day() first when disabling daily."""
        # When switching from daily to day-specific, day must be set first via set_day
        if self.daily and self.day is None:
            raise ValueError("Set a specific day via set_day() before disabling daily.")
        self.daily = not self.daily

    def set_priority(self, priority: Priority) -> None:
        """Set the scheduling priority for this task."""
        self.priority = priority

    def set_day(self, day: str) -> None:
        """Set the specific day this task is scheduled on; must be a valid day string."""
        if day not in DAYS:
            raise ValueError(f"day must be one of {DAYS}")
        self.day = day

    def set_start_time(self, start: int) -> None:
        """Set the start hour for this task in 24-hour format (e.g. 8 for 8am)."""
        self.start_time = start

    def set_total_blocks(self, total: int) -> None:
        """Set the duration in half-hour blocks (1–8, i.e. 30 min to 4 hours)."""
        if total < 1 or total > 8:
            raise ValueError("total_blocks must be between 1 and 8 (30 min to 4 hours)")
        self.total_blocks = total

    def to_dict(self) -> dict:
        """Serialize the task to a JSON-compatible dict."""
        return {
            "name": self.name,
            "pet_name": self.pet_name,
            "start_time": self.start_time,
            "total_blocks": self.total_blocks,
            "priority": self.priority.name,
            "preference": self.preference,
            "daily": self.daily,
            "day": self.day,
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize a Task from a dict produced by to_dict()."""
        task = cls(
            name=data["name"],
            pet_name=data["pet_name"],
            start_time=data["start_time"],
            total_blocks=data["total_blocks"],
            priority=Priority[data["priority"]],
            preference=data["preference"],
            daily=data["daily"],
            day=data.get("day"),
        )
        task.is_complete = data.get("is_complete", False)
        return task


class Pet:
    def __init__(self, name: str, species: str) -> None:
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    def __repr__(self) -> str:
        """Return a brief summary of the pet's name, species, and task count."""
        return f"{self.name} is a {self.species} with {len(self.tasks)} task(s)."

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_tasks(self, filter: str | None = None) -> list[Task]:
        """Return tasks filtered by a day name, 'daily', 'complete', 'incomplete', or all if None."""
        if filter is None:
            return list(self.tasks)
        if filter == "daily":
            return [t for t in self.tasks if t.daily]
        if filter == "complete":
            return [t for t in self.tasks if t.is_complete]
        if filter == "incomplete":
            return [t for t in self.tasks if not t.is_complete]
        if filter in DAYS:
            return [t for t in self.tasks if t.daily or t.day == filter]
        return list(self.tasks)

    def to_dict(self) -> dict:
        """Serialize the pet and all its tasks to a JSON-compatible dict."""
        return {
            "name": self.name,
            "species": self.species,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Deserialize a Pet (and its tasks) from a dict produced by to_dict()."""
        pet = cls(name=data["name"], species=data["species"])
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []
        self.availability: dict[str, list[bool]] = {
            day: [True] * 26 for day in DAYS
        }

    def __repr__(self) -> str:
        """Return a summary of the owner's pet count and total weekly availability in hours."""
        return f"{self.name} has {len(self.pets)} pet(s) and is available for {sum(sum(day) for day in self.availability.values())/2} hour(s) per week."

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's roster."""
        self.pets.remove(pet)

    def update_availability(self, new_availability: dict[str, list[bool]]) -> None:
        """Replace the owner's weekly availability grid with a new one."""
        self.availability = new_availability

    def to_dict(self) -> dict:
        """Serialize the owner, their pets, and availability to a JSON-compatible dict."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
            "availability": self.availability,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Deserialize an Owner (with pets and availability) from a dict produced by to_dict()."""
        owner = cls(name=data["name"])
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        owner.availability = data.get("availability", {day: [True] * 26 for day in DAYS})
        return owner


class Scheduler:
    def __init__(self, id: int, owner: Owner) -> None:
        self.id = id
        self.owner = owner
        self.weekly_plan: dict[str, list[Task]] = {day: [] for day in DAYS}
        self.plan_explanation: list[str] = []

    def get_tasks(self, pet: Pet | None = None) -> list[Task]:
        """Return all unique scheduled tasks, optionally filtered to a single pet."""
        seen = set()
        result = []
        for day_tasks in self.weekly_plan.values():
            for task in day_tasks:
                if id(task) not in seen:
                    if pet is None or task.pet_name == pet.name:
                        seen.add(id(task))
                        result.append(task)
        return result

    def get_sorted_tasks(
        self, sort_type: str = "time", sort_order: str = "ascending"
    ) -> list[Task]:
        """Return all scheduled tasks sorted by 'time' or 'priority' in ascending or descending order."""
        tasks = self.get_tasks()
        reverse = sort_order == "descending"
        if sort_type == "time":
            tasks.sort(key=lambda t: t.start_time, reverse=reverse)
        elif sort_type == "priority":
            tasks.sort(key=lambda t: (t.priority.value * 2 + int(t.preference)), reverse=reverse)
        return tasks

    def generate_schedule(self) -> Generator:
        # Yields {"conflict": True, "task1": Task, "task2": Task} when a
        # high-priority tie requires user input. Caller resolves by sending
        # back the chosen Task via generator.send(chosen_task).
        # Final yield: {"conflict": False, "final_schedule": dict[str, list[Task]]}
        self.weekly_plan = {day: [] for day in DAYS}
        self.plan_explanation = []

        all_tasks: list[Task] = []
        for pet in self.owner.pets:
            all_tasks.extend(pet.tasks)

        # Sort descending: HIGH+pref > HIGH > MEDIUM+pref > MEDIUM > LOW+pref > LOW
        all_tasks.sort(key=lambda t: (t.priority.value * 2 + int(t.preference)), reverse=True)

        # Per-day occupancy grid: occupied[day][block] = Task or None
        occupied: dict[str, list[Task | None]] = {day: [None] * 26 for day in DAYS}

        for task in all_tasks:
            if task.daily:
                days_to_assign: list[str] = DAYS
            else:
                assert task.day is not None  # guaranteed by __init__: day required when daily=False
                days_to_assign = [task.day]

            for day in days_to_assign:
                # start_time is treated as 24h hour (e.g. 8=8am, 15=3pm)
                # map to half-hour block index: block 0 = 8:00am
                block_start = (task.start_time - 8) * 2
                block_end = block_start + task.total_blocks

                if block_start < 0 or block_end > 26:
                    self.plan_explanation.append(
                        f"{task.name} for {task.pet_name} was skipped on {day}: "
                        f"start time {task.start_time}:00 is outside the 8am–8pm schedule window."
                    )
                    continue

                avail = self.owner.availability[day]
                if not all(avail[block_start:block_end]):
                    self.plan_explanation.append(
                        f"{task.name} for {task.pet_name} was not scheduled on {day}: "
                        f"owner unavailable at {task.start_time}:00."
                    )
                    continue

                # Find any conflicting task in the target blocks.
                # Same-name tasks from different pets are co-scheduled (owner does them together).
                conflict_task: Task | None = None
                for b in range(block_start, block_end):
                    occupant = occupied[day][b]
                    if occupant is not None and not (
                        occupant.name.lower() == task.name.lower()
                        and occupant.pet_name != task.pet_name
                    ):
                        conflict_task = occupant
                        break

                if conflict_task is None:
                    for b in range(block_start, block_end):
                        occupied[day][b] = task
                    self.weekly_plan[day].append(task)
                else:
                    # Both tasks have the same composite priority (task was sorted after conflict_task,
                    # so conflict_task has >= priority — equal is the only conflict case possible here)
                    if task.priority == Priority.HIGH:
                        # Yield conflict for user resolution
                        chosen = yield {"conflict": True, "task1": conflict_task, "task2": task, "day": day}
                        if chosen is task:
                            # Replace conflict_task with task
                            for b in range(24):
                                if occupied[day][b] is conflict_task:
                                    occupied[day][b] = None
                            if conflict_task in self.weekly_plan[day]:
                                self.weekly_plan[day].remove(conflict_task)
                            for b in range(block_start, block_end):
                                occupied[day][b] = task
                            self.weekly_plan[day].append(task)
                            self.plan_explanation.append(
                                f"HIGH priority conflict on {day} at {task.start_time}:00: "
                                f"user chose {task.name} over {conflict_task.name}."
                            )
                        else:
                            self.plan_explanation.append(
                                f"HIGH priority conflict on {day} at {task.start_time}:00: "
                                f"user kept {conflict_task.name} over {task.name}."
                            )
                    else:
                        # MEDIUM or LOW tie — randomly pick; first-sorted task already holds the slot
                        keep = random.choice([conflict_task, task])
                        if keep is task:
                            for b in range(24):
                                if occupied[day][b] is conflict_task:
                                    occupied[day][b] = None
                            if conflict_task in self.weekly_plan[day]:
                                self.weekly_plan[day].remove(conflict_task)
                            for b in range(block_start, block_end):
                                occupied[day][b] = task
                            self.weekly_plan[day].append(task)
                        self.plan_explanation.append(
                            f"{task.priority.name} priority tie on {day} at {task.start_time}:00 "
                            f"between {task.name} and {conflict_task.name}: {keep.name} was randomly selected."
                        )

        yield {"conflict": False, "final_schedule": self.weekly_plan}

    def get_pet_happiness(self, pet: Pet) -> int:
        """Return the percentage of the pet's tasks that made it into the schedule (0 if no tasks)."""
        if not pet.tasks:
            return 0
        scheduled_ids = {id(t) for tasks in self.weekly_plan.values() for t in tasks}
        scheduled_count = sum(1 for t in pet.tasks if id(t) in scheduled_ids)
        return int((scheduled_count / len(pet.tasks)) * 100)

    def to_dict(self) -> dict:
        """Serialize the scheduler, owner, and weekly plan to a JSON-compatible dict."""
        return {
            "id": self.id,
            "owner": self.owner.to_dict(),
            "weekly_plan": {
                day: [task.to_dict() for task in tasks]
                for day, tasks in self.weekly_plan.items()
            },
            "plan_explanation": self.plan_explanation,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Scheduler:
        """Deserialize a Scheduler (with owner and weekly plan) from a dict produced by to_dict()."""
        owner = Owner.from_dict(data["owner"])
        scheduler = cls(id=data["id"], owner=owner)
        scheduler.plan_explanation = data.get("plan_explanation", [])
        for day, tasks in data.get("weekly_plan", {}).items():
            scheduler.weekly_plan[day] = [Task.from_dict(t) for t in tasks]
        return scheduler


class Storage:
    def __init__(self) -> None:
        self.schedulers: list[Scheduler] = []

    def _load_raw(self) -> list[dict]:
        """Read the JSON file and return the raw list of scheduler dicts, or [] if missing/corrupt."""
        if not os.path.exists(PATH):
            return []
        with open(PATH) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save(self, scheduler: Scheduler) -> None:
        """Upsert a scheduler into the JSON file, matching by id."""
        data = self._load_raw()
        for i, s in enumerate(data):
            if s["id"] == scheduler.id:
                data[i] = scheduler.to_dict()
                break
        else:
            data.append(scheduler.to_dict())
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        with open(PATH, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> list[Scheduler]:
        """Load all schedulers from the JSON file into memory and return them."""
        self.schedulers = [Scheduler.from_dict(s) for s in self._load_raw()]
        return self.schedulers
    
    def clear(self) -> None:
        """Wipe all schedulers from memory and delete the JSON file; for testing only."""
        # !!!!!Method to clear schedulers from storage, should only be used for testing.!!!!!
        self.schedulers = []
        if os.path.exists(PATH):
            os.remove(PATH)

if __name__ == "__main__":
    # Put CLI test code here.
    print("You are running pawpal_system.py directly, this is a test of class features.")
    kevin = Owner("Kevin") # Owner with open availability
    new_schedule = Scheduler(1, kevin) # add a scheduler for Kevin
    tigrex = Pet("Tigrex", "cat") # add a pet for Kevin
    kevin.add_pet(tigrex) # link Tigrex to Kevin

    fido = Pet("Fido", "dog") # add a second pet for Kevin
    kevin.add_pet(fido) # link Fido to Kevin

    tigrex.add_task(Task("Feed", "Tigrex", 8, 1, Priority.HIGH, True, True)) # add morning feed
    tigrex.add_task(Task("Feed", "Tigrex", 15, 1, Priority.HIGH, True, True)) # add afternoon feed
    tigrex.add_task(Task("Feed", "Tigrex", 19, 1, Priority.HIGH, True, True)) # add evening feed
    tigrex.add_task(Task("Vet visit", "Tigrex", 10, 2, Priority.HIGH, False, False, "monday")) # add vet visit
    tigrex.add_task(Task("Training", "Tigrex", 10, 1, Priority.HIGH, False, False, "monday")) # add training with obvious conflict with vet visit

    gen = new_schedule.generate_schedule()
    result = next(gen)
    while result['conflict']:
        print(f'Conflict on {result["day"]}: 1: {result["task1"].name} vs 2: {result["task2"].name}')
        print('Choose which task to keep (1 or 2): ', end='')
        choice = input()
        if choice == '1':
            result = gen.send(result['task1'])
        elif choice == '2':
            result = gen.send(result['task2'])

    print('Schedule generated.')
    print('Monday:', [t.name for t in new_schedule.weekly_plan['monday']])
    print('Tuesday:', [t.name for t in new_schedule.weekly_plan['tuesday']])
    print('Tigrex happiness:', new_schedule.get_pet_happiness(tigrex), '%')
    print('Fido happiness:', new_schedule.get_pet_happiness(fido), '%')
    print('Explanations:', new_schedule.plan_explanation)

    print(new_schedule.weekly_plan)