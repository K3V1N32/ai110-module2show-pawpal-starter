# PawPal+
## ```Innovation in pet care management.```

## Assignment information

You've been asked to design PawPal+, a smart pet care management system that helps owners keep their furry friends happy and healthy. The app will track daily routines -- feedings, walks, medications, and appointments -- while using algorithmic logic to organize and prioritize tasks.

Your mission is to move from concept to a working application by designing a modular system architecture using Python’s object-oriented programming (OOP). You will act as the lead architect, using AI to brainstorm your design, scaffold your core logic, and implement sophisticated scheduling algorithms. You will practice a "CLI-first" workflow, ensuring your backend logic in pawpal_system.py is robust and verified through a demo script before connecting it to a modern Streamlit UI.

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

<hr>

# Human Brainstorming

## Classes
### **Scheduler**
Attributes:
- owner: Owner
- weekly_plan: dict{Day:list[Task]}

Methods:
- get_tasks(pet: Pet = None): list<Task>
- get_sorted_tasks(sort_type: str = "time", sort_order: str = "descending"): list<Task>
- generate_schedule(day: str = None): dict{Day:list[Task]}
- get_pet_happiness(pet: Pet): percentage: int

### **Owner**
Attributes:
- name: str
- pets: list<Pet>
- availability: dict

Methods:
- add_pet(Pet): None
- remove_pet(Pet): None

### **Pet**
Attributes:
- name: str
- species: str
- tasks: list<Task>

Methods:
- add_task(Task): None
- remove_task(Task): None
- get_tasks(filter: str = None): list<Task>

### **Task**
Attributes:
- name: str
- start_time: int
- total_blocks: int
- daily: bool
- day: int
- priority: int
- preference: bool
- is_complete: bool

Methods:
- toggle_complete(): None
- toggle_preference(): None
- toggle_daily(): None
- set_priority(priority: int): None
- set_day(day: int): None
- set_start_time(start: int): None
- set_total_blocks(total: int): None

## Priority system

Levels of priority -> low, medium, high. Level of Preferences: False/True

Priority is more important than preference, so that will be what determines order, while preference is what breaks ties.

Below is a priority state order to follow:

-Highest Priority Overall-

1. Priority: High, Preference: True
2. Priority: High, Preference: False
3. Priority: Medium, Preference: True
4. Priority: Medium, Preference: False
5. Priority: Low, Preference: True
6. Priority: Low, Preference: False

-Lowest Priority Overall-

## Timeslot system

7 days [Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday]

Each day can be scheduled in blocks from 8am to 8pm, in 24 half hour blocks.

Min time for a task will be half an hour[1 block], maximum time for a task will be 4 hours [8 blocks].

Tasks will be given a start time and a total blocks attribute, to account for a time slot that the task will take up.

Only one task can be assigned per time block, no overlap may happen. Priority gets slot, use preference as tie-breaker.

If two tasks have the same priority and preference, for low and medium just pick the task for that timeblock at random, for high priority ask the user which should be scheduled.

Tasks can be daily recurring, or occur on only a single day for this demo.

## JSON storage

All of the data should be stored in a JSON file for this offline demo to keep it persistent, this project can take in and generate a lot of data, and we wouldn't want a browser refresh to erase the progress made on schedule generation for a user.

<hr>
The prompt to the AI to help with planning: 

"Alright Claude, I have this PawPal Project that I am working on, you will be my senior engineer on this project, and help guide me. Please read over the information in PawPal+ Plan.md and for now, under the AI Planning header please put your critique and guidance from a senior perspective. Only generate what I've told you to for now, I will ask for more after we go over the plans."
<hr>

# AI Planning

## Senior Review: Critique & Guidance

The overall architecture is solid — four clean domain classes with a clear separation of concerns. Here's where you'll run into trouble if you don't address these before writing code.

---

### Type Inconsistencies

**`Task.day` is typed as `int`, but your day system uses string names** (Sunday, Monday, etc.). Pick one and be consistent throughout. An `int` index (0–6) is fine, but `Scheduler.weekly_plan` and `generate_schedule(day: str)` need to match. Right now they don't.

**`priority` is typed as `int` on Task, but described as `"low/medium/high"` strings in the priority system.** This will cause bugs. Use a Python `Enum` — it gives you type safety, readable names, and natural sort order:
```python
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
```

---

### Missing or Underspecified Attributes

**`Owner.availability: dict` has no defined structure.** Before you write a single line of the scheduler, you need to know what this looks like. A likely structure: `{day_index: list[block_index]}` — i.e., which half-hour blocks the owner is free on each day. Without this, `generate_schedule` has nothing to constrain against.

**Tasks have no reference to their owning Pet.** `Pet.get_tasks()` works fine going downward, but `Scheduler.get_tasks(pet: Pet)` has to iterate all pets to filter — and nothing links a Task back to its Pet. Add either a `pet_name: str` attribute to Task, or a back-reference `pet: Pet`. You'll thank yourself when debugging the scheduler.

**`get_pet_happiness` has no defined logic or supporting data.** Happiness is not a stored attribute anywhere, and no Task attributes track history (e.g., completion streaks, missed tasks). Either define what factors drive this metric now, or cut it from v1. A placeholder that returns a hardcoded value will mislead you during testing.

---

### Schedule Generation Algorithm Is Undefined

You've described the *priority rules* but not the *algorithm*. These are different things. Before implementing, answer:

1. Do you sort all tasks by priority+preference first, then greedily assign them to their requested `start_time`?
2. What happens when a task's `start_time + total_blocks` runs past block 24 (8pm)?
3. When you "ask the user" to resolve a high-priority tie — is that a CLI `input()` call, a Streamlit widget, or something else? This decision changes the method signature.

A greedy sort-then-assign is the right approach here, but sketch it out in pseudocode before implementing.

---

### Missing Method: Conflict Resolution

Your priority rules describe conflict resolution logic, but no method handles it. `Scheduler` needs something like `_resolve_conflict(task1: Task, task2: Task) -> Task`. Burying this logic inside `generate_schedule` will make it untestable and hard to reason about. Keep it separate.

---

### JSON Storage Has No Owner

You've decided on JSON persistence but haven't assigned responsibility for it. Will `Scheduler` serialize/deserialize itself? Will there be a separate `Storage` class? For a demo of this scope, a simple `Storage` class with `save(scheduler)` and `load() -> Scheduler` is the cleanest approach — it keeps persistence out of your domain classes entirely.

---

### `generate_schedule` Return Type Looks Wrong

Currently: `generate_schedule(day: str = None): dict{Day:list[Task]}`

If you pass a specific day, returning the entire weekly dict is wasteful and confusing. Consider:
- `generate_schedule() -> dict[str, list[Task]]` — regenerates the full week
- `get_schedule(day: str) -> list[Task]` — returns the plan for one day

Separate the "build" operation from the "query" operation.

---

### Summary of Action Items Before Coding

| Issue | Action |
|---|---|
| `Task.day` type mismatch | Standardize to `int` index (0–6) everywhere |
| `priority` as int vs string | Replace with `Priority` Enum |
| `Owner.availability` structure | Define as `dict[int, list[int]]` (day → blocks) |
| Task→Pet back-reference | Add `pet_name: str` to Task |
| `get_pet_happiness` logic | Define metric or cut from v1 |
| Schedule generation algorithm | Write pseudocode before implementing |
| Conflict resolution | Extract to its own `_resolve_conflict` method |
| JSON persistence | Assign to a dedicated `Storage` class |
| `generate_schedule` return type | Split into generate (full week) and get (single day) |