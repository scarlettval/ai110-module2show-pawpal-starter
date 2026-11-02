# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running `python main.py` (one owner with 90 minutes, two pets, six tasks):

```
All tasks, sorted by preferred time
------------------------------------------------------------
     08:00  Morning walk         Mochi  [to do]
     09:00  Breakfast            Mochi  [to do]
     09:00  Give meds            Luna   [to do]
     17:30  Play with wand toy   Luna   [to do]
  any time  Brush coat           Mochi  [to do]
  any time  Long hike            Mochi  [to do]

Only Luna's tasks, sorted by time
------------------------------------------------------------
     09:00  Give meds            Luna   [to do]
     17:30  Play with wand toy   Luna   [to do]

Conflict check
------------------------------------------------------------
  WARNING: Conflict at 09:00: Breakfast (Mochi) and Give meds (Luna) are set for the same time.

============================================================
                      Today's Schedule
============================================================
Daily plan for Jordan (80 of 90 min used):
  08:00 - Morning walk for Mochi (30 min) - high priority, you prioritize walk, at your preferred time 08:00
  08:30 - Brush coat for Mochi (15 min) - low priority
  09:00 - Give meds for Luna (5 min) - high priority, at your preferred time 09:00
  09:05 - Breakfast for Mochi (10 min) - high priority, wanted 09:00, moved to the earliest free slot
  17:30 - Play with wand toy for Luna (20 min) - medium priority, at your preferred time 17:30
Skipped (not enough time): Long hike (Mochi)
============================================================

Recurring tasks: marking Morning walk and Brush coat done
------------------------------------------------------------
  Morning walk (daily) done -> next one due 2026-11-02
  Brush coat (weekly) done -> next one due 2026-11-08

Mochi's unfinished tasks after that
------------------------------------------------------------
  Breakfast            due 2026-11-01
  Long hike            due 2026-11-01
  Morning walk         due 2026-11-02
  Brush coat           due 2026-11-08
```

## 🧪 Testing PawPal+

Run the full test suite from the project folder:

```bash
python -m pytest
```

The 18 tests in `tests/test_pawpal.py` cover:

- **Basics:** marking a task complete, adding a task to a pet (and recording which pet it belongs to), rejecting an invalid priority.
- **Sorting:** `sort_by_time()` returns tasks in chronological order with untimed tasks last; `sort_tasks()` puts high priority first.
- **Filtering:** `filter_tasks()` by pet name, by done/not done, and both together.
- **Recurring tasks:** completing a daily task creates a new one due the next day, a weekly one a week later, and a one-time task does not repeat. Tomorrow's task doesn't appear in today's plan.
- **Conflict detection:** two tasks at the same time produce a warning, different times produce none, and the generated plan never places two tasks at the same time.
- **Edge cases:** the plan stays within the owner's available minutes, completed tasks are left out, and an owner whose pets have no tasks gets an empty plan with a clear message.

Tests use a fixed date instead of today's date, so they give the same result whenever they run.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Scarlett\codepath-ai\ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
collected 18 items

tests\test_pawpal.py ..................                                  [100%]

============================= 18 passed in 0.07s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every core behavior (sorting, filtering, recurrence, conflicts, the time budget) has a passing test, including the main edge cases. It isn't 5 stars because conflict detection only catches exact time matches, the Streamlit UI isn't tested automatically, and some cases are still untested, such as a plan that runs past midnight or invalid time text like `"9am"`.

## 📐 Smarter Scheduling

| Feature                 | Method(s)                                                  | Notes                                                                                                                                                                                            |
| ----------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Sort by time            | `Scheduler.sort_by_time()`                                 | Orders tasks by scheduled time, or preferred time if not scheduled yet. Uses `sorted()` with a `lambda` key on the `"HH:MM"` string; tasks with no time go last.                                 |
| Sort by priority        | `Scheduler.sort_tasks()`, `Task.priority_rank()`           | Used when choosing tasks: high priority first, then the owner's preferred task types, then shortest first.                                                                                       |
| Filtering               | `Scheduler.filter_tasks()`, `Scheduler.get_todays_tasks()` | Filter by pet name and/or done vs. not done. `get_todays_tasks()` keeps only unfinished tasks due today or earlier.                                                                              |
| Fitting the time budget | `Scheduler.generate_plan()`                                | Adds tasks in priority order until the owner's available minutes run out; the rest are listed as skipped by `explain_plan()`.                                                                    |
| Conflict detection      | `Scheduler.detect_conflicts()`                             | Returns a warning message (it never crashes) for each time that two or more tasks ask for. Only exact time matches are flagged; `generate_plan()` moves overlapping tasks to the next free slot. |
| Recurring tasks         | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Marking a `daily` or `weekly` task done adds a fresh copy due 1 day or 7 days later, using `timedelta`. `once` tasks don't repeat.                                                               |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** _(optional)_: <!-- Insert a screenshot or link to a demo video here -->
