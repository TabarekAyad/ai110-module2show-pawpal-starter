from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@email.com", available_minutes_per_day=120)

mochi = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
luna  = Pet(name="Luna",  species="cat", age_years=5, energy_level="low")

# --- Tasks added intentionally out of time order ---
mochi.add_task(Task("Evening walk",    "walk",       duration_minutes=25, priority="medium", time_window="17:00-18:00"))
mochi.add_task(Task("Breakfast",       "feeding",    duration_minutes=10, priority="high",   time_window="07:00-07:30", is_recurring=True, recurrence_interval="daily"))
mochi.add_task(Task("Flea medication", "medication", duration_minutes=5,  priority="medium", time_window="09:00-09:15"))
mochi.add_task(Task("Morning walk",    "walk",       duration_minutes=30, priority="high",   time_window="08:00-09:00"))

luna.add_task(Task("Dinner",           "feeding",    duration_minutes=5,  priority="high",   time_window="18:00-18:15", is_recurring=True, recurrence_interval="daily"))
luna.add_task(Task("Grooming brush",   "grooming",   duration_minutes=15, priority="medium", time_window="14:00-14:30"))
luna.add_task(Task("Laser toy play",   "enrichment", duration_minutes=10, priority="low"))
luna.add_task(Task("Breakfast",        "feeding",    duration_minutes=5,  priority="high",   time_window="07:00-07:15", is_recurring=True, recurrence_interval="daily"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Build schedule ---
scheduler = Scheduler(owner)
scheduler.build_schedule()

# --- 1. Raw schedule (priority order) ---
print("=" * 55)
print("  PawPal+ -- Today's Schedule (priority order)")
print("=" * 55)
print(scheduler.explain_plan())

# --- 2. Sorted by start time ---
print("\n" + "=" * 55)
print("  Sorted by start time")
print("=" * 55)
for task in scheduler.sort_tasks_by_time():
    window = f"  [{task.time_window}]" if task.time_window else "  [no window]"
    print(f"{window:22}  {task.title} [{task.pet_name}]")

# --- 3. Filter: pending tasks only ---
print("\n" + "=" * 55)
print("  Filter: pending tasks (all pets)")
print("=" * 55)
for t in owner.filter_tasks(completed=False):
    print(f"  [ ] {t.title} [{t.pet_name}] -- {t.priority}")

# --- 4. Filter: Mochi's tasks only ---
print("\n" + "=" * 55)
print("  Filter: Mochi's tasks only")
print("=" * 55)
for t in owner.filter_tasks(pet_name="Mochi"):
    status = "[x]" if t.completed else "[ ]"
    print(f"  {status} {t.title} -- {t.priority}")

# --- 5. Mark some tasks complete, then filter completed ---
mochi.tasks[0].mark_complete()  # Evening walk
luna.tasks[3].mark_complete()   # Luna's Breakfast

print("\n" + "=" * 55)
print("  Filter: completed tasks")
print("=" * 55)
completed = owner.filter_tasks(completed=True)
if completed:
    for t in completed:
        print(f"  [x] {t.title} [{t.pet_name}]")
else:
    print("  None completed yet.")

# --- 6. Conflicts ---
print("\n" + "=" * 55)
conflicts = scheduler.detect_conflicts()
if conflicts:
    print(f"  {len(conflicts)} conflict(s) detected:")
    for a, b in conflicts:
        print(f"    '{a.title}' and '{b.title}' overlap at '{a.time_window}' / '{b.time_window}'")
else:
    print("  No time window conflicts.")
print("=" * 55)
