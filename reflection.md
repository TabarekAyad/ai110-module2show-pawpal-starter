# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The system is built around four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- **`Owner`** — the top-level entity. Holds the owner's name, email, and `available_minutes_per_day`, which is the core scheduling constraint. Responsible for managing the list of pets and collecting all tasks across them.
- **`Pet`** — belongs to an owner. Stores the pet's name, species, age, and energy level. Responsible for holding that pet's care tasks and returning them sorted by priority.
- **`Task`** — represents a single care action such as a walk, feeding, medication, or grooming. Holds `duration_minutes`, `priority`, an optional `time_window`, an `is_recurring` flag for repeating tasks like daily meals or meds, and a `completed` flag.
- **`Scheduler`** — the algorithmic core. Takes an owner (and all their pets' tasks), sorts tasks by priority, and greedily fits them within the owner's time budget. Produces an ordered daily plan via `build_schedule()`, flags overlapping time windows via `detect_conflicts()`, and summarizes the reasoning via `explain_plan()`.

The three core user actions the system supports are:

1. **Add a pet** — register a pet under an owner with its name, species, age, and energy level.
2. **Add a task** — attach a care task to a specific pet with a duration, priority, optional time window, and recurrence setting.
3. **Generate today's schedule** — produce a prioritized, time-constrained daily plan across all pets, with an explanation of what was included and what was skipped.


**b. Design changes**

Yes, three changes were made after reviewing the initial skeleton:

1. **Added `pet_name` to `Task`** — the initial design had `Pet` holding a list of `Task` objects, but a `Task` had no reference back to which pet it belonged to. Once the `Scheduler` collects all tasks across all pets, that context is lost. Adding `pet_name` as an optional attribute (set automatically when `add_task()` is called) means the scheduler can label tasks correctly in the plan output (e.g. *"Walk — Mochi, 20 min"*).

2. **Added a `PRIORITY_ORDER` mapping** — `priority` was stored as a plain string (`"low"` / `"medium"` / `"high"`). Sorting strings alphabetically gives the wrong order (`"high" < "low" < "medium"`). A module-level dictionary `{"high": 3, "medium": 2, "low": 1}` gives `build_schedule()` a correct numeric sort key.

3. **Changed `Scheduler` from `@dataclass` to a plain class** — the initial stub used `@dataclass` for all four classes. `Scheduler` is a poor fit for dataclass because its key attributes (`scheduled_tasks`, `skipped_tasks`, `time_budget_minutes`) are derived state, not constructor inputs. A plain class with an explicit `__init__` is cleaner and clearer.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
