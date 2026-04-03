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
        pass

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age_years: int
    energy_level: str                    # "low" | "medium" | "high"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    email: str
    available_minutes_per_day: int
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner: Owner = owner
        self.time_budget_minutes: int = owner.available_minutes_per_day
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def build_schedule(self) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[tuple]:
        pass

    def explain_plan(self) -> str:
        pass

    def get_total_time(self) -> int:
        pass
