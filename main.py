"""Demo script: build an owner with two pets and print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_header(title: str) -> None:
    """Print a section title with a rule under it."""
    print()
    print(title)
    print("-" * 60)


def print_tasks(tasks: list[Task]) -> None:
    """Print one line per task: time, title, pet, and status."""
    for task in tasks:
        time = task.start_time or task.preferred_time or "any time"
        status = "done" if task.completed else "to do"
        print(f"  {time:>8}  {task.title:<20} {task.pet_name:<6} [{status}]")


def main() -> None:
    owner = Owner("Jordan", available_minutes=90, preferences=["walk"])

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of time order on purpose, to show sort_by_time() working.
    luna.add_task(Task("Play with wand toy", 20, "medium", "enrichment", preferred_time="17:30"))
    mochi.add_task(Task("Brush coat", 15, "low", "grooming", frequency="weekly"))
    luna.add_task(Task("Give meds", 5, "high", "meds", preferred_time="09:00"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding", preferred_time="09:00"))  # same time as meds
    mochi.add_task(Task("Morning walk", 30, "high", "walk", preferred_time="08:00"))
    mochi.add_task(Task("Long hike", 60, "low", "walk", frequency="once"))

    scheduler = Scheduler(owner, day_start="08:00")

    print_header("All tasks, sorted by preferred time")
    print_tasks(scheduler.sort_by_time(owner.get_all_tasks()))

    print_header("Only Luna's tasks, sorted by time")
    print_tasks(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna")))

    print_header("Conflict check")
    warnings = scheduler.detect_conflicts()
    for warning in warnings:
        print(f"  WARNING: {warning}")
    if not warnings:
        print("  No conflicts.")

    print()
    print("=" * 60)
    print("Today's Schedule".center(60))
    print("=" * 60)
    plan = scheduler.generate_plan()
    print(scheduler.explain_plan(plan))
    print("=" * 60)

    print_header("Recurring tasks: marking Morning walk and Brush coat done")
    walk = next(t for t in mochi.tasks if t.title == "Morning walk")
    brush = next(t for t in mochi.tasks if t.title == "Brush coat")
    for task in (walk, brush):
        next_task = scheduler.mark_task_complete(task)
        print(f"  {task.title} ({task.frequency}) done -> next one due {next_task.due_date}")

    print_header("Mochi's unfinished tasks after that")
    for task in scheduler.filter_tasks(pet_name="Mochi", completed=False):
        print(f"  {task.title:<20} due {task.due_date}")


if __name__ == "__main__":
    main()
