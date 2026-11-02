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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

`detect_conflicts()` only warns when two tasks ask for the exact same preferred time (for example, Breakfast and Give meds both at 09:00). It does not check whether durations overlap, so a 30-minute walk at 08:00 and meds at 08:15 don't trigger a warning.

This is reasonable for a pet owner because overlaps don't get lost. When `generate_plan()` builds the day, it never lets two tasks run at once: a task whose preferred time is already taken is moved to the next free slot, and its reason says "moved to the earliest free slot". So the warning covers the case most likely to be a mistake (two things booked at the same minute), and the plan itself handles the rest. Exact matching is also simple: one pass that groups tasks by time, instead of comparing every pair of tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
