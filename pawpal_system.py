from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    category: str                        # walk / feeding / medication / grooming / enrichment
    duration_minutes: int
    priority: str                        # "low" | "medium" | "high"
    time_window: Optional[str] = None    # e.g. "morning" or "08:00-09:00"
    is_recurring: bool = False
    recurrence_interval: Optional[str] = None  # "daily" | "weekly"
    completed: bool = False
    pet_name: Optional[str] = None       # set when task is added to a pet

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is high."""
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    age_years: int
    energy_level: str                    # "low" | "medium" | "high"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet, stamping the pet's name onto it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> list[Task]:
        """Return this pet's tasks sorted from highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 0), reverse=True)


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of every task across all owned pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return tasks optionally filtered by pet name and/or completion status."""
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.time_budget_minutes: int = owner.available_minutes_per_day
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def build_schedule(self) -> list[Task]:
        """Sort incomplete tasks by priority (then shortest-first on ties) and greedily fit within budget."""
        self.scheduled_tasks = []
        self.skipped_tasks = []
        # Only schedule tasks that haven't been completed yet
        pending = self.owner.filter_tasks(completed=False)
        # Primary: highest priority first. Tie-break: shortest duration first (fits more tasks)
        sorted_tasks = sorted(
            pending,
            key=lambda t: (-PRIORITY_ORDER.get(t.priority, 0), t.duration_minutes)
        )
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.time_budget_minutes:
                self.scheduled_tasks.append(task)
                time_used += task.duration_minutes
            else:
                self.skipped_tasks.append(task)
        return self.scheduled_tasks

    def sort_tasks_by_time(self) -> list[Task]:
        """Return scheduled tasks ordered by time window (windowed tasks first, then the rest)."""
        windowed = [t for t in self.scheduled_tasks if t.time_window is not None]
        unwindowed = [t for t in self.scheduled_tasks if t.time_window is None]
        return sorted(windowed, key=lambda t: t.time_window) + unwindowed

    def reset_recurring_tasks(self) -> None:
        """Reset completion status on all recurring tasks so they re-enter the next day's schedule."""
        for task in self.owner.get_all_tasks():
            if task.is_recurring:
                task.completed = False

    def _parse_window(self, window: str) -> tuple[int, int] | None:
        """Parse a 'HH:MM-HH:MM' string into (start_min, end_min). Returns None if unparseable."""
        try:
            start_str, end_str = window.split("-")
            def to_min(t: str) -> int:
                h, m = t.strip().split(":")
                return int(h) * 60 + int(m)
            return to_min(start_str), to_min(end_str)
        except Exception:
            return None

    def detect_conflicts(self) -> list[tuple]:
        """Return pairs of scheduled tasks whose time windows overlap."""
        conflicts = []
        windowed = [t for t in self.scheduled_tasks if t.time_window is not None]
        for i in range(len(windowed)):
            for j in range(i + 1, len(windowed)):
                a, b = windowed[i], windowed[j]
                a_range = self._parse_window(a.time_window)
                b_range = self._parse_window(b.time_window)
                if a_range and b_range:
                    # Numeric overlap: two ranges overlap if one starts before the other ends
                    if a_range[0] < b_range[1] and b_range[0] < a_range[1]:
                        conflicts.append((a, b))
                else:
                    # Fall back to string equality for labels like "morning" / "evening"
                    if a.time_window == b.time_window:
                        conflicts.append((a, b))
        return conflicts

    def explain_plan(self) -> str:
        """Return a plain-language summary of scheduled and skipped tasks."""
        if not self.scheduled_tasks:
            return "No tasks were scheduled."
        lines = [f"Schedule for {self.owner.name} ({self.get_total_time()} min total):\n"]
        for task in self.scheduled_tasks:
            pet_label = f" [{task.pet_name}]" if task.pet_name else ""
            window = f" -- {task.time_window}" if task.time_window else ""
            lines.append(f"  [+] {task.title}{pet_label} ({task.duration_minutes} min, {task.priority} priority{window})")
        if self.skipped_tasks:
            lines.append("\nSkipped (insufficient time):")
            for task in self.skipped_tasks:
                pet_label = f" [{task.pet_name}]" if task.pet_name else ""
                lines.append(f"  [-] {task.title}{pet_label} ({task.duration_minutes} min, {task.priority} priority)")
        return "\n".join(lines)

    def get_total_time(self) -> int:
        """Return the total minutes of all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)
