# PawPal+ Project Reflection

## 1. System Design

User should be able to:

- Add a pet
- See daily tasks
- Schedule a walk

**a. Initial design**

My initial UML has four main classes. An Owner has many Pets, each Pet has many Tasks, and a Scheduler reads the Owner's data to build the day's plan.

- **Owner**: holds the owner's name, how many minutes they have for pet care today, their preferences, and their list of pets. It handles adding, removing and looking up pets, and gathers every task across all pets.
- **Pet**: holds the pet's name, species, age and its care tasks. It handles adding and removing tasks and returns the tasks that aren't done yet.
- **Task** (dataclass): one care activity (walk, feeding, meds, etc.) with a title, duration, priority (low/medium/high), category, frequency (daily/weekly), an optional preferred time, and a completed flag. It can mark itself complete and turn its priority into a number for sorting.
- **Scheduler**: takes an Owner and a day start time. It sorts tasks by priority, picks the ones that fit in the owner's available time, gives them start times, and explains why each task was chosen.

**b. Design changes**

After asking AI to review the skeleton, I made two changes:

1. **Task now has `start_time` and `reason` fields.** The review pointed out that a Task had no start time or reason, so the plan couldn't answer "when does this happen and why?", which the README requires. The AI first suggested a separate `ScheduledTask` class for this, but that added a fifth class and three more relationships. I wanted the design as simple as possible, so I kept four classes and put the two fields on Task instead. The Scheduler fills them in when it builds the plan.
2. **Task now has a `pet_name` field.** A Task didn't record which pet it belongs to, so once tasks from several pets were combined, the Scheduler couldn't tell whose walk was whose. `Pet.add_task()` sets it. I used the pet's name instead of a reference to the Pet object so the dataclasses don't point at each other.

Things the review flagged that I'm leaving for implementation: deciding what happens to tasks that don't fit in the available time (drop them, or list them as skipped), and handling two tasks that share the same preferred time.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers five things:

1. **Available time:** the owner's minutes for the day. This is a hard limit; tasks that don't fit are skipped and listed.
2. **Priority:** high, medium or low. Tasks are chosen in priority order, so a low-priority task never pushes out a high-priority one.
3. **Owner preferences:** task types the owner cares most about (for example walks) win ties between tasks of the same priority.
4. **Preferred time:** a task can ask for a set time. It gets that time if it's free, or the earliest free slot after it.
5. **Due date and completion:** only unfinished tasks due today (or overdue) are planned.

I decided time and priority mattered most because a busy owner's real problem is "I can't do everything today, so what matters?" Missing meds is worse than missing a brushing session, so priority decides _what_ gets done, and preferred times only decide _when_. Preferences are a tie-breaker because they're about taste, not the pet's health. Shorter tasks come before longer ones of equal priority, so more tasks fit in the day.

**b. Tradeoffs**

`detect_conflicts()` only warns when two tasks ask for the exact same preferred time (for example, Breakfast and Give meds both at 09:00). It does not check whether durations overlap, so a 30-minute walk at 08:00 and meds at 08:15 don't trigger a warning.

This is reasonable for a pet owner because overlaps don't get lost. When `generate_plan()` builds the day, it never lets two tasks run at once: a task whose preferred time is already taken is moved to the next free slot, and its reason says "moved to the earliest free slot". So the warning covers the case most likely to be a mistake (two things booked at the same minute), and the plan itself handles the rest. Exact matching is also simple: one pass that groups tasks by time, instead of comparing every pair of tasks.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code as an agent in every phase: brainstorming the four classes and drafting the Mermaid UML, generating the class skeleton, implementing the scheduling logic, writing the demo script and tests, wiring the Streamlit UI, and drafting documentation. It could edit several files at once and run commands itself (`python main.py`, `python -m pytest`, and the Streamlit app in a browser), so it checked its own work instead of just handing me code.

The most helpful prompts were pasting the assignment's step-by-step instructions for a phase and asking it to do that phase, then asking direct "why" questions about the result, such as whether the diagram had unnecessary relationships, whether "Mermaid.js" meant a JavaScript file, and why "Jordan" was pre-filled in the app.

**b. Judgment and verification**

The clearest moment was the UML in Phase 1. The AI's first design had a fifth class, `ScheduledTask`, to hold each task's start time and reason. When I asked whether the diagram had unnecessary complexity, it said that class added three of the six relationships. I chose to keep only four classes and put `start_time` and `reason` on `Task` instead, because I wanted the design as simple as possible (as per instructions from the assignment and avoid unnecessary complexity).

I also pushed back on scope: in Phase 2 the AI implemented more than needed, so I explicitly asked it to keep the work matched to the assignment. And I didn't let it push to GitHub until I had reviewed the changes and reflection myself.

To verify the AI's work, I relied on running things, not just reading them:

- The demo output in `main.py` showed a 30-minute gap in the first schedule, which led to letting flexible tasks fill gaps between timed tasks.
- When one of the 18 tests failed, the question was whether the bug was in the test or the logic. The scheduler was right (equal-priority tasks go shortest first), and the test's expectation was wrong.
- Testing the Streamlit app found a real bug: "Mark done" marked a _copy_ of the task, because Streamlit can return a copy of an object chosen in a dropdown. The fix was to select tasks by their position in the list.

**c. AI strategy**

- **Most effective features:** editing several files in one step (for example `pawpal_system.py`, `main.py` and the README together), and the AI running the code, tests and app itself so problems showed up right away. Then I would test the app and note of any inconsistencies.
- **A suggestion I modified:** replacing the `ScheduledTask` class with two fields on `Task` (described above) to keep the design at four classes.
- **Chat sessions:** the assignment suggests a separate chat session per phase. I did most phases in one long session instead. That kept context, since the AI remembered the four-class decision when writing later code, but it also meant I had to be clear about where each phase started and stopped. Next time I would start a fresh session for planning-heavy phases like algorithms and testing, so the AI's suggestions aren't based on earlier code.

---

## 4. Testing and Verification

**a. What you tested**

The 18 tests in `tests/test_pawpal.py` cover sorting by time and by priority, filtering by pet and status, daily/weekly/one-time recurrence, conflict detection, staying within the time budget, leaving out completed tasks, and edge cases like pets with no tasks and two tasks at the same time.

These matter because they are the promises the app makes to a pet owner: the most important tasks get done, nothing is double-booked, and a daily task doesn't silently disappear after you finish it. The tests use a fixed date, so recurrence results don't change depending on the day they run.

**b. Confidence**

About 4 out of 5. Every core behavior has a passing test, and I also checked the app by hand in the browser. I'm not at 5 because conflict detection only catches exact time matches, and the Streamlit UI has no automated tests (the "Mark done" bug was only found by trying the app).

Next I would test: a plan that runs past midnight, invalid time text like `"9am"`, a task longer than the whole time budget, three or more tasks at the same time, and completing an overdue weekly task (its next copy could already be in the past).

---

## 5. Reflection

**a. What went well**

I'm most satisfied that the design stayed simple. It started as four classes and ended as the same four classes. All the "smart" features (sorting, filtering, recurrence, conflicts) fit into the existing `Task` and `Scheduler` without new classes, and every scheduled task explains itself with a reason.

**b. What you would improve**

- Save the owner's pets and tasks to a file, so they survive a page refresh (right now they live only in `st.session_state`).
- Let users edit and delete tasks in the app, not just add them and mark them done.
- Detect overlapping durations as conflicts, not just exact time matches.
- Add automated tests for the Streamlit UI.

**c. Key takeaway**

Being the "lead architect" means the AI can write a lot of correct code quickly, but I still have to decide what the system should be and check that it does it. The AI's first ideas were reasonable but not always what I wanted, like the extra `ScheduledTask` class. The most valuable things I did were asking "is this more complex than it needs to be?", keeping each phase to its actual scope, and insisting on running the code and tests rather than trusting that it looked right.
