# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

PawPal+ is a simple task list with several algorithmic improvements:

**Priority-first scheduling with duration tie-breaking**
The scheduler sorts all pending tasks by priority (high → medium → low). When two tasks share the same priority, the shorter one is scheduled first — this maximises how many tasks fit within the owner's daily time budget.

**Filtering by pet and status**
Tasks can be filtered by pet name, completion status, or both. This lets the UI show only what's relevant — e.g. pending tasks for a specific pet — without modifying the underlying data.

**Chronological display sorting**
Once a schedule is built, `sort_tasks_by_time()` reorders it by start time using parsed `HH:MM-HH:MM` windows, so the owner sees tasks in the order they'll actually happen throughout the day.

**Automatic recurring task scheduling**
Tasks marked as `daily` or `weekly` automatically generate their next occurrence when completed. The due date is calculated with Python's `timedelta` (`+1 day` for daily, `+7 days` for weekly) and the new instance is added to the pet's task list immediately.

**Lightweight conflict detection**
`conflict_warnings()` checks all scheduled tasks for overlapping time windows using numeric minute-based comparison (not string matching). It returns a list of human-readable warning strings — never crashes, always safe to iterate.

## Testing PawPal+

### Run the tests

```bash
python -m pytest
```

Or for verbose output with individual test names:

```bash
python -m pytest -v
```

### What the tests cover

The test suite in `tests/test_pawpal.py` contains 24 tests across six categories:

| Category | What is verified |
|---|---|
| **Task basics** | `mark_complete()` flips `completed` to `True`; adding a task increases the pet's task count |
| **Sorting** | Tasks with `HH:MM-HH:MM` windows are returned in chronological order; unwindowed tasks appear last; high-priority tasks are always scheduled before lower ones; equal-priority tasks tie-break by shortest duration first |
| **Recurrence** | Completing a daily task creates one new pending instance with `due_date = today + 1`; weekly tasks get `due_date = today + 7`; completing a recurring task twice creates two separate occurrences; completing a non-recurring task creates nothing; completed tasks never re-enter a rebuilt schedule |
| **Conflict detection** | Exact same window is flagged; overlapping windows (e.g. `08:00-09:00` vs `08:30-08:45`) are flagged; non-overlapping windows are not; `conflict_warnings()` returns formatted warning strings |
| **Filtering** | `filter_tasks()` returns only the specified pet's tasks; filters by `completed` status; both filters applied simultaneously; unknown pet name returns an empty list |
| **Edge cases** | Pet with no tasks returns an empty schedule without crashing; all tasks exceeding the time budget are moved to `skipped_tasks`; already-completed tasks are excluded from the schedule |

### Confidence level

**4 / 5 stars**

The core logic — scheduling, sorting, filtering, recurrence, and conflict detection — is thoroughly tested with 24 passing tests. One star is withheld because time windows are optional in the UI (users can add tasks without them), which limits the real-world effectiveness of `sort_tasks_by_time()` and `detect_conflicts()` for tasks entered through the app. Adding a time window input field to the UI would close this gap.

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
