import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Section 1: Owner setup — collect name + time before creating the Owner object
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

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Name:** {owner.name}")
with col2:
    st.write(f"**Available time:** {owner.available_minutes_per_day} min/day")

# ---------------------------------------------------------------------------
# Section 2: Add a pet  →  calls owner.add_pet()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

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
    elif new_pet_name in [p.name for p in owner.pets]:
        st.warning(f"A pet named '{new_pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=new_pet_name.strip(), species=new_species, age_years=1, energy_level=new_energy))
        st.session_state.pet_form_v += 1
        st.rerun()

if owner.pets:
    st.write("**Your pets:**")
    st.table([{"name": p.name, "species": p.species, "energy": p.energy_level} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 3: Add a task  →  calls pet.add_task()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Add a Task")

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
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        if not selected_pet_name or not task_title.strip() or not duration or not priority:
            st.warning("Please fill in all task fields.")
        else:
            target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
            target_pet.add_task(Task(
                title=task_title.strip(),
                category="general",
                duration_minutes=int(duration),
                priority=priority,
            ))
            st.session_state.task_form_v += 1
            st.rerun()

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks:**")
        st.table([
            {"pet": t.pet_name, "task": t.title, "duration (min)": t.duration_minutes, "priority": t.priority}
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

# ---------------------------------------------------------------------------
# Section 4: Generate schedule  →  calls Scheduler.build_schedule()
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        scheduler.build_schedule()
        st.success(f"Schedule built — {scheduler.get_total_time()} min planned.")
        st.text(scheduler.explain_plan())
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning(f"{len(conflicts)} time window conflict(s):")
            for a, b in conflicts:
                st.write(f"  - '{a.title}' and '{b.title}' both during '{a.time_window}'")
