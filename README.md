# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

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

# Run with coverage:
pytest --cov
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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
<video src="media/video/PawPal+Demo.mov" width="50%"></video>
