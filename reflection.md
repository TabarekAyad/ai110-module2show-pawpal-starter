# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

    The system is built around four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

    - `Owner` holds the pet owner's basic info and their available time per day — the top-level constraint driving the schedule.
    - `Pet` belongs to an owner and holds a list of care tasks specific to that pet.
    - `Task` represents a single care action (walk, feeding, medication, grooming, etc.) with a duration, priority, optional time window, and a recurring flag for daily repeats like meals or meds.
    - `Scheduler` takes an owner (and all their pets' tasks), applies priority and time-budget constraints, and produces an ordered daily plan with a plain-language explanation.

    **Three core user actions the system supports:**

    1. **Add a pet** — the owner registers a pet by providing its name, species, age, and energy level. The pet is linked to the owner and starts with an empty task list.

    2. **Add/schedule a task** — the owner attaches a care task to a specific pet. Each task has a title, category (walk, feeding, medication, etc.), duration in minutes, a priority level (low, medium, or high), and an optional time window. Tasks can be marked as recurring (e.g., daily feedings).

    3. **Generate today's schedule** — the scheduler collects all tasks across the owner's pets, sorts them by priority, and greedily fits them within the owner's available time budget. It returns an ordered list of scheduled tasks, flags any that were skipped due to time constraints, and produces a plain-language explanation of the plan.

- What classes did you include, and what responsibilities did you assign to each?

    - **`Owner`** — top-level entity holding the owner's basic info and `available_minutes_per_day`, which is the core scheduling constraint. Manages the list of pets.
    - **`Pet`** — linked to an owner. Stores attributes like name, species, age, and energy level. Responsible for holding and retrieving that pet's care tasks.
    - **`Task`** — represents one care action (walk, feeding, medication, grooming, etc.). Holds `duration_minutes`, `priority`, `time_window`, `is_recurring`, and `completed` — everything the scheduler needs to reason about a task.
    - **`Scheduler`** — the algorithmic core. Takes an owner and all their pets' tasks, sorts by priority, fits tasks within the time budget, and produces an ordered daily plan via `build_schedule()`, `detect_conflicts()`, and `explain_plan()`.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
