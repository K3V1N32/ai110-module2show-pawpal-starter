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

# Human Brainstorming - Updated to reflect AI Planning!

## Classes
### **Scheduler**
Attributes:
- id: int
- owner: Owner
- weekly_plan: dict{day:list[Task]}
- plan_explanation: list<str>

Methods:
- get_tasks(pet: Pet = None): list<Task>
- get_sorted_tasks(sort_type: str = "time", sort_order: str = "ascending"): list<Task>
- generate_schedule(): python generator function yield {conflict: True, task1: Task, task2: Task} or {conflict: False, final_schedule: dict{day:list[Task]}}
- get_pet_happiness(pet: Pet): percentage: int
- to_dict(): dict
- from_dict(data: dict)$ Scheduler

### **Owner**
Attributes:
- name: str
- pets: list<Pet>
- availability: dict{day:list[bool]}

Methods:
- add_pet(Pet): None
- remove_pet(Pet): None
- update_availability(dict{day:list[bool]}): None
- to_dict(): dict
- from_dict(data: dict)$ Owner

### **Pet**
Attributes:
- name: str
- species: str
- tasks: list<Task>

Methods:
- add_task(Task): None
- remove_task(Task): None
- get_tasks(filter: str = None): list<Task>
- to_dict(): dict
- from_dict(data: dict)$ Pet

### **Task**
Attributes:
- name: str
- pet_name: str
- start_time: int
- total_blocks: int
- daily: bool
- day: str
- priority: Priority
- preference: bool
- is_complete: bool

Methods:
- toggle_complete(): None
- toggle_preference(): None
- toggle_daily(): None
- set_priority(priority: Priority): None
- set_day(day: str): None
- set_start_time(start: int): None
- set_total_blocks(total: int): None
- to_dict(): dict
- from_dict(data: dict)$ Task

### **Storage**
Attributes:
- schedulers: list<Scheduler>

Methods:
- save(scheduler: Scheduler): None
- load(): list<Scheduler>

Note: The assignment wants me to make a "daily plan" but I am specifically tackling this as a week schedule because I wanted to challenge myself, and a week plan seems more useful than just a single daily plan.

Note: I removed the per day schedule generation, and decided to stick with only weekly schedule generation to simplify the process, the user should still be able to view just a single day schedule if they wish, but the overall schedule generation will generate the entire week.

Note: The day attribute in Task will have a default value of None. If a task is initilized with daily == False, day will be required to be a day str and error if None is passed to prevent unexpected bugs.

Note: Priority will be an enum with LOW = 1, MEDIUM = 2, and HIGH = 3

Note: Pet happiness will be a percentage of tasks actually assigned to the current schedule, so it will reference the schedule to see x out of x tasks scheduled. Example: all of Luna's tasks are scheduled: 100% happiness, only half of Fido's tasks are scheduled: 50% happiness. In case of no tasks I will set pet happiness to 0% as that to me would mean neglect of daily needs.

Note: On plan_explanation, when generating a schedule, any time one task is chosen over another, we should write a reason, such as "Medication task was prioritized over Walking task due to Medication having High priority." as per the assignments requirements of explaining to the user why something could be missing from the schedule. plan_explanation can be empty and should be handled gracefully.

Updated main objects to have to_dict and from_dict functions included to handle json saving/loading smoothly.

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

The algorithm for assigning priority will be a greedy-sort algorithm that sorts tasks by priority/preference first, then greedily assign them to the start_time/weekly_plan if that block of time is fully available. When adding a task, there will be logic that prevents start_time + total_blocks from running past 24 total blocks, and there will be a suite of pytests to make sure that stays the same throughout refactors.

## Timeslot system

7 days [Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday]

Each day can be scheduled in blocks from 8am to 8pm, in 24 half hour blocks.

Min time for a task will be half an hour[1 block], maximum time for a task will be 4 hours [8 blocks].

Tasks will be given a start time and a total blocks attribute, to account for a time slot that the task will take up.

Only one task can be assigned per time block, no overlap may happen. Priority gets slot, use preference as tie-breaker.

If two tasks have the same priority and preference, for low and medium just pick the task for that timeblock at random, for high priority ask the user which should be scheduled. This should be available for CLI and Streamlit interface, we will use a generator function to allow asking user and wait for the results.

If 2 tasks such as "feed" or "walk" are scheduled for 2 or more pets the scheduler will attempt to schedule both tasks at the same time, this way we could feed all of our cats and dogs at the same time or walk all your dogs at the same time as long as the task name matches.

Tasks can be daily recurring, or occur on only a single day for this demo.

Availability will start as fully open blocks dictionary such that True is the default state of open availability and False means that the block is not available. I believe bool works well here due to only having 2 states, either available, or not available. Default dict example:
Note: The blocks are increased to 26 to account for a task happening at 8pm that might take up 1 or 2 blocks.

```python
availability = {
    sunday: [True] * 26,
    monday: [True] * 26,
    tuesday: [True] * 26,
    wednesday: [True] * 26,
    thursday: [True] * 26,
    friday: [True] * 26,
    saturday: [True] * 26
}
```
## JSON storage

All of the data should be stored in a JSON file for this offline demo to keep it persistent, this project can take in and generate a lot of data, and we wouldn't want a browser refresh to erase the progress made on schedule generation for a user. The storage should happend from scheduler down, so pack tasks into pets, pets into owner, and owner into scheduler, and we will load all schedulers into memory when the app/CLI starts, and handle no schedulers loaded as a new user state. Saving will be manual save button/CLI input and an autosave after generating a schedule. load() will load all schedulers into memory at the start of the app, so loading will only happen once and will be stored in the main app as loaded_schedulers: List<Scheduler> where all our scheduler Objects will be stored in memory while using the app.

## Streamlit ideas

For streamlit implementation, I want a new user to load into a page that sells the app a little bit and just has a name input, on name input that is where the first Scheduler and Owner are established. The name page phases out, with a "Welcome [name]" for a few seconds, and then the next page is loaded in: the availability input. I imagine the availability input to look like a week-calendar with the half hour 8am-8pm timeblocks outlined and clickable and it should be clear whether the time is available, or unavailable. The app should have tabs on the top that allow a user to go back to the other options and change them at-will, the data should save to app memory upon edit, and only save to file when the user changes the tab or moves to the next input portion. After availability, the app will load a page for pets, there will be a name and species input, and a button to add a task, the button for the task will bring up a task input form window to add task information, it should be clearly explained how priority determines order first, and preference is a tie-breaker. The user can enter as many tasks as they like for a pet, and I imagine the pet tab/page to contain a new pet/new task buttons and a dropdown or tabs to select which pet and clearly label what pet they are adding tasks for as they add tasks. Finally once at least a single pet and task are added, a nicely formatted button that stands out should appear to allow generation of the schedule, and upon clicking the button, the data will save to file, and a loading page should appear letting the user now that the schedule is generating. If confilcts arise, a window in the app will pop up with the title, "⚠️ There is a priority conflict, please choose which task you would like to schedule for [time] on [day]:" and it should show task1 on the left, and task2 on the right, they should be clickable and a button underneath says "Submit". After conflict resolution a new tab will become available for "Weekly Plan" that will show a similar week-calendar from the avaialbility, with color coded(Simple emote to show priority[red=high, yellow=medium, green=low]) pet tasks scheduled on the calendar and easy to read. The tasks should be clickable to mark or unmark them as complete, and the current day of the week should have an indicator that shows it is the current day, no actual dates will be used in the demo, just day names for the 7 days of the week.

Calendar grid will be implemented as st.data_editor so that we don't have to import streamlit-calendar.

If data already exists for a scheduler then the streamlit app will load a page for the already completed data or start back where the user left off, for instance the availability page if they did not submit the availability yet. The organization of the app once a schedule has been generated should be:

Tabs at the top for | Name | Availability | Pets | Schedule |

Save data to memory after every change, save to disk when user clicks "save" button and after generating a schedule.

CLI input for this app will be pretty clunky, but the assignment requires it for testing the logic of the main classes.

## Schedule Generation

Instead of trying to make a phase engine for conflicts, I propose a python generator function for generate_schedule(). This would preserve the state of the function between calls, and yield a conflict when needed. We will store the generator in st.session_state to keep it in-memory.

In CLI we can use input() to send, and in streamlit we can use st.dialog and rerun on user selection.

The generate_schedule will always yield a dict with {"conflict" : bool} to indicate whether it is a conflict yield, or a final_schedule yield.

Make sure to treat generate_schedule as a generator, it will not return useful information, it needs to yield it, catch with checking for result["conflict"]

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

<hr>
Made changes and new prompt:

"Could you review my changes and let me know if my plan makes more sense now and put your notes under the heading AI Planning part 2?"
<hr>

# AI Planning part 2

## Senior Review: Progress Check

Most of the Part 1 issues are addressed — good iteration. Here's what still needs attention before coding.

---

### What You Got Right

- `pet_name: str` on Task — good, closes the back-reference gap.
- `priority: Priority` on Task — correct, matches the Enum note below it.
- `Owner.availability` with the bool list example — much clearer, this is now implementable.
- `resolve_conflict` added to Scheduler — exactly right.
- `get_pet_happiness` now has a concrete definition (tasks scheduled / total tasks) — this is clean and testable.
- `Scheduler.id: int` added — needed for JSON keying.
- Greedy sort algorithm described — good enough to implement from.

---

### Still Needs Fixing

**Python doesn't support method overloading.** You listed `generate_schedule()` twice with different signatures. This won't work — the second definition silently overwrites the first. Use a single method with an optional parameter and return a union type, or better, split into two distinct method names as originally suggested:
```python
def generate_schedule() -> dict[str, list[Task]]:  # builds the full week
def get_schedule(day: str) -> list[Task]:            # queries one day
```
Pick one approach and remove the duplicate.

**Setter method signatures don't match the updated attribute types.** You changed `Task.day` to `str` and `Task.priority` to `Priority`, but the setters still read:
- `set_priority(priority: int)` — should be `set_priority(priority: Priority)`
- `set_day(day: int)` — should be `set_day(day: str)`

These are the methods tests will call. Wrong types here means wrong tests.

**`[True * 24]` is not valid Python.** The correct syntax is `[True] * 24`. A small typo in the plan, but copy-pasting this into code will give you `[24]` (integer multiplication), not a list of 24 booleans.

---

### New Issues to Resolve Before Coding

**The `generate_schedule` async/await problem is architectural.** You wrote that it should "await an answer from CLI/streamlit." Making `generate_schedule` an `async` function means every caller must also be async, which pulls the event loop requirement all the way up through the app. Don't do this.

The right pattern is **dependency injection** — pass a conflict resolver as a parameter:
```python
def generate_schedule(conflict_resolver=None) -> dict[str, list[Task]]:
```
For CLI: `conflict_resolver = lambda t1, t2: input("Choose 1 or 2")`
For Streamlit: `conflict_resolver = lambda t1, t2: st.selectbox(...)`

This keeps `generate_schedule` synchronous and testable, and the UI layer decides how to ask the user. This also means `resolve_conflict` should accept an optional resolver function rather than hardcoding `input()`.

**`Storage` is still prose, not a class.** You described the behavior well, but there's no class definition. Add it to your class list with at minimum:
- `save(scheduler: Scheduler) -> None`
- `load() -> list[Scheduler]`

This matters because `Storage` touches every other class during serialization — its interface needs to be defined before you implement the others, not after.

**`Task.day` and `Task.daily` interact in an undefined way.** If `daily=True`, the task appears every day — so what is `day` set to? `None`? An empty string? A sentinel like `"all"`? You need a defined contract here, otherwise `generate_schedule` has to special-case it with no spec to follow. Recommendation: when `daily=True`, `day` is ignored and should be set to `None`. Document this explicitly.

**`get_pet_happiness` edge case: division by zero.** If a pet has no tasks, `tasks_scheduled / total_tasks` blows up. Define the return value for a pet with no tasks (0% and 100% are both defensible — pick one and document it).

---

### Minor Flags

- `get_sorted_tasks` defaults to `sort_order="descending"` for time-sorted tasks. That means the last task of the day shows first. Ascending is almost certainly what you want for a daily schedule view — reconsider the default.
- The Streamlit section is an incomplete sentence. Finish it before starting implementation so there's a spec to build toward.

---

### Updated Checklist

| Item | Status |
|---|---|
| `pet_name: str` on Task | ✅ Done |
| `priority: Priority` Enum | ✅ Done |
| `Owner.availability` structure | ✅ Done |
| `resolve_conflict` method | ✅ Done |
| `get_pet_happiness` metric defined | ✅ Done |
| `generate_schedule` overload (Python doesn't allow) | ❌ Fix — split into two methods |
| Setter type signatures | ❌ Fix — `str`/`Priority` not `int` |
| `[True * 24]` syntax | ❌ Fix — should be `[True] * 24` |
| `generate_schedule` async problem | ❌ Fix — use dependency injection |
| `Storage` class defined formally | ❌ Add to class list |
| `daily=True` + `day` interaction | ❌ Define the contract |
| `get_pet_happiness` zero-task edge case | ❌ Define return value |

<hr>
Made more changes and came up with new UI ideas. New Prompt:

"Ok I've addressed the next set of concerns, please let me know how the plan looks now, and if my streamlit UI ideas can work within the limitations of streamlit. Please put notes under the heading AI Planning part 3."

# AI Planning part 3

## Senior Review: Design Is Solid, Streamlit Has One Hard Problem

The class design is now clean. Almost everything from Parts 1 and 2 is resolved. Here's the final state and the Streamlit reality check.

---

### What You Got Right

- `Storage` class properly defined with `save` and `load` — good.
- Setter signatures fixed (`Priority`, `str`) — good.
- `[True] * 24` syntax fixed — good.
- `conflict_resolver` injected into `generate_schedule` — exactly right.
- `daily=True` → `day=None` contract documented — good.
- `get_pet_happiness` zero-task returns 0% — defensible, documented — good.
- `sort_order` default changed to ascending — good.
- `plan_explanation: list[str]` on Scheduler — good explainability feature.

The backend design is ready to implement.

---

### One Remaining Backend Issue

**`Storage` has no serialization contract.** `save(scheduler)` writes to JSON and `load()` reads it back — but none of your domain classes have a `to_dict()` / `from_dict()` method. JSON can only serialize primitives. A `Scheduler` object with nested `Owner`, `Pet`, and `Task` objects will raise a `TypeError` the moment you call `json.dumps()` on it.

Before implementing `Storage`, decide: does each class own its own serialization, or does `Storage` handle it externally? The cleanest approach for a project this size is to add `to_dict()` and `from_dict()` as class methods on each domain object:

```python
class Task:
    def to_dict(self) -> dict: ...
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task": ...
```

`Storage.save` then calls `scheduler.to_dict()` and `Storage.load` calls `Scheduler.from_dict(data)`. Add these to your class definitions — they're not optional, they're required for JSON persistence to work.

Also: **the `plan_explanation` note is cut off** mid-sentence ("we should write a reason, such as... to"). Finish it before implementing so you know exactly when and what to append to that list.

---

### Streamlit: What Works, What Doesn't

Most of your UI ideas are feasible. One is not — and it's a load-bearing part of the flow.

---

**✅ Tab navigation (`st.tabs`)** — Works natively. `st.tabs(["Name", "Availability", "Pets", "Schedule"])` is straightforward.

**⚠️ Save on tab switch** — Streamlit has no tab-switch event. You cannot trigger a callback when the user clicks a different tab. The workaround: save to `st.session_state` on every widget `on_change`, and save to disk when the user clicks an explicit "Save" button or when schedule generation runs. Drop the "save on tab switch" idea — replace it with autosave to session state on every change, and disk-save only on generation + manual save.

**✅ Welcome animation / page transition** — Achievable with `st.session_state` flags and `st.rerun()`. Show the welcome screen, use `time.sleep(2)` then `st.rerun()` to advance. It won't be a smooth CSS transition, but it'll be a clean phase change. Good enough for a demo.

**⚠️ Availability calendar grid** — Streamlit has no native calendar widget. Your options:
1. `st.data_editor` with a 7×24 DataFrame — cleanest and most interactive, cells are clickable booleans
2. 168 `st.checkbox` widgets in a `st.columns(7)` layout — functional but visually dense
3. Third-party component like `streamlit-calendar` — requires an extra install

`st.data_editor` is the best fit here — it renders as a grid, supports boolean cells, and handles state automatically. Recommend this approach.

**✅ Task input form as a modal** — `@st.dialog` (stable since Streamlit 1.36) does exactly this. A decorated function becomes a popup. This is the right tool.

**❌ Conflict resolution popup mid-schedule-generation — this is the hard problem.** Your plan assumes `generate_schedule` can pause mid-execution, show a popup, wait for the user to click, then continue. This is not how Streamlit works.

Streamlit reruns the entire script from top to bottom on every user interaction. A Python function cannot pause mid-execution and wait for a UI event. The `conflict_resolver` lambda you pass in cannot open a `@st.dialog` and block — by the time the user clicks, the function call stack is gone.

The solution is a **two-phase state machine** using `st.session_state`:

- Phase 1: `generate_schedule` runs. When it hits a high-priority conflict, it stores the conflict in `st.session_state["pending_conflict"]` and returns a partial result.
- Phase 2: On the next rerun, the app detects `pending_conflict` in session state and opens the conflict dialog automatically.
- Phase 3: User submits their choice. Choice is stored in `st.session_state["conflict_resolution"]`. App reruns.
- Phase 4: `generate_schedule` is called again, but this time it reads the stored resolution from session state and continues past the conflict it previously hit.

This means `generate_schedule` needs to be resumable — it must accept a `resolutions: dict` parameter that maps a conflict key (e.g. `"monday_block_4"`) to the chosen task. When it encounters a conflict that already has a resolution stored, it uses it and moves on. When it encounters one that doesn't, it returns early after storing the conflict.

This is more engineering work than the plan implies — plan for it now rather than discovering it mid-implementation.

**✅ Color-coded schedule calendar** — Same `st.data_editor` or columns-based layout as availability. Priority border colors require `st.markdown` with `unsafe_allow_html=True` for custom CSS, or using colored emoji/icons as a simpler fallback. The emoji approach (🔴 high, 🟡 medium, 🟢 low) requires zero CSS and reads clearly.

**✅ Clickable tasks to toggle complete** — `st.checkbox` per task, bound to `task.toggle_complete()` on change. Straightforward.

**✅ Current day indicator** — Store `current_day` in `st.session_state` (or derive from `datetime.now().strftime('%A')`). Highlight that column/section with a different background using CSS or a simple `"← Today"` label.

---

### Summary

| Item | Status |
|---|---|
| All Part 2 checklist items | ✅ Done |
| `to_dict()` / `from_dict()` on domain classes | ❌ Add to class definitions |
| `plan_explanation` note finished | ❌ Complete the cut-off sentence |
| Streamlit tab nav | ✅ Feasible — `st.tabs` |
| Streamlit welcome transition | ✅ Feasible — `session_state` + `st.rerun()` |
| Streamlit availability calendar | ✅ Feasible — use `st.data_editor` |
| Streamlit task form modal | ✅ Feasible — `@st.dialog` |
| Streamlit save on tab switch | ⚠️ Not possible — replace with autosave to session state |
| Streamlit conflict resolution popup | ❌ Needs redesign — requires two-phase state machine, not a simple lambda |
| Streamlit color-coded schedule | ✅ Feasible — use emoji priority indicators or CSS |

<hr>

To claude:
"Alright I've resolved the current issues, please advise and let me know if we are ready to generate the mermaid UML diagram for our program! Please put notes under the header AI Planning part 4."

<hr>

# AI Planning part 4

## Senior Review: Almost There — Two Quick Fixes, Then UML

The design is in excellent shape. The generator approach is cleanly documented, the Streamlit plan is realistic, and all the major structural issues from Parts 1–3 are resolved. Two small things to fix before the diagram, then we're ready.

---

### Fix Before UML

**`Scheduler` is missing `to_dict()` and `from_dict()`.** Owner, Pet, and Task all have them, but Scheduler doesn't. `Storage.save(scheduler)` has to serialize a Scheduler — it can't do that without `scheduler.to_dict()`. Add these to the Scheduler class definition.

**`from_dict` needs to be marked as a classmethod.** You have `from_dict(data: dict): Owner` listed as a regular instance method on Owner, Pet, and Task. But `from_dict` constructs a new object from raw data — you can't call it on an instance that doesn't exist yet. In Python this must be a `@classmethod`:
```python
@classmethod
def from_dict(cls, data: dict) -> "Owner": ...
```
Note this in your class definitions so it's clear during implementation. The UML can represent this as `from_dict(data: dict)$ Owner` (the `$` is Mermaid's notation for static/class methods).

**Minor: `to_dict()` return type on Task says `Task` instead of `dict`.** It should be `to_dict(): dict`. Small typo but it'll confuse whoever implements it.

---

### Design Is Ready

Everything else is solid:

| Item | Status |
|---|---|
| All Part 3 checklist items | ✅ Done |
| Generator approach documented | ✅ Done |
| `plan_explanation` empty case handled | ✅ Done |
| Streamlit calendar via `st.data_editor` | ✅ Done |
| Save strategy (manual + post-generation) | ✅ Done |
| `Scheduler.to_dict()` / `from_dict()` | ❌ Add to class definition |
| `from_dict` marked as classmethod | ❌ Note in class definitions |
| `Task.to_dict()` return type (`Task` → `dict`) | ❌ Typo fix |

---

### What the UML Will Need to Capture

When you're ready to generate, the diagram should show:

- **5 classes**: `Scheduler`, `Owner`, `Pet`, `Task`, `Storage`
- **1 enum**: `Priority` (LOW, MEDIUM, HIGH)
- **Relationships**:
  - `Scheduler` → `Owner` (composition, one-to-one)
  - `Owner` → `Pet` (composition, one-to-many)
  - `Pet` → `Task` (composition, one-to-many)
  - `Scheduler` → `Task` (association via `weekly_plan`, one-to-many)
  - `Storage` → `Scheduler` (dependency, manages many)
  - `Task` → `Priority` (dependency, uses)
- `from_dict` methods marked as class-level (static) on each class
- `generate_schedule()` return type noted as `Generator` not a plain dict

Fix those three items above and say the word — UML is next.