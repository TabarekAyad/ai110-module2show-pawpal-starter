from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Jordan", email="jordan@email.com", available_minutes_per_day=180)

mochi = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
luna  = Pet(name="Luna",  species="cat", age_years=5, energy_level="low")

# --- Tasks: intentional overlaps built in ---
# Conflict 1: same pet, exact same window
mochi.add_task(Task("Morning walk",    "walk",        duration_minutes=30, priority="high",   time_window="08:00-09:00"))
mochi.add_task(Task("Flea medication", "medication",  duration_minutes=5,  priority="medium", time_window="08:00-09:00"))

# Conflict 2: different pets, overlapping windows (08:30 falls inside 08:00-09:00)
luna.add_task(Task( "Breakfast",       "feeding",     duration_minutes=5,  priority="high",   time_window="08:30-08:45"))

# No conflict: non-overlapping
mochi.add_task(Task("Breakfast",       "feeding",     duration_minutes=10, priority="high",   time_window="07:00-07:30", is_recurring=True, recurrence_interval="daily"))
luna.add_task(Task( "Grooming brush",  "grooming",    duration_minutes=15, priority="medium", time_window="14:00-14:30"))
luna.add_task(Task( "Laser toy play",  "enrichment",  duration_minutes=10, priority="low"))

owner.add_pet(mochi)
owner.add_pet(luna)

# --- Build schedule ---
scheduler = Scheduler(owner)
scheduler.build_schedule()

print("=" * 55)
print("  PawPal+ -- Today's Schedule")
print("=" * 55)
print(scheduler.explain_plan())

# --- Conflict warnings (lightweight: returns strings, never crashes) ---
print("\n" + "=" * 55)
print("  Conflict Check")
print("=" * 55)
warnings = scheduler.conflict_warnings()
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")
print("=" * 55)
