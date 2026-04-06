import pytest
from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(minutes=120):
    owner = Owner(name="Jordan", email="", available_minutes_per_day=minutes)
    pet = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
    owner.add_pet(pet)
    return owner, pet


# ---------------------------------------------------------------------------
# Original tests (Phase 2)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", category="walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Breakfast", category="feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Evening walk", category="walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_tasks_by_time_chronological_order():
    """Tasks with HH:MM-HH:MM windows should be returned in start-time order."""
    owner, pet = make_owner()
    pet.add_task(Task("Dinner",      "feeding",    duration_minutes=5,  priority="high",   time_window="18:00-18:15"))
    pet.add_task(Task("Breakfast",   "feeding",    duration_minutes=10, priority="high",   time_window="07:00-07:30"))
    pet.add_task(Task("Afternoon",   "enrichment", duration_minutes=15, priority="medium", time_window="14:00-14:30"))
    pet.add_task(Task("Morning walk","walk",        duration_minutes=30, priority="high",   time_window="08:00-09:00"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    sorted_tasks = scheduler.sort_tasks_by_time()
    windows = [t.time_window for t in sorted_tasks if t.time_window]

    assert windows == ["07:00-07:30", "08:00-09:00", "14:00-14:30", "18:00-18:15"]


def test_sort_tasks_by_time_unwindowed_tasks_last():
    """Tasks without a time_window should appear after all windowed tasks."""
    owner, pet = make_owner()
    pet.add_task(Task("Fetch",     "enrichment", duration_minutes=20, priority="low"))
    pet.add_task(Task("Breakfast", "feeding",    duration_minutes=10, priority="high", time_window="07:00-07:30"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    sorted_tasks = scheduler.sort_tasks_by_time()

    assert sorted_tasks[-1].time_window is None
    assert sorted_tasks[0].time_window == "07:00-07:30"


def test_build_schedule_priority_order():
    """High-priority tasks should always be scheduled before lower-priority ones."""
    owner, pet = make_owner(minutes=60)
    pet.add_task(Task("Low task",    "enrichment", duration_minutes=10, priority="low"))
    pet.add_task(Task("High task",   "walk",       duration_minutes=10, priority="high"))
    pet.add_task(Task("Medium task", "grooming",   duration_minutes=10, priority="medium"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    priorities = [t.priority for t in scheduler.scheduled_tasks]

    assert priorities.index("high") < priorities.index("medium")
    assert priorities.index("medium") < priorities.index("low")


def test_build_schedule_tie_break_shortest_first():
    """Equal-priority tasks should be sorted shortest-duration first."""
    owner, pet = make_owner(minutes=30)
    pet.add_task(Task("Long high",  "walk",    duration_minutes=20, priority="high"))
    pet.add_task(Task("Short high", "feeding", duration_minutes=5,  priority="high"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert scheduler.scheduled_tasks[0].title == "Short high"
    assert scheduler.scheduled_tasks[1].title == "Long high"


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_complete_recurring_daily_task_creates_next_occurrence():
    """Completing a daily recurring task should add a new pending task."""
    owner, pet = make_owner()
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",
                      is_recurring=True, recurrence_interval="daily"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert len(owner.get_all_tasks()) == 1
    scheduler.complete_task(pet.tasks[0])
    assert len(owner.get_all_tasks()) == 2


def test_next_occurrence_is_not_completed():
    """The next occurrence of a recurring task should have completed=False."""
    owner, pet = make_owner()
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",
                      is_recurring=True, recurrence_interval="daily"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    scheduler.complete_task(pet.tasks[0])

    new_task = pet.tasks[1]
    assert new_task.completed is False


def test_daily_recurring_task_due_date_is_tomorrow():
    """A daily recurring task's next occurrence should have due_date = today + 1."""
    owner, pet = make_owner()
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",
                      is_recurring=True, recurrence_interval="daily"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    scheduler.complete_task(pet.tasks[0])

    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)


def test_weekly_recurring_task_due_date_is_next_week():
    """A weekly recurring task's next occurrence should have due_date = today + 7."""
    owner, pet = make_owner()
    pet.add_task(Task("Bath time", "grooming", duration_minutes=20, priority="medium",
                      is_recurring=True, recurrence_interval="weekly"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    scheduler.complete_task(pet.tasks[0])

    assert pet.tasks[1].due_date == date.today() + timedelta(weeks=1)


def test_complete_non_recurring_task_does_not_create_occurrence():
    """Completing a non-recurring task should not add any new tasks."""
    owner, pet = make_owner()
    pet.add_task(Task("One-off walk", "walk", duration_minutes=30, priority="high"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    scheduler.complete_task(pet.tasks[0])

    assert len(owner.get_all_tasks()) == 1



# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_same_window():
    """Two tasks sharing the exact same time window should be flagged as a conflict."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk",       "walk",       duration_minutes=30, priority="high",   time_window="08:00-09:00"))
    pet.add_task(Task("Medication", "medication", duration_minutes=5,  priority="medium", time_window="08:00-09:00"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert len(scheduler.detect_conflicts()) == 1


def test_detect_conflicts_overlapping_windows():
    """Two tasks with overlapping but not identical windows should be flagged."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk",      "walk",    duration_minutes=60, priority="high",   time_window="08:00-09:00"))
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",   time_window="08:30-08:45"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert len(scheduler.detect_conflicts()) == 1


def test_detect_conflicts_no_overlap():
    """Tasks with non-overlapping windows should produce no conflicts."""
    owner, pet = make_owner()
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",   time_window="07:00-07:30"))
    pet.add_task(Task("Walk",      "walk",    duration_minutes=30, priority="high",   time_window="08:00-09:00"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert scheduler.detect_conflicts() == []


def test_conflict_warnings_returns_strings():
    """conflict_warnings() should return a list of non-empty strings."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk",       "walk",       duration_minutes=30, priority="high",   time_window="08:00-09:00"))
    pet.add_task(Task("Medication", "medication", duration_minutes=5,  priority="medium", time_window="08:00-09:00"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    warnings = scheduler.conflict_warnings()

    assert len(warnings) == 1
    assert isinstance(warnings[0], str)
    assert "WARNING" in warnings[0]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_build_schedule_pet_with_no_tasks():
    """A scheduler with no tasks should return an empty schedule without crashing."""
    owner, pet = make_owner()
    scheduler = Scheduler(owner)
    result = scheduler.build_schedule()
    assert result == []


def test_build_schedule_all_tasks_exceed_budget():
    """When all tasks exceed the budget, scheduled_tasks is empty and all are skipped."""
    owner, pet = make_owner(minutes=10)
    pet.add_task(Task("Long walk", "walk",    duration_minutes=60, priority="high"))
    pet.add_task(Task("Bath",      "grooming",duration_minutes=45, priority="high"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert scheduler.scheduled_tasks == []
    assert len(scheduler.skipped_tasks) == 2


def test_build_schedule_skips_completed_tasks():
    """Already-completed tasks should not appear in the schedule."""
    owner, pet = make_owner()
    done = Task("Done walk", "walk", duration_minutes=30, priority="high", completed=True)
    pet.add_task(done)

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    assert done not in scheduler.scheduled_tasks


def test_filter_tasks_by_pet_name():
    """filter_tasks(pet_name=...) should return only tasks for that pet."""
    owner = Owner(name="Jordan", email="", available_minutes_per_day=120)
    mochi = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
    luna  = Pet(name="Luna",  species="cat", age_years=5, energy_level="low")
    mochi.add_task(Task("Walk",     "walk",    duration_minutes=30, priority="high"))
    luna.add_task(Task("Grooming",  "grooming",duration_minutes=15, priority="medium"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    result = owner.filter_tasks(pet_name="Mochi")
    assert all(t.pet_name == "Mochi" for t in result)
    assert len(result) == 1


def test_filter_tasks_by_completed_status():
    """filter_tasks(completed=False) should return only pending tasks."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk",      "walk",    duration_minutes=30, priority="high"))
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high"))
    pet.tasks[0].mark_complete()

    pending = owner.filter_tasks(completed=False)
    done    = owner.filter_tasks(completed=True)

    assert len(pending) == 1
    assert pending[0].title == "Breakfast"
    assert len(done) == 1
    assert done[0].title == "Walk"


def test_filter_tasks_by_pet_and_status_combined():
    """filter_tasks with both pet_name and completed should apply both filters."""
    owner = Owner(name="Jordan", email="", available_minutes_per_day=120)
    mochi = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
    luna  = Pet(name="Luna",  species="cat", age_years=5, energy_level="low")
    mochi.add_task(Task("Walk",     "walk",    duration_minutes=30, priority="high"))
    mochi.add_task(Task("Breakfast","feeding", duration_minutes=10, priority="high"))
    luna.add_task(Task("Grooming",  "grooming",duration_minutes=15, priority="medium"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.tasks[0].mark_complete()

    result = owner.filter_tasks(pet_name="Mochi", completed=False)
    assert len(result) == 1
    assert result[0].title == "Breakfast"


def test_filter_tasks_no_match_returns_empty():
    """filter_tasks with a non-existent pet name should return an empty list."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk", "walk", duration_minutes=30, priority="high"))

    result = owner.filter_tasks(pet_name="NonExistent")
    assert result == []


def test_completing_recurring_task_twice_creates_two_occurrences():
    """Each time a recurring task is completed, exactly one new occurrence is added."""
    owner, pet = make_owner()
    pet.add_task(Task("Breakfast", "feeding", duration_minutes=10, priority="high",
                      is_recurring=True, recurrence_interval="daily"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()

    scheduler.complete_task(pet.tasks[0])   # completes original → adds occurrence #2
    assert len(pet.tasks) == 2

    scheduler.complete_task(pet.tasks[1])   # completes occurrence #2 → adds occurrence #3
    assert len(pet.tasks) == 3
    assert pet.tasks[2].completed is False


def test_build_schedule_excludes_completed_after_complete_task():
    """After complete_task(), the completed task should not re-enter a fresh schedule."""
    owner, pet = make_owner()
    pet.add_task(Task("Walk", "walk", duration_minutes=30, priority="high"))

    scheduler = Scheduler(owner)
    scheduler.build_schedule()
    scheduler.complete_task(pet.tasks[0])

    # Rebuild — the completed task must not appear
    scheduler.build_schedule()
    assert all(t.completed is False for t in scheduler.scheduled_tasks)
