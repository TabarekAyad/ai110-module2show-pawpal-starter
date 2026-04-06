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

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
