import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------
st.subheader("Owner")

if "owner" not in st.session_state:
    with st.form("owner_form"):
        owner_name_input = st.text_input("Your name", key="owner_name")
        available_input = st.number_input("Available minutes per day", min_value=0, max_value=480, value=None, placeholder="e.g. 90", key="owner_minutes")
        submitted_owner = st.form_submit_button("Save")
    if submitted_owner:
        if not owner_name_input.strip():
            st.warning("Please enter your name.")
        elif not available_input:
            st.warning("Please enter your available minutes per day.")
        else:
            st.session_state.owner = Owner(
                name=owner_name_input.strip(),
                email="",
                available_minutes_per_day=int(available_input),
            )
            for key in ["owner_name", "owner_minutes"]:
                st.session_state.pop(key, None)
            st.rerun()
    st.stop()

owner: Owner = st.session_state.owner

if "pet_form_v" not in st.session_state:
    st.session_state.pet_form_v = 0
if "task_form_v" not in st.session_state:
    st.session_state.task_form_v = 0
if "editing_pet" not in st.session_state:
    st.session_state.editing_pet = None
if "editing_task" not in st.session_state:
    st.session_state.editing_task = None  # (pet_name, task_title)

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Name:** {owner.name}")
with col2:
    st.write(f"**Available time:** {owner.available_minutes_per_day} min/day")

# ---------------------------------------------------------------------------
# Section 2: Pets — add, edit, delete
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Pets")

with st.form(f"add_pet_form_{st.session_state.pet_form_v}"):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        new_pet_name = st.text_input("Pet name")
    with col_b:
        new_species = st.selectbox("Species", ["", "dog", "cat", "other"])
    with col_c:
        new_energy = st.selectbox("Energy level", ["", "low", "medium", "high"])
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    if not new_pet_name.strip() or not new_species or not new_energy:
        st.warning("Please fill in all pet fields.")
    elif new_pet_name.strip() in [p.name for p in owner.pets]:
        st.warning(f"A pet named '{new_pet_name.strip()}' already exists.")
    else:
        owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species, age_years=1, energy_level=new_energy))
        st.session_state.pet_form_v += 1
        st.rerun()

if owner.pets:
    st.write("**Your pets:**")
    for pet in owner.pets:
        col_name, col_info, col_edit, col_del = st.columns([2, 3, 1, 1])
        with col_name:
            st.write(f"**{pet.name}**")
        with col_info:
            st.write(f"{pet.species} · {pet.energy_level} energy")
        with col_edit:
            if st.button("Edit", key=f"edit_pet_{pet.name}"):
                st.session_state.editing_pet = pet.name
        with col_del:
            if st.button("Delete", key=f"del_pet_{pet.name}"):
                owner.pets = [p for p in owner.pets if p.name != pet.name]
                if st.session_state.editing_pet == pet.name:
                    st.session_state.editing_pet = None
                st.rerun()

    if st.session_state.editing_pet:
        pet = next((p for p in owner.pets if p.name == st.session_state.editing_pet), None)
        if pet:
            st.markdown(f"**Editing pet: {pet.name}**")
            with st.form(f"edit_pet_form_{pet.name}"):
                species_opts = ["dog", "cat", "other"]
                energy_opts = ["low", "medium", "high"]
                new_name_e = st.text_input("Name", value=pet.name)
                new_species_e = st.selectbox("Species", species_opts, index=species_opts.index(pet.species) if pet.species in species_opts else 0)
                new_energy_e = st.selectbox("Energy level", energy_opts, index=energy_opts.index(pet.energy_level) if pet.energy_level in energy_opts else 0)
                save_pet = st.form_submit_button("Save changes")
                cancel_pet = st.form_submit_button("Cancel")
            if save_pet:
                new_name_e = new_name_e.strip()
                if not new_name_e:
                    st.warning("Pet name cannot be empty.")
                elif new_name_e != pet.name and new_name_e in [p.name for p in owner.pets]:
                    st.warning(f"A pet named '{new_name_e}' already exists.")
                else:
                    # Update pet_name on all tasks belonging to this pet
                    for t in pet.tasks:
                        t.pet_name = new_name_e
                    pet.name = new_name_e
                    st.session_state.editing_pet = None
                    st.rerun()
            if cancel_pet:
                st.session_state.editing_pet = None
                st.rerun()
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3: Tasks — add, edit, delete
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Tasks")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form(f"add_task_form_{st.session_state.task_form_v}"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", [""] + pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title")
        with col2:
            duration = st.number_input("Duration (min)", min_value=0, max_value=240, value=None, placeholder="e.g. 20")
        with col3:
            priority = st.selectbox("Priority", ["", "low", "medium", "high"])
        col4, col5 = st.columns(2)
        with col4:
            is_recurring = st.checkbox("Recurring task")
        with col5:
            recurrence_interval = st.selectbox("Repeat", ["", "daily", "weekly"])
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        if not selected_pet_name or not task_title.strip() or not duration or not priority:
            st.warning("Please fill in all task fields.")
        elif is_recurring and not recurrence_interval:
            st.warning("Please select how often this task repeats.")
        else:
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            existing_titles = [t.title.lower() for t in target_pet.tasks]
            if task_title.strip().lower() in existing_titles:
                st.warning(f"'{task_title.strip()}' already exists for {selected_pet_name}. Duplicate tasks are not allowed.")
            else:
                target_pet.add_task(Task(
                    title=task_title.strip(),
                    category="general",
                    duration_minutes=int(duration),
                    priority=priority,
                    is_recurring=is_recurring,
                    recurrence_interval=recurrence_interval if is_recurring else None,
                ))
                st.session_state.task_form_v += 1
                st.rerun()

    # --- Filter ---
    st.markdown("**Filter tasks**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_pet = st.selectbox("By pet", ["All"] + [p.name for p in owner.pets], key="filter_pet")
    with col_f2:
        filter_status = st.selectbox("By status", ["All", "Pending", "Completed"], key="filter_status")

    pet_filter = None if filter_pet == "All" else filter_pet
    status_filter = None if filter_status == "All" else (filter_status == "Completed")
    filtered = owner.filter_tasks(pet_name=pet_filter, completed=status_filter)

    if filtered:
        st.write("**Tasks:**")
        for idx, task in enumerate(filtered):
            pet_obj = next((p for p in owner.pets if p.name == task.pet_name), None)
            col_t, col_info, col_done, col_edit, col_del = st.columns([2, 4, 2, 1, 1])
            with col_t:
                st.write(f"**{task.title}**")
            with col_info:
                recur = f" · repeats {task.recurrence_interval}" if task.is_recurring else ""
                st.write(f"{task.pet_name} · {task.duration_minutes} min · {task.priority}{recur}")
            with col_done:
                if task.completed:
                    st.success("Completed: Yes")
                else:
                    st.warning("Completed: No")
            with col_edit:
                if st.button("Edit", key=f"edit_task_{idx}"):
                    st.session_state.editing_task = (task.pet_name, task.title)
            with col_del:
                if st.button("Delete", key=f"del_task_{idx}"):
                    if pet_obj:
                        pet_obj.tasks = [t for t in pet_obj.tasks if t is not task]
                    st.rerun()

        if st.session_state.editing_task:
            e_pet_name, e_task_title = st.session_state.editing_task
            e_pet = next((p for p in owner.pets if p.name == e_pet_name), None)
            e_task = next((t for t in e_pet.tasks if t.title == e_task_title), None) if e_pet else None
            if e_task:
                st.markdown(f"**Editing task: {e_task.title} [{e_pet_name}]**")
                priority_opts = ["low", "medium", "high"]
                with st.form(f"edit_task_form_{e_pet_name}_{e_task_title}"):
                    new_title_e = st.text_input("Title", value=e_task.title)
                    new_dur_e = st.number_input("Duration (min)", min_value=1, max_value=240, value=e_task.duration_minutes)
                    new_pri_e = st.selectbox("Priority", priority_opts, index=priority_opts.index(e_task.priority) if e_task.priority in priority_opts else 0)
                    new_recur_e = st.checkbox("Recurring", value=e_task.is_recurring)
                    new_interval_e = st.selectbox("Repeat", ["", "daily", "weekly"], index=["", "daily", "weekly"].index(e_task.recurrence_interval or ""))
                    save_task = st.form_submit_button("Save changes")
                    cancel_task = st.form_submit_button("Cancel")
                if save_task:
                    e_task.title = new_title_e.strip()
                    e_task.duration_minutes = int(new_dur_e)
                    e_task.priority = new_pri_e
                    e_task.is_recurring = new_recur_e
                    e_task.recurrence_interval = new_interval_e if new_recur_e else None
                    st.session_state.editing_task = None
                    st.rerun()
                if cancel_task:
                    st.session_state.editing_task = None
                    st.rerun()
    else:
        st.info("No tasks match the current filter.")

# ---------------------------------------------------------------------------
# Section 4: Generate schedule
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduler.build_schedule()
        st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    scheduler: Scheduler = st.session_state.scheduler
    st.success(f"Schedule built — {scheduler.get_total_time()} min planned.")

    warnings = scheduler.conflict_warnings()
    if warnings:
        for w in warnings:
            st.warning(w)

    st.markdown("**Mark tasks complete / remove from schedule:**")
    for i, task in enumerate(list(scheduler.scheduled_tasks)):
        col_chk, col_lbl, col_status, col_del = st.columns([1, 6, 2, 1])
        with col_chk:
            checked = st.checkbox("", value=task.completed, key=f"task_done_{i}")
            if checked and not task.completed:
                scheduler.complete_task(task)  # marks done; if recurring, adds next occurrence to pet
                st.rerun()
        with col_lbl:
            label = f"{task.title} [{task.pet_name}] — {task.duration_minutes} min, {task.priority}"
            if task.is_recurring:
                label += f" (repeats {task.recurrence_interval})"
            st.write(label)
        with col_status:
            if task.completed:
                st.success("Completed: Yes")
            else:
                st.warning("Completed: No")
        with col_del:
            if st.button("Remove", key=f"sched_del_{i}"):
                scheduler.scheduled_tasks.remove(task)
                scheduler.skipped_tasks.append(task)
                st.rerun()
