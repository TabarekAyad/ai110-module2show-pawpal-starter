from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@email.com", available_minutes_per_day=90)

mochi = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
luna  = Pet(name="Luna",  species="cat", age_years=5, energy_level="low")

# --- Tasks for Mochi ---
mochi.add_task(Task("Morning walk",    "walk",      duration_minutes=30, priority="high",   time_window="morning"))
mochi.add_task(Task("Breakfast",       "feeding",   duration_minutes=10, priority="high",   is_recurring=True, recurrence_interval="daily"))
mochi.add_task(Task("Flea medication", "medication",duration_minutes=5,  priority="medium", time_window="morning"))
mochi.add_task(Task("Fetch session",   "enrichment",duration_minutes=20, priority="low"))

# --- Tasks for Luna ---
luna.add_task(Task("Breakfast",        "feeding",   duration_minutes=5,  priority="high",   is_recurring=True, recurrence_interval="daily"))
luna.add_task(Task("Grooming brush",   "grooming",  duration_minutes=15, priority="medium", time_window="evening"))
luna.add_task(Task("Laser toy play",   "enrichment",duration_minutes=10, priority="low"))

# --- Build schedule ---
owner.add_pet(mochi)
owner.add_pet(luna)

scheduler = Scheduler(owner)
scheduler.build_schedule()

# --- Output ---
print("=" * 50)
print("       PawPal+ -- Today's Schedule")
print("=" * 50)
print(scheduler.explain_plan())

conflicts = scheduler.detect_conflicts()
if conflicts:
    print("\nConflicts detected:")
    for a, b in conflicts:
        print(f"   {a.title} [{a.pet_name}] and {b.title} [{b.pet_name}] both scheduled during '{a.time_window}'")
else:
    print("\nNo time window conflicts.")
print("=" * 50)
