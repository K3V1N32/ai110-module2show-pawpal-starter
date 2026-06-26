from pawpal_system import Storage, Scheduler, Owner, Pet, Task, Priority, DAYS

if __name__ == "__main__":
    print("Welcome to the PawPal+ scheduling system!")

    main_storage = Storage()

    main_storage.clear()  # Clear existing data for a fresh start for testing.

    kevin = Owner("Kevin") # create an owner object
    print(f"Created owner: {kevin.name}")
    scheduler = Scheduler(1, kevin) # create a scheduler object, passing in our owner
    print("Scheduler created.")
    tigrex = Pet("Tigrex", "cat") # add a pet for Kevin
    print(f"Created pet: {tigrex.name}, a {tigrex.species}")
    bond = Pet("Bond", "dog") # add a second pet for Kevin
    print(f"Created pet: {bond.name}, a {bond.species}")
    kevin.add_pet(tigrex) # link Tigrex to Kevin
    print(f"Linked {tigrex.name} to {kevin.name}")
    kevin.add_pet(bond) # link Bond to Kevin
    print(f"Linked {bond.name} to {kevin.name}")
    tigrex.add_task(Task("Feed", "Tigrex", 8, 1, Priority.HIGH, True, True)) # add morning feed
    tigrex.add_task(Task("Feed", "Tigrex", 15, 1, Priority.HIGH, True, True)) # add afternoon feed
    tigrex.add_task(Task("Feed", "Tigrex", 19, 1, Priority.HIGH, True, True)) # add evening feed
    tigrex.add_task(Task("Vet visit", "Tigrex", 10, 2, Priority.HIGH, False, False, "monday")) # add vet visit
    tigrex.add_task(Task("Training", "Tigrex", 10, 1, Priority.HIGH, False, False, "monday")) # add training with obvious conflict with vet visit
    print(f"Added tasks for {tigrex.name}: {[task.name for task in tigrex.tasks]}")
    bond.add_task(Task("Feed", "Bond", 8, 1, Priority.HIGH, True, True)) # add morning feed
    bond.add_task(Task("Feed", "Bond", 15, 1, Priority.HIGH, True, True)) # add afternoon feed
    bond.add_task(Task("Feed", "Bond", 19, 1, Priority.HIGH, True, True)) # add evening feed
    bond.add_task(Task("Walk", "Bond", 9, 1, Priority.HIGH, True, True)) # add morning walk
    bond.add_task(Task("Walk", "Bond", 17, 1, Priority.HIGH, True, True)) # add evening walk
    bond.add_task(Task("Vet visit", "Bond", 11, 2, Priority.HIGH, False, False, "tuesday")) # add vet visit
    bond.add_task(Task("Training", "Bond", 11, 1, Priority.HIGH, False, False, "tuesday")) # add training with obvious conflict with vet visit
    print(f"Added tasks for {bond.name}: {[task.name for task in bond.tasks]}")

    print("Starting schedule generation...")
    schedule = scheduler.generate_schedule()  # start schedule generator
    result = next(schedule)
    while result['conflict']:
        print(f'Conflict on {result["day"]}: 1: {result["task1"].name} for {result["task1"].pet_name} vs 2: {result["task2"].name} for {result["task2"].pet_name}')
        print('Choose which task to keep (1 or 2): ', end='')
        choice = input()
        if choice == '1':
            result = schedule.send(result['task1'])
        elif choice == '2':
            result = schedule.send(result['task2'])
    print("Schedule generation complete.")
    today = "monday"
    tasks = sorted(scheduler.weekly_plan[today], key=lambda t: t.start_time)
    print(f"--Tasks for {today}--")
    for task in tasks:
        print(f"{task.name} for {task.pet_name} at {task.start_time}:00 for {task.total_blocks/2} hour(s)")
    print(f"Tigrex happiness: {scheduler.get_pet_happiness(tigrex)}%")
    print(f"Bond happiness: {scheduler.get_pet_happiness(bond)}%")
    print("Explanations for scheduling decisions:")
    for explanation in scheduler.plan_explanation:
        print(f"- {explanation}")
