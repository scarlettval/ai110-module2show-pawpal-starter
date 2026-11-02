"""PawPal+ logic layer: class skeletons generated from diagrams/uml.mmd.

Method bodies are intentionally left as stubs; scheduling logic comes in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_LEVELS = ("low", "medium", "high")


@dataclass
class Task:
    """A single pet care activity, e.g. a walk, feeding, or medication."""

    title: str
    duration_minutes: int
    priority: str = "medium"           # one of PRIORITY_LEVELS
    category: str = "general"          # walk, feeding, meds, enrichment, grooming, ...
    frequency: str = "daily"           # daily or weekly
    preferred_time: str | None = None  # "HH:MM" if the owner wants it at a set time
    completed: bool = False
    pet_name: str = ""                 # set by Pet.add_task so the plan knows whose task it is
    start_time: str | None = None      # "HH:MM", filled in by the Scheduler
    reason: str = ""                   # why the Scheduler picked this task

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        pass

    def priority_rank(self) -> int:
        """Return a number for sorting (higher = more important)."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet and set its pet_name."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        pass


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int = 120
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name."""
        pass

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        pass


class Scheduler:
    """Builds a daily plan for an owner's pets based on time and priority."""

    def __init__(self, owner: Owner, day_start: str = "08:00") -> None:
        self.owner = owner
        self.day_start = day_start

    def generate_plan(self) -> list[Task]:
        """Choose and order today's tasks so they fit in the owner's available time,
        filling in each chosen task's start_time and reason."""
        pass

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then by preferred time and duration."""
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a readable summary of the plan and why each task was included."""
        pass
