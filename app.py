import streamlit as st
import time as timer
from pawpal_system import Storage, Scheduler, Owner, Pet, Task, Priority, DAYS, BLOCKS_PER_DAY


def block_label(index: int) -> str:
    """Return a 12-hour clock label for the half-hour block starting at the given index (0 = 8:00 AM)."""
    total_minutes = index * 30
    hour24 = 8 + total_minutes // 60
    minute = total_minutes % 60
    period = "AM" if hour24 < 12 else "PM"
    hour12 = hour24 % 12 or 12
    return f"{hour12}:{minute:02d} {period}"


BLOCK_LABELS = [block_label(i) for i in range(BLOCKS_PER_DAY)]


def next_scheduler_id() -> int:
    """Return an id guaranteed to be unused by any current scheduler.

    Using len(schedulers) + 1 breaks once a scheduler has been deleted, since a later
    addition can reuse an id that's still on disk and clobber the wrong saved record.
    """
    existing_ids = [scheduler.id for scheduler in st.session_state.schedulers]
    return max(existing_ids, default=0) + 1


def save_progress() -> None:
    """Persist the currently selected scheduler to disk so no changes are ever lost."""
    if "selected_scheduler" in st.session_state:
        st.session_state.storage.save(st.session_state.selected_scheduler)


def render_owner_tab() -> None:
    st.title("Owner Profile")
    st.divider()
    schedules = [schedule for schedule in st.session_state.schedulers]
    owner_names = [schedule.owner.name for schedule in schedules]
    # "owner_selectbox" is a keyed widget, so passing `index=` here every render conflicts
    # with the Session State API writes the add/delete-owner dialogs make to this same key
    # (Streamlit raises "created with a default value but also had its value set via the
    # Session State API" if both happen). Only seed it when it's missing or has drifted out
    # of range; otherwise let the stored value drive the widget.
    if "owner_selectbox" not in st.session_state or st.session_state.owner_selectbox >= len(schedules):
        st.session_state.owner_selectbox = owner_names.index(st.session_state.selected_scheduler.owner.name)
    selected_index = st.selectbox("Select Owner", range(len(owner_names)), format_func=lambda i: owner_names[i], key="owner_selectbox")
    st.session_state.selected_scheduler = schedules[selected_index]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add New Owner"):
            render_add_owner_dialog()
    with col2:
        if st.button("Delete Owner"):
            render_delete_owner_dialog(st.session_state.selected_scheduler)

    owner = st.session_state.selected_scheduler.owner
    st.write("You can update your name below:")
    # "update_owner_name" is a keyed widget, so Streamlit ignores `value=` after the first
    # render and keeps whatever was last typed. Re-seed it whenever the selected owner
    # actually changes so it doesn't keep showing the previous owner's name.
    if st.session_state.get("update_owner_name_for") != st.session_state.selected_scheduler.id:
        st.session_state.update_owner_name = owner.name
        st.session_state.update_owner_name_for = st.session_state.selected_scheduler.id
    new_name = st.text_input("Update Owner Name", key="update_owner_name")
    if st.button("Update Name"):
        if str(new_name).strip() == "":
            st.warning("Please enter a valid name.")
        elif any(scheduler.owner.name.lower() == new_name.strip().lower() for scheduler in st.session_state.schedulers if scheduler != st.session_state.selected_scheduler):
            st.warning(f"An owner named '{new_name}' already exists. Please choose a different name.")
        else:
            owner.name = new_name
            save_progress()
            st.success(f"Owner name updated to '{new_name}'.")


def render_availability_tab(advance_on_save: bool) -> None:
    st.title("Set Availability")
    st.divider()
    owner = st.session_state.selected_scheduler.owner
    st.write("Selected Owner: ", owner.name)
    st.write("Click a cell to mark a half-hour block as available (checked) or unavailable (unchecked).")
    

    grid_data = {"Time": BLOCK_LABELS}
    for day in DAYS:
        grid_data[day.capitalize()] = list(owner.availability[day])

    column_config = {"Time": st.column_config.TextColumn("Time", disabled=True)}
    for day in DAYS:
        column_config[day.capitalize()] = st.column_config.CheckboxColumn(day.capitalize())

    edited = st.data_editor(
        grid_data,
        key="availability_editor",
        column_config=column_config,
        hide_index=True,
        width="stretch",
    )

    if st.button("Save Availability"):
        for day in DAYS:
            owner.availability[day] = list(edited[day.capitalize()])
        if advance_on_save:
            st.session_state.progress = 2
        save_progress()
        st.success("Availability saved successfully!")
        st.rerun()

START_TIME_LABELS = BLOCK_LABELS[:25]  # 8:00 AM through 8:00 PM
PRIORITY_LABELS = ["Low", "Medium", "High"]


@st.dialog("Add a Pet")
def render_add_pet_dialog() -> None:
    owner = st.session_state.selected_scheduler.owner
    pet_name = st.text_input("Pet Name", key="new_pet_name")
    pet_species = st.text_input("Species", key="new_pet_species")
    if st.button("Add Pet", key="add_pet_button"):
        if pet_name.strip() == "":
            st.warning("Please enter a valid pet name.")
        elif pet_species.strip() == "":
            st.warning("Please enter a valid species.")
        elif any(pet.name.lower() == pet_name.strip().lower() for pet in owner.pets):
            st.warning(f"A pet named '{pet_name}' already exists. Please choose a different name.")
        else:
            owner.add_pet(Pet(pet_name.strip(), pet_species.strip()))
            save_progress()
            st.success(f"Pet '{pet_name}' added successfully!")
            st.rerun()


@st.dialog("Add a Task")
def render_add_task_dialog(pet: Pet) -> None:
    st.write(f"Add a task for {pet.name}")
    task_name = st.text_input("Task Name", key="new_task_name")
    daily = st.checkbox("Daily", value=True, key="new_task_daily")
    day = None
    if not daily:
        day = st.selectbox("Day", [d.capitalize() for d in DAYS], key="new_task_day")
    start_label = st.selectbox("Start Time", START_TIME_LABELS, key="new_task_start")
    duration_minutes = st.slider("Duration (minutes)", min_value=30, max_value=240, step=30, value=30, key="new_task_duration")
    priority_label = st.selectbox("Priority", PRIORITY_LABELS, key="new_task_priority")
    preference = st.checkbox("Preference", value=False, key="new_task_preference")

    if st.button("Add Task", key="add_task_button"):
        if task_name.strip() == "":
            st.warning("Please enter a valid task name.")
        else:
            start_time = 8 + START_TIME_LABELS.index(start_label) * 0.5
            new_task = Task(
                name=task_name.strip(),
                pet_name=pet.name,
                start_time=start_time,
                total_blocks=duration_minutes // 30,
                priority=Priority[priority_label.upper()],
                preference=preference,
                daily=daily,
                day=day.lower() if day else None,
            )
            pet.add_task(new_task)
            save_progress()
            st.success(f"Task '{task_name}' added for {pet.name}.")
            st.rerun()

@st.dialog("Delete Pet")
def render_delete_pet_dialog(pet: Pet) -> None:
    st.write(f"Are you sure you want to delete {pet.name}? This will also delete all tasks associated with this pet.")
    if st.button("Confirm Deletion", key=f"confirm_delete_pet_{pet.name}"):
        st.session_state.selected_scheduler.remove_pet(pet)
        # "selected_pet_name" is a keyed selectbox; if it was pointing at the pet we just
        # deleted, drop it so the widget re-initializes against the remaining pet list
        # instead of holding a stale name that's no longer a valid option.
        if st.session_state.get("selected_pet_name") == pet.name:
            st.session_state.pop("selected_pet_name", None)
        save_progress()
        st.success(f"Pet '{pet.name}' deleted.")
        st.rerun()

@st.dialog("Add new Owner")
def render_add_owner_dialog() -> None:
    st.write("Add a new owner profile")
    owner_name = st.text_input("Owner Name", key="new_owner_name")
    if st.button("Add Owner", key="add_owner_button"):
        if owner_name.strip() == "":
            st.warning("Please enter a valid name.")
        elif any(scheduler.owner.name.lower() == owner_name.strip().lower() for scheduler in st.session_state.schedulers):
            st.warning(f"An owner named '{owner_name}' already exists. Please choose a different name.")
        else:
            new_owner = Owner(owner_name.strip())
            new_scheduler = Scheduler(id=next_scheduler_id(), owner=new_owner)
            st.session_state.schedulers.append(new_scheduler)
            st.session_state.selected_scheduler = new_scheduler
            # The "Select Owner" selectbox on the Owner tab has key="owner_selectbox", so once
            # it's been rendered once, Streamlit ignores any `index=` we pass it on later reruns
            # and uses this stored value instead. Update it here too, or the selectbox will snap
            # selected_scheduler back to the old owner the moment it re-renders.
            st.session_state.owner_selectbox = len(st.session_state.schedulers) - 1
            save_progress()
            st.success(f"Owner '{owner_name}' created successfully! You can now set your availability.")
            st.rerun()


@st.dialog("Delete Owner")
def render_delete_owner_dialog(scheduler: Scheduler) -> None:
    st.write(
        f"Are you sure you want to delete owner '{scheduler.owner.name}'? "
        "This will permanently delete all of their pets, tasks, and schedule data."
    )
    if st.button("Confirm Deletion", key=f"confirm_delete_owner_{scheduler.id}"):
        st.session_state.schedulers.remove(scheduler)
        st.session_state.storage.delete(scheduler.id)
        if st.session_state.selected_scheduler is scheduler:
            if st.session_state.schedulers:
                st.session_state.selected_scheduler = st.session_state.schedulers[0]
                # Reset the keyed widgets that reference the deleted owner/scheduler so
                # they don't hold a now out-of-range index or a value tied to a dead id.
                st.session_state.owner_selectbox = 0
                st.session_state.pop("update_owner_name_for", None)
            else:
                st.session_state.pop("selected_scheduler", None)
                st.session_state.progress = 0
        st.session_state.pop("selected_pet_name", None)
        st.success(f"Owner '{scheduler.owner.name}' deleted.")
        st.rerun()

def render_pets_tab() -> None:
    st.title("Pets")
    st.divider()
    owner = st.session_state.selected_scheduler.owner

    st.write("Here is a list of your pets:")
    for pet in owner.pets:
        col1, col2 = st.columns([5, 1])
        with col1:
            st.write(f"- {pet.name} has {len(pet.tasks)} task(s) scheduled.")
        with col2:
            if st.button(f"Delete {pet.name}", key=f"delete_pet_{pet.name}"):
                render_delete_pet_dialog(pet)
    
    if st.button("Add Pet", key="open_add_pet_dialog"):
        render_add_pet_dialog()

    if not owner.pets:
        st.info("Add a pet above to start scheduling tasks.")
        return

    st.divider()
    pet_names = [pet.name for pet in owner.pets]
    selected_pet_name = st.selectbox("Select a Pet", pet_names, key="selected_pet_name")
    selected_pet = next(pet for pet in owner.pets if pet.name == selected_pet_name)

    if st.button(f"Add Task for {selected_pet.name}", key="open_add_task_dialog"):
        render_add_task_dialog(selected_pet)

    st.divider()
    st.subheader(f"Tasks for {selected_pet.name}")
    tasks = sorted(selected_pet.get_tasks(), key=lambda t: t.start_time)
    if not tasks:
        st.info("No tasks added yet.")

    for task in tasks:
        task_key = task.id
        start_label_current = block_label(int((task.start_time - 8) * 2))
        schedule_desc = "Daily" if task.daily else (task.day or "").capitalize()
        with st.expander(f"{start_label_current} — {task.name} ({schedule_desc})"):
            edit_name = str(st.text_input("Task Name", value=task.name, key=f"edit_name_{task_key}"))
            edit_daily = st.checkbox("Daily", value=task.daily, key=f"edit_daily_{task_key}")
            edit_day = task.day
            if not edit_daily:
                day_options = [d.capitalize() for d in DAYS]
                current_day_label = (task.day or DAYS[0]).capitalize()
                edit_day_label = st.selectbox(
                    "Day", day_options, index=day_options.index(current_day_label), key=f"edit_day_{task_key}"
                )
                edit_day = edit_day_label.lower()
            edit_start_label = st.selectbox(
                "Start Time", START_TIME_LABELS, index=START_TIME_LABELS.index(start_label_current), key=f"edit_start_{task_key}"
            )
            edit_duration = st.slider(
                "Duration (minutes)", min_value=30, max_value=240, step=30, value=task.total_blocks * 30, key=f"edit_duration_{task_key}"
            )
            edit_priority_label = st.selectbox(
                "Priority", PRIORITY_LABELS, index=PRIORITY_LABELS.index(task.priority.name.capitalize()), key=f"edit_priority_{task_key}"
            )
            edit_preference = st.checkbox("Preference", value=task.preference, key=f"edit_preference_{task_key}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes", key=f"save_task_{task_key}"):
                    if edit_name.strip() == "":
                        st.warning("Please enter a valid task name.")
                    else:
                        task.name = edit_name.strip()
                        task.daily = edit_daily
                        task.day = edit_day
                        task.start_time = 8 + START_TIME_LABELS.index(edit_start_label) * 0.5
                        task.total_blocks = edit_duration // 30
                        task.priority = Priority[edit_priority_label.upper()]
                        task.preference = edit_preference
                        save_progress()
                        st.success(f"Task '{task.name}' updated.")
                        st.rerun()
            with col2:
                if st.button("Delete", key=f"delete_task_{task_key}"):
                    st.session_state.selected_scheduler.remove_task(selected_pet, task)
                    save_progress()
                    st.success(f"Task '{task.name}' deleted.")
                    st.rerun()


def start_schedule_generation() -> None:
    """Create a fresh schedule generator for the selected scheduler and run it to its first stop."""
    scheduler = st.session_state.selected_scheduler
    st.session_state.schedule_generator = scheduler.generate_schedule()
    advance_schedule_generation()


def advance_schedule_generation(chosen_task: Task | None = None) -> None:
    """Resume the in-flight schedule generator, optionally sending a conflict resolution, and rerun."""
    generator = st.session_state.schedule_generator
    try:
        if chosen_task is None:
            result = next(generator)
        else:
            result = generator.send(chosen_task)
    except StopIteration:
        result = {"conflict": False}

    if result["conflict"]:
        st.session_state.schedule_conflict = result
    else:
        st.session_state.pop("schedule_generator", None)
        st.session_state.pop("schedule_conflict", None)
        st.session_state.progress = 5
        st.success("Schedule generated successfully!")
    save_progress()
    st.rerun()


@st.dialog("Resolve Scheduling Conflict")
def render_conflict_dialog() -> None:
    conflict = st.session_state.schedule_conflict
    task1, task2, day = conflict["task1"], conflict["task2"], conflict["day"]
    st.write(
        f"Both of these HIGH priority tasks want the same time slot on **{day.capitalize()}**. "
        "Which one should keep the slot?"
    )
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**{task1.name}** ({task1.pet_name})")
        st.caption(f"{block_label(int((task1.start_time - 8) * 2))}, {task1.total_blocks * 30} min")
        if st.button(f"Keep {task1.name}", key="keep_conflict_task1"):
            advance_schedule_generation(task1)
    with col2:
        st.markdown(f"**{task2.name}** ({task2.pet_name})")
        st.caption(f"{block_label(int((task2.start_time - 8) * 2))}, {task2.total_blocks * 30} min")
        if st.button(f"Keep {task2.name}", key="keep_conflict_task2"):
            advance_schedule_generation(task2)


def render_schedule_tab() -> None:
    st.title("Weekly Schedule")
    scheduler = st.session_state.selected_scheduler
    st.write(f"Schedule for {scheduler.owner.name}")
    st.divider()
    
    if scheduler.owner.pets:
        if len(scheduler.owner.pets[0].tasks) == 0:
            st.info("Add tasks for your pets in the Pets tab to generate a schedule.")
            return
    else:
        st.info("Add pets in the Pets tab to generate a schedule.")
        return

    grid_data = {"Time": BLOCK_LABELS}
    for day in DAYS:
        column = [[] for _ in range(BLOCKS_PER_DAY)]
        for task in scheduler.weekly_plan[day]:
            block_start = int((task.start_time - 8) * 2)
            block_end = min(block_start + task.total_blocks, BLOCKS_PER_DAY)
            label = f"{task.name} ({task.pet_name})"
            for block in range(block_start, block_end):
                column[block].append(label)
        grid_data[day.capitalize()] = [", ".join(labels) for labels in column]

    column_config = {"Time": st.column_config.TextColumn("Time", disabled=True)}
    for day in DAYS:
        column_config[day.capitalize()] = st.column_config.TextColumn(day.capitalize(), disabled=True)

    st.dataframe(grid_data, column_config=column_config, hide_index=True, width="stretch")

    if scheduler.owner.pets:
        st.divider()
        st.subheader("Pet Happiness")
        happiness_cols = st.columns(len(scheduler.owner.pets))
        for col, pet in zip(happiness_cols, scheduler.owner.pets):
            with col:
                st.metric(pet.name, f"{scheduler.get_pet_happiness(pet)}%")

    st.divider()
    st.subheader("Scheduling Notes")
    st.write("Here's the reasoning behind how tasks were placed (or skipped) on the schedule above:")
    if scheduler.plan_explanation:
        for note in scheduler.plan_explanation:
            st.write(f"- {note}")
    else:
        st.write("All tasks were scheduled without any conflicts.")

    st.divider()
    if st.button("Regenerate Schedule"):
        start_schedule_generation()


if "storage" not in st.session_state:
    st.session_state.storage = Storage()  # create a storage component to manage schedulers

if "schedulers" not in st.session_state:
    st.session_state.schedulers = st.session_state.storage.load() # load existing schedulers from storage into session state

if "selected_scheduler" not in st.session_state:
    if len(st.session_state.schedulers) > 0:
        st.session_state.selected_scheduler = st.session_state.schedulers[0]  # default to the first scheduler if any exist

if "progress" not in st.session_state:
    #Steps: 
    #0 = no saved owners, introduce app and set first owner name
    #1 = set availability for the owner
    #2 = add pets for the owner
    #3 = owner has pets, but no tasks added
    #4 = owner has pets and tasks, but no schedule generated
    #5 = owner has pets and tasks, and schedule generated / owners were loaded from storage
    if len(st.session_state.schedulers) == 0:
        st.session_state.progress = 0  # track progress through the app's steps, start at 0
    else:
        st.session_state.progress = 5  # if schedulers were loaded from storage, skip to the final step

# session progress logic for steps 3 and 4
if len(st.session_state.schedulers) > 0: # Check for schedulers
    if st.session_state.progress == 2 or st.session_state.progress == 3: # Check that progress is 2 or 3
        if st.session_state.schedulers[0].owner.pets: # Check that the owner has pets
            if len(st.session_state.schedulers[0].owner.pets) > 0:
                st.session_state.progress = 3 # move to step 3 if the owner has pets
                if len(st.session_state.schedulers[0].owner.pets[0].tasks) > 0: # check that at least one task has been added for a pet, which is needed to start generating schedules
                    st.session_state.progress = 4 # move to step 4 if the owner has pets with tasks

# Begin page rendering
st.set_page_config(page_title="PawPal+", page_icon="🐾")

# Debug Sidebar
debug = False # Set to True to enable debug mode, False to disable - Adds a sidebar with debug information and buttons to save/clear schedulers from storage
if debug == True:
    st.sidebar.title("PawPal+ Debug Tool")
    st.sidebar.write("Step: ", st.session_state.progress)
    st.sidebar.write("Selected Scheduler: ", st.session_state.selected_scheduler.owner.name if "selected_scheduler" in st.session_state else "N/A")
    st.sidebar.write("Schedulers: ", st.session_state.schedulers)
    st.sidebar.write("Availability: ", st.session_state.selected_scheduler.owner.availability if "selected_scheduler" in st.session_state else "N/A")
    st.sidebar.button("Save current scheduler to file", on_click=lambda: st.session_state.storage.save(st.session_state.selected_scheduler))
    st.sidebar.button("Clear all schedulers from file", on_click=lambda: st.session_state.storage.clear())

# | tab name(step) |
# | Owner(0) | Availability(1) | Pets(2/3) [4 is where generate schedule button will show, user will click genereate schedule before the schedule tab shows] | Schedule(5) |

if st.session_state.progress == 0:
    tab1 = st.tabs(["PawPal+"])
    with tab1[0]:
        st.title("🐾 PawPal+")
        st.divider()
        st.write("Welcome to the PawPal+ scheduling system! This app helps pet owners manage their pets' daily tasks and schedules.")
        st.write("To get started, please enter your name below to create an owner profile.")
        owner_name = st.text_input("Owner Name", key="owner_name")
        if st.button("Create Owner"):
            if owner_name.strip() == "":
                st.warning("Please enter a valid name.")
            else:
                new_owner = Owner(owner_name)
                new_scheduler = Scheduler(id=next_scheduler_id(), owner=new_owner)
                st.session_state.schedulers.append(new_scheduler)
                st.session_state.selected_scheduler = new_scheduler
                st.session_state.progress = 1  # move to the next step
                save_progress()
                st.success(f"Owner '{owner_name}' created successfully! You can now set your availability.")
                st.rerun()

if st.session_state.progress == 1:
    tab1, tab2 = st.tabs(["Owner", "Availability"], default="Availability", key="progress_one_tabs")
    with tab1:
        render_owner_tab()
    with tab2:
        render_availability_tab(advance_on_save=True)

if st.session_state.progress == 2:
    tab1, tab2, tab3 = st.tabs(["Owner", "Availability", "Pets"], default="Pets", key="progress_two_tabs")
    st.session_state.progress_two_tabs = "Pets"
    with tab1:
        render_owner_tab()
    with tab2:
        render_availability_tab(advance_on_save=False)
    with tab3:
        render_pets_tab()

if st.session_state.progress == 3:
    tab1, tab2, tab3 = st.tabs(["Owner", "Availability", "Pets"], default="Pets", key="progress_three_tabs")
    with tab1:
        render_owner_tab()
    with tab2:
        render_availability_tab(advance_on_save=False)
    with tab3:
        render_pets_tab()

if st.session_state.progress == 4:
    tab1, tab2, tab3 = st.tabs(["Owner", "Availability", "Pets"], default="Pets", key="progress_four_tabs")
    with tab1:
        render_owner_tab()
    with tab2:
        render_availability_tab(advance_on_save=False)
    with tab3:
        render_pets_tab()

    st.sidebar.write("Owner, Pet, and Tasks have been added, click the button below to generate a schedule!")
    if st.sidebar.button("Generate Schedule"):
        start_schedule_generation()

if st.session_state.progress == 5:
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Owner", "Availability", "Pets", "Schedule"], default="Schedule", key="progress_five_tabs"
    )
    with tab1:
        render_owner_tab()
    with tab2:
        render_availability_tab(advance_on_save=False)
    with tab3:
        render_pets_tab()
    with tab4:
        render_schedule_tab()

if "schedule_conflict" in st.session_state:
    render_conflict_dialog()

#🐾 - Just here to keep the emoji available for copy/paste
