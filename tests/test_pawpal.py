import json

import pytest

import pawpal_system
from pawpal_system import (
    BLOCKS_PER_DAY,
    DAYS,
    Owner,
    Pet,
    Priority,
    Scheduler,
    Storage,
    Task,
    format_hour,
)


@pytest.fixture(autouse=True)
def isolate_storage_path(tmp_path, monkeypatch):
    """Point Storage at a throwaway file so tests never touch the real data/schedulers.json."""
    monkeypatch.setattr(pawpal_system, "PATH", str(tmp_path / "schedulers.json"))


def run_schedule(scheduler, chooser=lambda conflict: conflict["task1"]):
    """Drive generate_schedule() to completion, resolving every HIGH-priority conflict with `chooser`."""
    gen = scheduler.generate_schedule()
    result = next(gen)
    while result["conflict"]:
        result = gen.send(chooser(result))
    return result


def make_task(name="Feed", pet_name="Tigrex", start_time=8, total_blocks=1,
              priority=Priority.HIGH, preference=False, daily=True, day=None):
    return Task(name, pet_name, start_time, total_blocks, priority, preference, daily, day)


# ---------------------------------------------------------------------------
# format_hour
# ---------------------------------------------------------------------------

def test_format_hour_whole_hour():
    assert format_hour(10) == "10:00"


def test_format_hour_half_hour():
    assert format_hour(10.5) == "10:30"


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

def test_task_requires_day_when_not_daily():
    with pytest.raises(ValueError):
        Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=False, day=None)


def test_task_allows_missing_day_when_daily():
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True)
    assert task.day is None


def test_task_generates_unique_id_by_default():
    task1 = make_task()
    task2 = make_task()
    assert task1.id != task2.id
    assert task1.id and task2.id


def test_task_accepts_explicit_id():
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True, id="custom-id")
    assert task.id == "custom-id"


def test_toggle_complete_changes_status():
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True)
    assert task.is_complete is False
    task.toggle_complete()
    assert task.is_complete is True
    task.toggle_complete()
    assert task.is_complete is False


def test_toggle_preference_changes_status():
    task = make_task(preference=False)
    task.toggle_preference()
    assert task.preference is True
    task.toggle_preference()
    assert task.preference is False


def test_toggle_daily_raises_without_day_set():
    task = make_task(daily=True)
    with pytest.raises(ValueError):
        task.toggle_daily()


def test_toggle_daily_switches_to_specific_day_once_set():
    task = make_task(daily=True)
    task.set_day("monday")
    task.toggle_daily()
    assert task.daily is False
    assert task.day == "monday"


def test_toggle_daily_back_to_daily_is_always_allowed():
    task = make_task(daily=False, day="monday")
    task.toggle_daily()
    assert task.daily is True


def test_set_priority():
    task = make_task(priority=Priority.LOW)
    task.set_priority(Priority.HIGH)
    assert task.priority == Priority.HIGH


def test_set_day_valid():
    task = make_task()
    task.set_day("friday")
    assert task.day == "friday"


def test_set_day_invalid_raises():
    task = make_task()
    with pytest.raises(ValueError):
        task.set_day("someday")


def test_set_start_time():
    task = make_task()
    task.set_start_time(14.5)
    assert task.start_time == 14.5


def test_set_total_blocks_valid_bounds():
    task = make_task()
    task.set_total_blocks(1)
    assert task.total_blocks == 1
    task.set_total_blocks(8)
    assert task.total_blocks == 8


@pytest.mark.parametrize("invalid_total", [0, 9, -1])
def test_set_total_blocks_out_of_range_raises(invalid_total):
    task = make_task()
    with pytest.raises(ValueError):
        task.set_total_blocks(invalid_total)


def test_task_to_dict_from_dict_roundtrip():
    original = make_task(
        name="Vet Visit", pet_name="Fido", start_time=10.5, total_blocks=2,
        priority=Priority.MEDIUM, preference=True, daily=False, day="monday",
    )
    original.toggle_complete()

    restored = Task.from_dict(original.to_dict())

    assert restored.id == original.id
    assert restored.name == original.name
    assert restored.pet_name == original.pet_name
    assert restored.start_time == original.start_time
    assert restored.total_blocks == original.total_blocks
    assert restored.priority == original.priority
    assert restored.preference == original.preference
    assert restored.daily == original.daily
    assert restored.day == original.day
    assert restored.is_complete == original.is_complete


# ---------------------------------------------------------------------------
# Pet
# ---------------------------------------------------------------------------

def test_add_task_increases_pet_task_count():
    pet = Pet("Tigrex", "cat")
    assert len(pet.tasks) == 0
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True)
    pet.add_task(task)
    assert len(pet.tasks) == 1


def test_remove_task_from_pet():
    pet = Pet("Tigrex", "cat")
    task = make_task(pet_name="Tigrex")
    pet.add_task(task)
    pet.remove_task(task)
    assert task not in pet.tasks


def test_pet_get_tasks_no_filter_returns_all():
    pet = Pet("Tigrex", "cat")
    pet.add_task(make_task(name="Feed"))
    pet.add_task(make_task(name="Walk"))
    assert len(pet.get_tasks()) == 2


def test_pet_get_tasks_daily_filter():
    pet = Pet("Tigrex", "cat")
    daily_task = make_task(daily=True)
    single_day_task = make_task(daily=False, day="monday")
    pet.add_task(daily_task)
    pet.add_task(single_day_task)
    assert pet.get_tasks("daily") == [daily_task]


def test_pet_get_tasks_complete_and_incomplete_filters():
    pet = Pet("Tigrex", "cat")
    complete_task = make_task(name="Feed")
    incomplete_task = make_task(name="Walk")
    complete_task.toggle_complete()
    pet.add_task(complete_task)
    pet.add_task(incomplete_task)
    assert pet.get_tasks("complete") == [complete_task]
    assert pet.get_tasks("incomplete") == [incomplete_task]


def test_pet_get_tasks_day_filter_includes_daily_and_matching_day_only():
    pet = Pet("Tigrex", "cat")
    daily_task = make_task(name="Feed", daily=True)
    monday_task = make_task(name="Vet", daily=False, day="monday")
    tuesday_task = make_task(name="Groom", daily=False, day="tuesday")
    for t in (daily_task, monday_task, tuesday_task):
        pet.add_task(t)
    monday_tasks = pet.get_tasks("monday")
    assert daily_task in monday_tasks
    assert monday_task in monday_tasks
    assert tuesday_task not in monday_tasks


def test_pet_to_dict_from_dict_roundtrip():
    pet = Pet("Tigrex", "cat")
    pet.add_task(make_task(name="Feed"))
    restored = Pet.from_dict(pet.to_dict())
    assert restored.name == pet.name
    assert restored.species == pet.species
    assert len(restored.tasks) == 1
    assert restored.tasks[0].name == "Feed"


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

def test_owner_default_availability_all_true_for_every_day():
    owner = Owner("Kevin")
    for day in DAYS:
        assert owner.availability[day] == [True] * BLOCKS_PER_DAY


def test_owner_add_and_remove_pet():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    assert pet in owner.pets
    owner.remove_pet(pet)
    assert pet not in owner.pets


def test_owner_update_availability():
    owner = Owner("Kevin")
    new_availability = {day: [False] * BLOCKS_PER_DAY for day in DAYS}
    owner.update_availability(new_availability)
    assert owner.availability == new_availability


def test_owner_to_dict_from_dict_roundtrip():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    owner.availability["monday"][0] = False

    restored = Owner.from_dict(owner.to_dict())

    assert restored.name == owner.name
    assert len(restored.pets) == 1
    assert restored.pets[0].name == "Tigrex"
    assert restored.availability["monday"][0] is False


# ---------------------------------------------------------------------------
# Scheduler: bookkeeping helpers
# ---------------------------------------------------------------------------

def test_scheduler_get_tasks_dedups_and_filters_by_pet():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    tigrex.add_task(make_task(name="Feed", pet_name="Tigrex", daily=True))
    fido.add_task(make_task(name="Walk", pet_name="Fido", start_time=9, daily=True))
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    all_tasks = scheduler.get_tasks()
    assert len(all_tasks) == 2  # deduped across all 7 days, not 14
    tigrex_tasks = scheduler.get_tasks(tigrex)
    assert len(tigrex_tasks) == 1
    assert tigrex_tasks[0].pet_name == "Tigrex"


def test_scheduler_get_sorted_tasks_by_time():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    late = make_task(name="Dinner", start_time=18, daily=True)
    early = make_task(name="Breakfast", start_time=8, daily=True)
    pet.add_task(late)
    pet.add_task(early)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    ascending = scheduler.get_sorted_tasks(sort_type="time", sort_order="ascending")
    assert [t.name for t in ascending] == ["Breakfast", "Dinner"]
    descending = scheduler.get_sorted_tasks(sort_type="time", sort_order="descending")
    assert [t.name for t in descending] == ["Dinner", "Breakfast"]


def test_scheduler_get_sorted_tasks_by_priority():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    low = make_task(name="Low", start_time=8, priority=Priority.LOW, daily=True)
    high = make_task(name="High", start_time=10, priority=Priority.HIGH, daily=True)
    pet.add_task(low)
    pet.add_task(high)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    descending = scheduler.get_sorted_tasks(sort_type="priority", sort_order="descending")
    assert [t.name for t in descending] == ["High", "Low"]


# ---------------------------------------------------------------------------
# Scheduler.generate_schedule: placement, skipping, availability
# ---------------------------------------------------------------------------

def test_generate_schedule_places_simple_task():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(daily=False, day="monday")
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.weekly_plan["monday"] == [task]


def test_generate_schedule_daily_task_assigned_to_every_day():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(daily=True)
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    for day in DAYS:
        assert scheduler.weekly_plan[day] == [task]


def test_generate_schedule_specific_day_task_assigned_only_to_that_day():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(daily=False, day="friday")
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    for day in DAYS:
        if day == "friday":
            assert scheduler.weekly_plan[day] == [task]
        else:
            assert scheduler.weekly_plan[day] == []


def test_generate_schedule_skips_task_starting_before_window():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(start_time=7, daily=False, day="monday")
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.weekly_plan["monday"] == []
    assert "outside the 8am" in scheduler.plan_explanation[0]


def test_generate_schedule_skips_task_extending_past_window():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(start_time=20.5, total_blocks=2, daily=False, day="monday")
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.weekly_plan["monday"] == []


def test_generate_schedule_skips_task_when_owner_unavailable():
    owner = Owner("Kevin")
    owner.availability["monday"][0] = False  # 8:00 AM block
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(start_time=8, total_blocks=1, daily=False, day="monday")
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.weekly_plan["monday"] == []
    assert "unavailable" in scheduler.plan_explanation[0]


def test_generate_schedule_co_schedules_same_name_different_pets():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed_tigrex = make_task(name="Feed", pet_name="Tigrex", daily=True)
    feed_fido = make_task(name="feed", pet_name="Fido", daily=True)  # case-insensitive match
    tigrex.add_task(feed_tigrex)
    fido.add_task(feed_fido)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    assert set(scheduler.weekly_plan["sunday"]) == {feed_tigrex, feed_fido}
    assert scheduler.plan_explanation == []


# ---------------------------------------------------------------------------
# Scheduler.generate_schedule: conflict resolution
# ---------------------------------------------------------------------------

def test_generate_schedule_higher_priority_wins_deterministically():
    """Regression: a strictly-lower-priority task must never win a coin flip against a
    higher-priority one; only genuine ties are randomized."""
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.HIGH, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.LOW, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    assert scheduler.weekly_plan["sunday"] == [feed]
    assert "already held by higher-priority" in scheduler.plan_explanation[0]


def test_generate_schedule_equal_priority_tie_keeps_existing(monkeypatch):
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.MEDIUM, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.MEDIUM, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)

    monkeypatch.setattr(pawpal_system.random, "choice", lambda seq: seq[0])
    run_schedule(scheduler)

    assert scheduler.weekly_plan["sunday"] == [feed]


def test_generate_schedule_equal_priority_tie_can_replace_existing(monkeypatch):
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.MEDIUM, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.MEDIUM, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)

    monkeypatch.setattr(pawpal_system.random, "choice", lambda seq: seq[1])
    run_schedule(scheduler)

    assert scheduler.weekly_plan["sunday"] == [vet]


def test_generate_schedule_high_priority_conflict_yields_for_user_input():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.HIGH, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.HIGH, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)

    gen = scheduler.generate_schedule()
    result = next(gen)
    assert result["conflict"] is True
    assert {result["task1"], result["task2"]} == {feed, vet}
    assert result["day"] == "sunday"


def test_generate_schedule_high_priority_conflict_keep_existing_every_day():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.HIGH, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.HIGH, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)

    run_schedule(scheduler, chooser=lambda c: c["task1"])

    for day in DAYS:
        assert scheduler.weekly_plan[day] == [feed]
    assert scheduler.get_tasks() == [feed]
    assert len(scheduler.plan_explanation) == len(DAYS)


def test_generate_schedule_high_priority_conflict_choose_incoming_every_day():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed = make_task(name="Feed", pet_name="Tigrex", start_time=12, priority=Priority.HIGH, daily=True)
    vet = make_task(name="Vet", pet_name="Fido", start_time=12, priority=Priority.HIGH, daily=True)
    tigrex.add_task(feed)
    fido.add_task(vet)
    scheduler = Scheduler(1, owner)

    run_schedule(scheduler, chooser=lambda c: c["task2"])

    for day in DAYS:
        assert scheduler.weekly_plan[day] == [vet]
    assert scheduler.get_tasks() == [vet]


def test_generate_schedule_group_conflict_displaces_entire_co_scheduled_group():
    """Regression: when a co-scheduled group (two same-named tasks from different pets)
    loses a conflict, BOTH must be removed -- not just whichever one the occupancy grid
    happened to still reference."""
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed_tigrex = make_task(name="Feed", pet_name="Tigrex", start_time=12,
                             priority=Priority.HIGH, preference=True, daily=True)
    feed_fido = make_task(name="Feed", pet_name="Fido", start_time=12,
                           priority=Priority.HIGH, preference=True, daily=True)
    vet_visit = make_task(name="Vet Visit", pet_name="Fido", start_time=12,
                           priority=Priority.HIGH, preference=True, daily=False, day="wednesday")
    tigrex.add_task(feed_tigrex)
    fido.add_task(feed_fido)
    fido.add_task(vet_visit)
    scheduler = Scheduler(1, owner)

    run_schedule(scheduler, chooser=lambda c: c["task2"] if c["task2"] is vet_visit else c["task1"])

    assert scheduler.weekly_plan["wednesday"] == [vet_visit]
    for day in DAYS:
        if day != "wednesday":
            assert set(scheduler.weekly_plan[day]) == {feed_tigrex, feed_fido}


def test_generate_schedule_group_conflict_can_keep_the_group_instead():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    feed_tigrex = make_task(name="Feed", pet_name="Tigrex", start_time=12,
                             priority=Priority.HIGH, preference=True, daily=True)
    feed_fido = make_task(name="Feed", pet_name="Fido", start_time=12,
                           priority=Priority.HIGH, preference=True, daily=True)
    vet_visit = make_task(name="Vet Visit", pet_name="Fido", start_time=12,
                           priority=Priority.HIGH, preference=True, daily=False, day="wednesday")
    tigrex.add_task(feed_tigrex)
    fido.add_task(feed_fido)
    fido.add_task(vet_visit)
    scheduler = Scheduler(1, owner)

    run_schedule(scheduler, chooser=lambda c: c["task1"])

    assert set(scheduler.weekly_plan["wednesday"]) == {feed_tigrex, feed_fido}
    assert vet_visit not in scheduler.get_tasks()


# ---------------------------------------------------------------------------
# Scheduler: deletion cleanup and happiness
# ---------------------------------------------------------------------------

def test_scheduler_remove_pet_purges_only_that_pets_tasks_from_schedule():
    owner = Owner("Kevin")
    tigrex = Pet("Tigrex", "cat")
    fido = Pet("Fido", "dog")
    owner.add_pet(tigrex)
    owner.add_pet(fido)
    tigrex_task = make_task(name="Feed", pet_name="Tigrex", daily=True)
    fido_task = make_task(name="Walk", pet_name="Fido", start_time=9, daily=True)
    tigrex.add_task(tigrex_task)
    fido.add_task(fido_task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    scheduler.remove_pet(tigrex)

    assert tigrex not in owner.pets
    for day in DAYS:
        assert tigrex_task not in scheduler.weekly_plan[day]
        assert fido_task in scheduler.weekly_plan[day]


def test_scheduler_remove_task_purges_it_from_schedule():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    task = make_task(daily=True)
    pet.add_task(task)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    scheduler.remove_task(pet, task)

    assert task not in pet.tasks
    for day in DAYS:
        assert task not in scheduler.weekly_plan[day]


def test_get_pet_happiness_zero_when_pet_has_no_tasks():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    scheduler = Scheduler(1, owner)
    assert scheduler.get_pet_happiness(pet) == 0


def test_get_pet_happiness_partial_when_some_tasks_unscheduled():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    scheduled = make_task(name="Feed", start_time=8, daily=True)
    unscheduled = make_task(name="TooLate", start_time=7, daily=True)  # outside window, always skipped
    pet.add_task(scheduled)
    pet.add_task(unscheduled)
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.get_pet_happiness(pet) == 50


def test_get_pet_happiness_survives_serialization_roundtrip():
    """Regression: happiness must not depend on Python object identity, since a saved and
    reloaded Scheduler deserializes pet.tasks and weekly_plan as two distinct sets of
    objects. Previously this always computed 0% after a reload."""
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    pet.add_task(make_task(daily=True))
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)
    assert scheduler.get_pet_happiness(pet) == 100

    reloaded = Scheduler.from_dict(scheduler.to_dict())
    reloaded_pet = reloaded.owner.pets[0]
    assert reloaded.get_pet_happiness(reloaded_pet) == 100


def test_scheduler_remove_pet_purges_schedule_after_reload():
    """Regression: the id()-based purge silently failed on a reloaded scheduler since the
    weekly_plan and pet.tasks copies are different objects after deserialization."""
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    pet.add_task(make_task(daily=True))
    scheduler = Scheduler(1, owner)
    run_schedule(scheduler)

    reloaded = Scheduler.from_dict(scheduler.to_dict())
    reloaded_pet = reloaded.owner.pets[0]

    reloaded.remove_pet(reloaded_pet)

    for day in DAYS:
        assert reloaded.weekly_plan[day] == []


def test_scheduler_to_dict_from_dict_roundtrip():
    owner = Owner("Kevin")
    pet = Pet("Tigrex", "cat")
    owner.add_pet(pet)
    pet.add_task(make_task(daily=True))
    scheduler = Scheduler(7, owner)
    run_schedule(scheduler)

    restored = Scheduler.from_dict(scheduler.to_dict())

    assert restored.id == 7
    assert restored.owner.name == "Kevin"
    assert restored.plan_explanation == scheduler.plan_explanation
    for day in DAYS:
        assert [t.name for t in restored.weekly_plan[day]] == [t.name for t in scheduler.weekly_plan[day]]


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

def make_scheduler(scheduler_id, owner_name="Kevin"):
    return Scheduler(scheduler_id, Owner(owner_name))


def test_storage_save_creates_file_and_load_reconstructs():
    storage = Storage()
    scheduler = make_scheduler(1, "Kevin")
    storage.save(scheduler)

    loaded = Storage().load()
    assert len(loaded) == 1
    assert loaded[0].id == 1
    assert loaded[0].owner.name == "Kevin"


def test_storage_save_upserts_by_id_instead_of_duplicating():
    storage = Storage()
    scheduler = make_scheduler(1, "Kevin")
    storage.save(scheduler)

    scheduler.owner.name = "Kevin Updated"
    storage.save(scheduler)

    loaded = Storage().load()
    assert len(loaded) == 1
    assert loaded[0].owner.name == "Kevin Updated"


def test_storage_delete_removes_only_target_scheduler():
    storage = Storage()
    storage.save(make_scheduler(1, "Kevin"))
    storage.save(make_scheduler(2, "Alice"))

    storage.delete(1)

    loaded = Storage().load()
    assert len(loaded) == 1
    assert loaded[0].owner.name == "Alice"


def test_storage_load_returns_empty_list_when_file_missing():
    assert Storage().load() == []


def test_storage_clear_resets_state_and_removes_file():
    storage = Storage()
    storage.save(make_scheduler(1, "Kevin"))
    storage.clear()

    assert storage.schedulers == []
    assert Storage().load() == []


def test_storage_load_raw_handles_corrupt_json_gracefully():
    with open(pawpal_system.PATH, "w") as f:
        f.write("not valid json {{{")

    assert Storage()._load_raw() == []
