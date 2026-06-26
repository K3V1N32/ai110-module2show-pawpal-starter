from pawpal_system import Task, Pet, Priority


def test_toggle_complete_changes_status():
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True)
    assert task.is_complete is False
    task.toggle_complete()
    assert task.is_complete is True
    task.toggle_complete()
    assert task.is_complete is False


def test_add_task_increases_pet_task_count():
    pet = Pet("Tigrex", "cat")
    assert len(pet.tasks) == 0
    task = Task("Feed", "Tigrex", 8, 1, Priority.HIGH, daily=True)
    pet.add_task(task)
    assert len(pet.tasks) == 1
