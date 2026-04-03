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
        self.completed = True

    def is_high_priority(self) -> bool:
        return self.priority == "high"


@dataclass
class Pet:
    name: str
    species: str
    age_years: int
    energy_level: str                    # "low" | "medium" | "high"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> list[Task]:
        return sorted(self.tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 0), reverse=True)


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.time_budget_minutes: int = owner.available_minutes_per_day
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def build_schedule(self) -> list[Task]:
        self.scheduled_tasks = []
        self.skipped_tasks = []
        all_tasks = self.owner.get_all_tasks()
        sorted_tasks = sorted(all_tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 0), reverse=True)
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.time_budget_minutes:
                self.scheduled_tasks.append(task)
                time_used += task.duration_minutes
            else:
                self.skipped_tasks.append(task)
        return self.scheduled_tasks

    def detect_conflicts(self) -> list[tuple]:
        conflicts = []
        windowed = [t for t in self.scheduled_tasks if t.time_window is not None]
        for i in range(len(windowed)):
            for j in range(i + 1, len(windowed)):
                if windowed[i].time_window == windowed[j].time_window:
                    conflicts.append((windowed[i], windowed[j]))
        return conflicts

    def explain_plan(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks were scheduled."
        lines = [f"Schedule for {self.owner.name} ({self.get_total_time()} min total):\n"]
        for task in self.scheduled_tasks:
            pet_label = f" [{task.pet_name}]" if task.pet_name else ""
            window = f" — {task.time_window}" if task.time_window else ""
            lines.append(f"  [+] {task.title}{pet_label} ({task.duration_minutes} min, {task.priority} priority{window})")
        if self.skipped_tasks:
            lines.append("\nSkipped (insufficient time):")
            for task in self.skipped_tasks:
                pet_label = f" [{task.pet_name}]" if task.pet_name else ""
                lines.append(f"  [-] {task.title}{pet_label} ({task.duration_minutes} min, {task.priority} priority)")
        return "\n".join(lines)

    def get_total_time(self) -> int:
        return sum(t.duration_minutes for t in self.scheduled_tasks)
