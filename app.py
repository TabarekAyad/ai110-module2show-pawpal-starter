import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ---------------------------------------------------------------------------
# Session state: initialise the Owner once; every rerun reuses the same object
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name="Jordan",
        email="",
        available_minutes_per_day=90,
    )

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 1: Owner info
# ---------------------------------------------------------------------------
st.subheader("Owner")
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

with st.form("add_pet_form"):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        new_pet_name = st.text_input("Pet name", value="Mochi")
    with col_b:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    with col_c:
        new_energy = st.selectbox("Energy level", ["low", "medium", "high"], index=1)
    submitted_pet = st.form_submit_button("Add pet")

if submitted_pet:
    existing_names = [p.name for p in owner.pets]
    if new_pet_name in existing_names:
        st.warning(f"A pet named '{new_pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=new_pet_name, species=new_species, age_years=1, energy_level=new_energy))
        st.success(f"Added {new_pet_name}!")

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
    with st.form("add_task_form"):
        pet_names = [p.name for p in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        submitted_task = st.form_submit_button("Add task")

    if submitted_task:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        target_pet.add_task(Task(
            title=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
        ))
        st.success(f"Added '{task_title}' to {selected_pet_name}.")

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
