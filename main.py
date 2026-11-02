"""Demo script: build an owner with two pets and print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=90, preferences=["walk"])

    mochi = Pet("Mochi", "dog", age=3)
    luna = Pet("Luna", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", "walk", preferred_time="08:00"))
    mochi.add_task(Task("Breakfast", 10, "high", "feeding"))
    luna.add_task(Task("Give meds", 5, "high", "meds", preferred_time="09:00"))
    luna.add_task(Task("Play with wand toy", 20, "medium", "enrichment"))
    mochi.add_task(Task("Brush coat", 15, "low", "grooming"))
    mochi.add_task(Task("Long hike", 60, "low", "walk"))

    scheduler = Scheduler(owner, day_start="08:00")
    plan = scheduler.generate_plan()

    print("=" * 60)
    print("Today's Schedule".center(60))
    print("=" * 60)
    print(scheduler.explain_plan(plan))
    print("=" * 60)


if __name__ == "__main__":
    main()
