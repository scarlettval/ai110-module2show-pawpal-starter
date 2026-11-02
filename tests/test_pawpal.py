from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

# A fixed "today" so recurrence and due-date tests give the same result on any day.
TODAY = date(2026, 1, 15)


def make_owner(minutes: int = 120) -> Owner:
    """Build an owner with one dog and one cat and no tasks."""
    owner = Owner("Jordan", available_minutes=minutes)
    owner.add_pet(Pet("Mochi", "dog"))
    owner.add_pet(Pet("Luna", "cat"))
    return owner


# --- Task and Pet basics -------------------------------------------------


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10))

    assert len(pet.tasks) == 1


def test_add_task_records_which_pet_it_belongs_to():
    pet = Pet("Mochi", "dog")
    task = Task("Breakfast", 10)

    pet.add_task(task)

    assert task.pet_name == "Mochi"


def test_invalid_priority_is_rejected():
    with pytest.raises(ValueError):
        Task("Walk", 30, priority="urgent")


# --- Sorting --------------------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Dinner", 10, preferred_time="18:00"))
    mochi.add_task(Task("Walk", 30, preferred_time="07:30"))
    mochi.add_task(Task("Meds", 5, preferred_time="12:15"))

    result = Scheduler(owner, today=TODAY).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in result] == ["Walk", "Meds", "Dinner"]


def test_sort_by_time_puts_tasks_without_a_time_last():
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Brush coat", 15))  # no preferred time
    mochi.add_task(Task("Walk", 30, preferred_time="23:45"))

    result = Scheduler(owner, today=TODAY).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in result] == ["Walk", "Brush coat"]


def test_sort_tasks_puts_high_priority_first():
    owner = make_owner()
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Low", 10, priority="low"))
    mochi.add_task(Task("High", 10, priority="high"))
    mochi.add_task(Task("Medium", 10, priority="medium"))

    result = Scheduler(owner, today=TODAY).sort_tasks(owner.get_all_tasks())

    assert [t.title for t in result] == ["High", "Medium", "Low"]


# --- Filtering ------------------------------------------------------------


def test_filter_tasks_by_pet_and_status():
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task("Walk", 30))
    owner.get_pet("Luna").add_task(Task("Meds", 5))
    owner.get_pet("Luna").add_task(Task("Play", 20, completed=True))
    scheduler = Scheduler(owner, today=TODAY)

    assert [t.title for t in scheduler.filter_tasks(pet_name="Luna")] == ["Meds", "Play"]
    assert [t.title for t in scheduler.filter_tasks(pet_name="Luna", completed=False)] == ["Meds"]
    assert [t.title for t in scheduler.filter_tasks(completed=True)] == ["Play"]


# --- Recurring tasks ------------------------------------------------------


def test_completing_daily_task_creates_one_for_the_next_day():
    owner = make_owner()
    walk = Task("Walk", 30, frequency="daily", due_date=TODAY)
    owner.get_pet("Mochi").add_task(walk)

    next_walk = Scheduler(owner, today=TODAY).mark_task_complete(walk)

    assert walk.completed is True
    assert next_walk.due_date == TODAY + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk in owner.get_pet("Mochi").tasks


def test_completing_weekly_task_creates_one_a_week_later():
    owner = make_owner()
    bath = Task("Bath", 20, frequency="weekly", due_date=TODAY)
    owner.get_pet("Mochi").add_task(bath)

    next_bath = Scheduler(owner, today=TODAY).mark_task_complete(bath)

    assert next_bath.due_date == TODAY + timedelta(days=7)


def test_completing_one_time_task_does_not_repeat():
    owner = make_owner()
    vet = Task("Vet visit", 60, frequency="once", due_date=TODAY)
    owner.get_pet("Mochi").add_task(vet)

    assert Scheduler(owner, today=TODAY).mark_task_complete(vet) is None
    assert len(owner.get_pet("Mochi").tasks) == 1


def test_tomorrows_task_is_not_in_todays_plan():
    owner = make_owner()
    walk = Task("Walk", 30, frequency="daily", due_date=TODAY)
    owner.get_pet("Mochi").add_task(walk)
    scheduler = Scheduler(owner, today=TODAY)

    scheduler.mark_task_complete(walk)

    # Today's walk is done and tomorrow's isn't due yet, so nothing is left for today.
    assert scheduler.generate_plan() == []


# --- Conflict detection ---------------------------------------------------


def test_detect_conflicts_flags_duplicate_times():
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task("Breakfast", 10, preferred_time="09:00", due_date=TODAY))
    owner.get_pet("Luna").add_task(Task("Meds", 5, preferred_time="09:00", due_date=TODAY))

    warnings = Scheduler(owner, today=TODAY).detect_conflicts()

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    assert "Breakfast (Mochi)" in warnings[0] and "Meds (Luna)" in warnings[0]


def test_detect_conflicts_is_empty_when_times_differ():
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task("Breakfast", 10, preferred_time="08:00", due_date=TODAY))
    owner.get_pet("Luna").add_task(Task("Meds", 5, preferred_time="09:00", due_date=TODAY))

    assert Scheduler(owner, today=TODAY).detect_conflicts() == []


def test_plan_never_puts_two_tasks_at_the_same_time():
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task("Breakfast", 10, "high", preferred_time="09:00", due_date=TODAY))
    owner.get_pet("Luna").add_task(Task("Meds", 5, "high", preferred_time="09:00", due_date=TODAY))

    plan = Scheduler(owner, today=TODAY).generate_plan()

    # Same priority, so the shorter task (Meds) keeps 09:00 and Breakfast starts right after it.
    assert [(t.title, t.start_time) for t in plan] == [("Meds", "09:00"), ("Breakfast", "09:05")]
    assert "moved" in plan[1].reason


# --- Planning and edge cases ----------------------------------------------


def test_plan_stays_within_available_minutes():
    owner = make_owner(minutes=40)
    mochi = owner.get_pet("Mochi")
    mochi.add_task(Task("Walk", 30, "high", due_date=TODAY))
    mochi.add_task(Task("Feed", 10, "high", due_date=TODAY))
    mochi.add_task(Task("Hike", 60, "low", due_date=TODAY))

    plan = Scheduler(owner, today=TODAY).generate_plan()

    assert sum(t.duration_minutes for t in plan) <= 40
    assert {t.title for t in plan} == {"Walk", "Feed"}


def test_completed_tasks_are_left_out_of_the_plan():
    owner = make_owner()
    owner.get_pet("Mochi").add_task(Task("Walk", 30, completed=True, due_date=TODAY))

    assert Scheduler(owner, today=TODAY).generate_plan() == []


def test_pet_with_no_tasks_gives_an_empty_plan():
    owner = make_owner()  # two pets, no tasks
    scheduler = Scheduler(owner, today=TODAY)

    plan = scheduler.generate_plan()

    assert plan == []
    assert "No tasks fit" in scheduler.explain_plan(plan)
