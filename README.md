# PawPal+ (Module 2 Project)

[Video Demo](#video)

## PawPal+ Features
### Owner Management

- Create and manage multiple owner profiles, each with their own schedule
- Switch between owners via a selector
- Rename an owner (with duplicate-name validation)
- Delete an owner (with confirmation dialog), cascading to remove all their pets, tasks, and schedule data

### Availability Setting

- Interactive weekly grid (half-hour blocks, 8 AM–8 PM) for marking when the owner is available
- Checkbox-per-cell editing via an editable data table, one column per day

### Pet Management

- Add pets (name + species) to an owner profile, with duplicate-name validation
- Delete a pet (with confirmation), which also removes all of that pet's tasks
- View a per-pet task count at a glance

### Task Management

- Add tasks per pet with: name, daily vs. specific-day recurrence, start time (30-min increments), duration (30–240 min), priority (Low/Medium/High), and a "preference" flag
- Edit any task's details inline via expandable panels
- Delete individual tasks

### Schedule Generation

- Auto-generate a weekly schedule from each pet's tasks and the owner's availability
- Interactive conflict resolution: when two HIGH priority tasks compete for the same slot, the user is prompted to choose which one keeps it
- Regenerate the schedule on demand

### Weekly Schedule View

- Read-only weekly grid showing which tasks occupy which half-hour blocks, per day
- Per-pet "happiness" score/metric based on how well their tasks were scheduled
- Human-readable scheduling notes explaining conflicts or skipped tasks

### Guided Onboarding

- Step-by-step progress flow (create owner → set availability → add pets → add tasks → generate schedule) that unlocks tabs as the user completes each step
- Returning users with saved data skip straight to the full schedule view

### Persistence

- All owners, pets, tasks, and schedules are automatically saved to disk after every change, so no progress is lost between sessions


## Scheduling Algorithm
**Approach**: Greedy, priority-ordered placement

PawPal+ builds each week's schedule with a single-pass greedy algorithm rather than an optimal solver — it processes tasks once, in priority order, placing each one if it fits.

### 1. Composite priority scoring
Every task gets a score: priority.value * 2 + preference (priority is Low=1/Medium=2/High=3, preference is a 0/1 boolean flag). This means a "preferred" Medium task (2×2+1=5) outranks a plain Medium task (2×2+0=4) but still loses to any High task (3×2=6 or 7). All tasks across all pets are flattened into one list and sorted descending by this score, so the algorithm always tries to place the most important tasks first.

### 2. Expansion and placement
- Daily tasks are expanded into 7 per-day placements (one for each day of the week); single-day tasks get just one.
- Each task's start time and duration are converted into a range of half-hour blocks (8:00 AM–9:00 PM, 26 blocks/day).
- A task is skipped outright if its blocks fall outside the schedule window or the owner marked themselves unavailable for any of those blocks.

### 3. Conflict detection
The algorithm tracks a per-day, per-block occupancy grid. When a task's blocks overlap something already placed, it checks whether the overlap is a real conflict:

- **Co-scheduling exception**: two tasks with the same name but different pets (e.g., "Feed" for two different cats) are never treated as conflicting — they're assumed to happen together.
- Everything else is a genuine conflict.

### 4. Conflict resolution (by composite score)
- Lower score loses automatically: the incoming task is dropped and skipped, no interaction needed.
- Tied score, Medium/Low: resolved silently via random.choice() — a coin flip between the two.
- Tied score, both High: the algorithm pauses and hands the decision to the user. This is implemented as a Python generator — generate_schedule() yields a {"conflict": True, task1, task2, day} payload, the UI shows a dialog, and the user's choice is sent back into the generator via .send() to resume scheduling exactly where it left off.

### 5. Explanations and metrics
- Every skip, drop, tie-break, and user decision is logged to plan_explanation as a human-readable note, shown in the Schedule tab so users understand why a task didn't make the cut.
- A pet happiness score is computed as (scheduled tasks / total tasks) × 100 — a simple satisfaction metric per pet based on how much of their requested routine actually fit.

### Design tradeoffs worth noting

- It's greedy, not globally optimal — a locked-in high-priority task can block a slightly-lower-priority one that might have produced a "better" overall schedule if placement order were different.
- Complexity is roughly O(n log n) for the sort plus O(n × blocks) for placement — fine at personal-schedule scale, not built for large-scale optimization.
- The generator/yield pattern lets multi-step user interaction (conflict resolution) live inside what's otherwise a synchronous scheduling pass, avoiding a more complex state machine in the UI layer.

### **[Here is the UML diagram for PawPal+ backend systems](/diagrams/uml.mmd)**

# Stretch Feature: Data Persistance

### Explain the persistance workflow and which files were modified:

## Workflow
Persistance works across two files with a clean split in ownership: pawpal_system.py owns storage mechanics and dict serialization, and app.py owns when to trigger saving and loading from json.

### Startup (load):

1. st.session_state.storage = Storage() is created once per session.
2. st.session_state.storage.load() reads data/schedulers.json via Storage._load_raw(), which tolerates a missing file ([]) or corrupt JSON ([]) rather than crashing.
3. Each raw dict is turned back into a live Scheduler object via Scheduler.from_dict(), which recursively rebuilds the nested Owner → Pet → Task objects.
4. If any schedulers were loaded, the app's progress state jumps straight to step 5 (full schedule view) instead of onboarding.

### Every mutation (save):

1. Any UI action that changes data (renaming an owner, adding a pet, editing a task, generating a schedule, etc.) calls save_progress().
2. That function calls st.session_state.storage.save(st.session_state.selected_scheduler) - only the currently selected scheduler is saved, not the whole list.
3. Storage.save() re-reads the whole JSON file, finds the entry whose "id" matches this scheduler and overwrites it in place (or appends if it's new), then rewrites the entire file. This upsert-by-id pattern is why every Scheduler needs a stable, collision-free id — hence next_scheduler_id() in app.py computing max(existing_ids) + 1 instead of len(schedulers) + 1, so a deleted-then-recreated scheduler can't collide with an id still on disk.

### Deletion:

- Storage.delete(scheduler_id) filters that id out of the raw JSON list and rewrites the file, called when an owner is deleted.

## Files involed
>pawpal_system.py
- Storage class is the persistence layer, it handles reads/writes on the JSON file at data/schedulers.json
- to_dict() / from_dict()
  - These methods are applied to every domain class, Task, Pet, Owner, and Scheduler. Each object knows how to serialize itself and it's children, and reconstruct itself from a plain dict. This is what lets Storage stay generic, it never touches individual fields, just calls scheduler.to_dict()

>app.py
- Loads from json on startup if it exists
- Calls save_progress() helper on nearly every state-changing action to achieve maximum persistence.

## Getting started

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```bash
Welcome to the PawPal+ scheduling system!
Created owner: Kevin
Scheduler created.
Created pet: Tigrex, a cat
Created pet: Bond, a dog
Linked Tigrex to Kevin
Linked Bond to Kevin
Added tasks for Tigrex: ['Feed', 'Feed', 'Feed', 'Vet visit', 'Training']
Added tasks for Bond: ['Feed', 'Feed', 'Feed', 'Walk', 'Walk', 'Vet visit', 'Training']
Starting schedule generation...
Conflict on monday: 1: Vet visit for Tigrex vs 2: Training for Tigrex
Choose which task to keep (1 or 2): 1
Conflict on tuesday: 1: Vet visit for Bond vs 2: Training for Bond
Choose which task to keep (1 or 2): 1
Schedule generation complete.
--Tasks for monday--
Feed for Tigrex at 8:00 for 0.5 hour(s)
Feed for Bond at 8:00 for 0.5 hour(s)
Walk for Bond at 9:00 for 0.5 hour(s)
Vet visit for Tigrex at 10:00 for 1.0 hour(s)
Feed for Tigrex at 15:00 for 0.5 hour(s)
Feed for Bond at 15:00 for 0.5 hour(s)
Walk for Bond at 17:00 for 0.5 hour(s)
Feed for Tigrex at 19:00 for 0.5 hour(s)
Feed for Bond at 19:00 for 0.5 hour(s)
Tigrex happiness: 80%
Bond happiness: 85%
Explanations for scheduling decisions:
- HIGH priority conflict on monday at 10:00: user kept Vet visit over Training.
- HIGH priority conflict on tuesday at 11:00: user kept Vet visit over Training.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with more verbose tests:
pytest -v
```

Sample test output:

```
========================================= test session starts =========================================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0 -- /Users/ks3276/projects/CodePath/AI110-PawPal+/ai110-module2show-pawpal-starter/.venv/bin/python3.13
cachedir: .pytest_cache
rootdir: /Users/ks3276/projects/CodePath/AI110-PawPal+/ai110-module2show-pawpal-starter
configfile: pytest.ini
plugins: anyio-4.14.0
collected 62 items                                                                                    

tests/test_pawpal.py::test_format_hour_whole_hour PASSED                                        [  1%]
tests/test_pawpal.py::test_format_hour_half_hour PASSED                                         [  3%]
tests/test_pawpal.py::test_task_requires_day_when_not_daily PASSED                              [  4%]
tests/test_pawpal.py::test_task_allows_missing_day_when_daily PASSED                            [  6%]
tests/test_pawpal.py::test_task_generates_unique_id_by_default PASSED                           [  8%]
tests/test_pawpal.py::test_task_accepts_explicit_id PASSED                                      [  9%]
tests/test_pawpal.py::test_toggle_complete_changes_status PASSED                                [ 11%]
tests/test_pawpal.py::test_toggle_preference_changes_status PASSED                              [ 12%]
tests/test_pawpal.py::test_toggle_daily_raises_without_day_set PASSED                           [ 14%]
tests/test_pawpal.py::test_toggle_daily_switches_to_specific_day_once_set PASSED                [ 16%]
tests/test_pawpal.py::test_toggle_daily_back_to_daily_is_always_allowed PASSED                  [ 17%]
tests/test_pawpal.py::test_set_priority PASSED                                                  [ 19%]
tests/test_pawpal.py::test_set_day_valid PASSED                                                 [ 20%]
tests/test_pawpal.py::test_set_day_invalid_raises PASSED                                        [ 22%]
tests/test_pawpal.py::test_set_start_time PASSED                                                [ 24%]
tests/test_pawpal.py::test_set_total_blocks_valid_bounds PASSED                                 [ 25%]
tests/test_pawpal.py::test_set_total_blocks_out_of_range_raises[0] PASSED                       [ 27%]
tests/test_pawpal.py::test_set_total_blocks_out_of_range_raises[9] PASSED                       [ 29%]
tests/test_pawpal.py::test_set_total_blocks_out_of_range_raises[-1] PASSED                      [ 30%]
tests/test_pawpal.py::test_task_to_dict_from_dict_roundtrip PASSED                              [ 32%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED                             [ 33%]
tests/test_pawpal.py::test_remove_task_from_pet PASSED                                          [ 35%]
tests/test_pawpal.py::test_pet_get_tasks_no_filter_returns_all PASSED                           [ 37%]
tests/test_pawpal.py::test_pet_get_tasks_daily_filter PASSED                                    [ 38%]
tests/test_pawpal.py::test_pet_get_tasks_complete_and_incomplete_filters PASSED                 [ 40%]
tests/test_pawpal.py::test_pet_get_tasks_day_filter_includes_daily_and_matching_day_only PASSED [ 41%]
tests/test_pawpal.py::test_pet_to_dict_from_dict_roundtrip PASSED                               [ 43%]
tests/test_pawpal.py::test_owner_default_availability_all_true_for_every_day PASSED             [ 45%]
tests/test_pawpal.py::test_owner_add_and_remove_pet PASSED                                      [ 46%]
tests/test_pawpal.py::test_owner_update_availability PASSED                                     [ 48%]
tests/test_pawpal.py::test_owner_to_dict_from_dict_roundtrip PASSED                             [ 50%]
tests/test_pawpal.py::test_scheduler_get_tasks_dedups_and_filters_by_pet PASSED                 [ 51%]
tests/test_pawpal.py::test_scheduler_get_sorted_tasks_by_time PASSED                            [ 53%]
tests/test_pawpal.py::test_scheduler_get_sorted_tasks_by_priority PASSED                        [ 54%]
tests/test_pawpal.py::test_generate_schedule_places_simple_task PASSED                          [ 56%]
tests/test_pawpal.py::test_generate_schedule_daily_task_assigned_to_every_day PASSED            [ 58%]
tests/test_pawpal.py::test_generate_schedule_specific_day_task_assigned_only_to_that_day PASSED [ 59%]
tests/test_pawpal.py::test_generate_schedule_skips_task_starting_before_window PASSED           [ 61%]
tests/test_pawpal.py::test_generate_schedule_skips_task_extending_past_window PASSED            [ 62%]
tests/test_pawpal.py::test_generate_schedule_skips_task_when_owner_unavailable PASSED           [ 64%]
tests/test_pawpal.py::test_generate_schedule_co_schedules_same_name_different_pets PASSED       [ 66%]
tests/test_pawpal.py::test_generate_schedule_higher_priority_wins_deterministically PASSED      [ 67%]
tests/test_pawpal.py::test_generate_schedule_equal_priority_tie_keeps_existing PASSED           [ 69%]
tests/test_pawpal.py::test_generate_schedule_equal_priority_tie_can_replace_existing PASSED     [ 70%]
tests/test_pawpal.py::test_generate_schedule_high_priority_conflict_yields_for_user_input PASSED [ 72%]
tests/test_pawpal.py::test_generate_schedule_high_priority_conflict_keep_existing_every_day PASSED [ 74%]
tests/test_pawpal.py::test_generate_schedule_high_priority_conflict_choose_incoming_every_day PASSED [ 75%]
tests/test_pawpal.py::test_generate_schedule_group_conflict_displaces_entire_co_scheduled_group PASSED [ 77%]
tests/test_pawpal.py::test_generate_schedule_group_conflict_can_keep_the_group_instead PASSED   [ 79%]
tests/test_pawpal.py::test_scheduler_remove_pet_purges_only_that_pets_tasks_from_schedule PASSED [ 80%]
tests/test_pawpal.py::test_scheduler_remove_task_purges_it_from_schedule PASSED                 [ 82%]
tests/test_pawpal.py::test_get_pet_happiness_zero_when_pet_has_no_tasks PASSED                  [ 83%]
tests/test_pawpal.py::test_get_pet_happiness_partial_when_some_tasks_unscheduled PASSED         [ 85%]
tests/test_pawpal.py::test_get_pet_happiness_survives_serialization_roundtrip PASSED            [ 87%]
tests/test_pawpal.py::test_scheduler_remove_pet_purges_schedule_after_reload PASSED             [ 88%]
tests/test_pawpal.py::test_scheduler_to_dict_from_dict_roundtrip PASSED                         [ 90%]
tests/test_pawpal.py::test_storage_save_creates_file_and_load_reconstructs PASSED               [ 91%]
tests/test_pawpal.py::test_storage_save_upserts_by_id_instead_of_duplicating PASSED             [ 93%]
tests/test_pawpal.py::test_storage_delete_removes_only_target_scheduler PASSED                  [ 95%]
tests/test_pawpal.py::test_storage_load_returns_empty_list_when_file_missing PASSED             [ 96%]
tests/test_pawpal.py::test_storage_clear_resets_state_and_removes_file PASSED                   [ 98%]
tests/test_pawpal.py::test_storage_load_raw_handles_corrupt_json_gracefully PASSED              [100%]

========================================= 62 passed in 0.06s ==========================================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | Scheduler.get_sorted_tasks(sort_type, sort_order) | Sorting algorithm that uses list.sort method to sort the scheduled tasks by start time, or priority. |
| Filtering | Pet.get_tasks(filter) | Filtering logic with several branching predicate rules (by day, daily-recurrence, completion status) built into the method to get_tasks from a pet, allowing for complex filtering of pet tasks |
| Conflict handling | Scheduler.generate_schedule() | generate_schedule uses a greedy, priority-based interval-scheduling algorithm to flatten and sort tasks by composite priority score, mapping tasks to discrete half-hour blocks, while maintining per-day occupancy grid to detect overlaps. There are also advanced conflic-resolution rules such as pause and yield for user input via CLI or streamlit for high priority conflicts, and random tie-break for lower priority tasks. |
| Recurring tasks | Task.daily(bool) | I've opted for daily vs scheduled on specific day to let users specify vet visits or training/dog park visits that may only happen on a single day. The default for a task is daily recurring. This is reflected in generate_schedule() and within __init__ of a task if daily is False then day is enforced, otherwise an error is raised. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Enter a name
2. Adjust Availability
3. Add a Pet
4. Add Tasks for that pet
5. Repeat adding pets/tasks as needed
6. Press the "Generate Schedule" Button on the sidebar, or "Regenerate Schedule" at the bottom of the "schedule" tab.
7. Answer any conflict resolution pop-ups
8. Browse the schedule, pet happiness, and conflict resolution reasoning.
9. Adjust Availability, Pets, Tasks at your discretion from the tabs, then goto the schedule tab and press the regenerate schedule button at the bottom once you've made updates.
10. The app saves your progress to file, so feel free to refresh, or come back at any time to review your schedule!

# Video

Below is a video demo of using PawPal+ in action!

https://github.com/user-attachments/assets/9ad682db-e558-487d-ae17-ebc69eb8fae7
