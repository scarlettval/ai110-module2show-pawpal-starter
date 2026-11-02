"""PawPal+ logic layer: the Owner, Pet, Task and Scheduler classes from diagrams/uml.mmd."""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_LEVELS = ("low", "medium", "high")


def to_minutes(hhmm: str) -> int:
    """Convert "HH:MM" to minutes after midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def to_hhmm(total_minutes: int) -> str:
    """Convert minutes after midnight to "HH:MM"."""
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


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

    def __post_init__(self) -> None:
        """Reject an unknown priority or a non-positive duration."""
        if self.priority not in PRIORITY_LEVELS:
            raise ValueError(f"priority must be one of {PRIORITY_LEVELS}, got {self.priority!r}")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    def mark_complete(self) -> None:
        """Mark this task as done for today."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a number for sorting (higher = more important)."""
        return PRIORITY_LEVELS.index(self.priority) + 1


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Set pet_name on any tasks passed in when the pet is created."""
        for task in self.tasks:
            task.pet_name = self.name

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet and set its pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        self.tasks = [task for task in self.tasks if task.title != title]

    def get_pending_tasks(self) -> list[Task]:
        """Return tasks that are not yet completed."""
        return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int = 120
    preferences: list[str] = field(default_factory=list)  # task categories the owner cares most about
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> None:
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != name]

    def get_pet(self, name: str) -> Pet | None:
        """Look up a pet by name."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily plan for an owner's pets based on time and priority."""

    def __init__(self, owner: Owner, day_start: str = "08:00") -> None:
        """Store the owner to plan for and the time the day starts ("HH:MM")."""
        self.owner = owner
        self.day_start = day_start

    def generate_plan(self) -> list[Task]:
        """Pick tasks that fit the owner's time, give each a start_time and reason, and return them in order."""
        pending = [task for task in self.owner.get_all_tasks() if not task.completed]

        # Clear results from any earlier run so skipped tasks don't keep old times.
        for task in pending:
            task.start_time = None
            task.reason = ""

        # 1. Pick tasks in priority order until the owner's time budget runs out.
        chosen = []
        minutes_left = self.owner.available_minutes
        for task in self.sort_tasks(pending):
            if task.duration_minutes <= minutes_left:
                chosen.append(task)
                minutes_left -= task.duration_minutes

        # 2. Lay the chosen tasks out through the day. Tasks with a preferred time go at
        #    that time (or as soon after as possible); flexible tasks fill the gaps.
        fixed = sorted(
            (t for t in chosen if t.preferred_time),
            key=lambda t: to_minutes(t.preferred_time),
        )
        flexible = [t for t in chosen if not t.preferred_time]  # already in priority order
        plan = []
        clock = to_minutes(self.day_start)
        while fixed or flexible:
            next_fixed_at = to_minutes(fixed[0].preferred_time) if fixed else None
            filler = next(
                (t for t in flexible
                 if next_fixed_at is None or clock + t.duration_minutes <= next_fixed_at),
                None,
            )
            if filler:
                task = filler
                flexible.remove(task)
            else:
                task = fixed.pop(0)
                clock = max(clock, next_fixed_at)
            task.start_time = to_hhmm(clock)
            task.reason = self._reason_for(task)
            plan.append(task)
            clock += task.duration_minutes

        return plan

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then by owner preference, then shortest first."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority_rank(),
                t.category not in self.owner.preferences,  # False sorts first
                t.duration_minutes,
            ),
        )

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a readable summary of the plan and why each task was included."""
        if not plan:
            return f"No tasks fit into {self.owner.name}'s day."

        used = sum(task.duration_minutes for task in plan)
        lines = [f"Daily plan for {self.owner.name} ({used} of {self.owner.available_minutes} min used):"]
        for task in plan:
            lines.append(
                f"  {task.start_time} - {task.title} for {task.pet_name} "
                f"({task.duration_minutes} min) - {task.reason}"
            )

        # Compare by identity: dataclass == would treat two identical tasks as the same task.
        planned_ids = {id(task) for task in plan}
        skipped = [
            task for task in self.owner.get_all_tasks()
            if not task.completed and id(task) not in planned_ids
        ]
        if skipped:
            titles = ", ".join(f"{task.title} ({task.pet_name})" for task in skipped)
            lines.append(f"Skipped (not enough time): {titles}")
        return "\n".join(lines)

    def _reason_for(self, task: Task) -> str:
        """Build a short explanation of why a task was scheduled when it was."""
        parts = [f"{task.priority} priority"]
        if task.category in self.owner.preferences:
            parts.append(f"you prioritize {task.category}")
        if task.preferred_time == task.start_time:
            parts.append(f"at your preferred time {task.preferred_time}")
        elif task.preferred_time:
            parts.append(f"wanted {task.preferred_time}, moved to the earliest free slot")
        return ", ".join(parts)
