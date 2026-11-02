# 🐾 PawPal+ (Module 2 Project)

**PawPal+** is a Streamlit app that helps a busy pet owner stay consistent with pet care. You enter your pets and their care tasks (walks, feeding, meds, enrichment, grooming), say how much time you have today, and PawPal+ builds a daily plan, explaining why each task was picked and when it happens.

## ✨ Features

- **Owner and pet profiles:** one owner, any number of pets, each with its own list of care tasks.
- **Priority-based planning:** tasks are chosen high priority first, then by the task types you care most about, then shortest first, until your available minutes run out. Tasks that don't fit are listed as skipped.
- **Preferred times:** a task can ask for a set time (like meds at 09:00). Tasks without one fill the gaps between timed tasks.
- **Sorting by time:** task lists are shown in time-of-day order, with "any time" tasks last.
- **Filtering:** view tasks for one pet or all pets, and only to-do, only done, or everything.
- **Conflict warnings:** if two tasks ask for the same time, PawPal+ shows a warning instead of failing, and the plan moves one of them to the next free slot.
- **Daily and weekly recurrence:** marking a daily task done creates tomorrow's copy; a weekly task comes back 7 days later. One-time tasks don't repeat.
- **Explained plans:** every scheduled task has a short reason, like "high priority, at your preferred time 09:00" or "wanted 09:00, moved to the earliest free slot".

## 🏗️ Architecture

The logic lives in [`pawpal_system.py`](pawpal_system.py) as four classes: `Owner` has `Pet`s, each `Pet` has `Task`s, and the `Scheduler` reads everything through the `Owner` to sort, filter and plan. The Streamlit UI is in [`app.py`](app.py) and a terminal demo is in [`main.py`](main.py).

- Final class diagram: [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd)
- Phase 1 draft, for comparison: [`diagrams/uml.mmd`](diagrams/uml.mmd)

Paste either file into the [Mermaid Live Editor](https://mermaid.live/) to see the diagram.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the terminal demo

```bash
python main.py
```

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

### What you can do in the app

The page has four sections, top to bottom:

- **Owner:** set your name, how many minutes you have for pet care today, and task types you care most about (e.g., walks and meds).
- **Pets:** add a pet with a name, species and age. Duplicate or empty names are refused with an error message. A table lists your pets and how many tasks each has.
- **Tasks:** add a task for a pet with a title, duration, priority, type, frequency (once, daily, weekly) and an optional preferred time. Below the form:
  - a yellow **conflict warning** appears if two tasks ask for the same time;
  - **"Your tasks"** shows a table sorted by time, with filters for which pet and to do / done / all;
  - **"Mark a task done"** completes a task; for a repeating task, a green message says when the next one is due.
- **Today's Schedule:** pick when your day starts and click **Generate schedule**. You get a green summary ("Scheduled 3 task(s) using 45 of 120 minutes"), the plan as a table with a "why" column, a warning listing any tasks that didn't fit, and a text explanation you can expand.

### Example workflow

1. Start the app with `streamlit run app.py`. Set **Minutes available** to 120 and pick **walk** as a task type you care about.
2. Add two pets: **Mochi** (dog) and **Luna** (cat).
3. Add tasks:
   - Mochi: "Morning walk", 30 min, high, daily, at 07:30
   - Mochi: "Breakfast", 10 min, high, daily, at 09:00
   - Luna: "Give meds", 5 min, high, daily, at 09:00
   - Mochi: "Long hike", 200 min, low, once, any time
4. A warning appears right away: _Conflict at 09:00: Breakfast (Mochi) and Give meds (Luna) are set for the same time._ The task table lists the walk first (07:30), then the two 09:00 tasks, then the hike (any time).
5. Set the filter to **Luna** to see only Give meds, then back to **All pets**.
6. Mark **Morning walk** done. The message says the next one is due tomorrow, and with the filter on **All**, the table shows today's walk as done and a new walk due tomorrow.
7. Click **Generate schedule**. The plan has Give meds at 09:00 and Breakfast at 09:05 ("wanted 09:00, moved to the earliest free slot"). The walk isn't there because it's done, and a warning says the 200-minute hike doesn't fit in the remaining time.

### Scheduler behaviors shown

| Behavior                                     | Where you see it                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| Sorting by time (`sort_by_time`)             | "Your tasks" table and the "Mark a task done" dropdown are in time order |
| Filtering (`filter_tasks`)                   | "Show pet" and "Show" controls above the task table                      |
| Conflict warnings (`detect_conflicts`)       | Yellow warning in the Tasks section; the moved task's "why" says so      |
| Recurrence (`mark_task_complete`)            | Marking a daily task done adds a copy due tomorrow                       |
| Time budget and priorities (`generate_plan`) | Low-priority tasks that don't fit are listed as "Not enough time today"  |

### Sample CLI output

The terminal demo (`python main.py`) runs the same features without the UI. This is the part that shows the conflict warning and the schedule; the full output is in the Sample Output section above.

```
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
```
