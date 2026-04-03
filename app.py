import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner + Pet setup ---
st.subheader("Owner & Pet Info")

col_o1, col_o2 = st.columns(2)
with col_o1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Available minutes/day", min_value=10, max_value=480, value=90)
with col_o2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Initialise the Owner in session_state once; reuse it on every subsequent rerun.
# Without this guard, a fresh Owner (with no pets/tasks) would be created on every click.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(
        name=owner_name,
        email="",
        available_minutes_per_day=available_minutes,
    )
    pet = Pet(name=pet_name, species=species, age_years=1, energy_level="medium")
    st.session_state.owner.add_pet(pet)

owner: Owner = st.session_state.owner
pet: Pet = owner.pets[0]

# --- Task entry ---
st.markdown("### Tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet.add_task(Task(
        title=task_title,
        category="general",
        duration_minutes=int(duration),
        priority=priority,
    ))

all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {"title": t.title, "duration (min)": t.duration_minutes, "priority": t.priority, "pet": t.pet_name}
        for t in all_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    st.success("Schedule generated!")
    st.text(scheduler.explain_plan())
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(f"{len(conflicts)} time window conflict(s) detected:")
        for a, b in conflicts:
            st.write(f"  - '{a.title}' and '{b.title}' both during '{a.time_window}'")
