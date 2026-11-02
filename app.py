from datetime import time

import streamlit as st

from pawpal_system import FREQUENCIES, PRIORITY_LEVELS, Owner, Pet, Scheduler, Task

CATEGORIES = ["walk", "feeding", "meds", "enrichment", "grooming", "general"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on your time and priorities.")

# Streamlit reruns this whole script on every click, so the Owner lives in
# st.session_state. It is only created the first time; later runs reuse it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
# Each widget has a key, so Streamlit remembers what the user typed between reruns.
owner.name = st.text_input("Owner name", value=owner.name, key="owner_name")
owner.available_minutes = st.number_input(
    "Minutes available for pet care today",
    min_value=0, max_value=1440, value=owner.available_minutes, key="owner_minutes",
)
owner.preferences = st.multiselect(
    "Task types you care most about", CATEGORIES, default=owner.preferences, key="owner_prefs"
)

st.divider()

st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"You already have a pet named {pet_name.strip()}.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name.strip()}!")

if owner.pets:
    st.table([{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)} for p in owner.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

st.subheader("Tasks")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        task_pet = st.selectbox("For which pet?", [p.name for p in owner.pets])
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            frequency = st.selectbox("Repeats", FREQUENCIES, index=FREQUENCIES.index("daily"))
        with col2:
            priority = st.selectbox("Priority", PRIORITY_LEVELS, index=2)
            category = st.selectbox("Type", CATEGORIES)
            preferred = st.time_input("Preferred time (empty = any time)", value=None, step=300)
        if st.form_submit_button("Add task"):
            pet = owner.get_pet(task_pet)
            pet.add_task(
                Task(
                    task_title,
                    int(duration),
                    priority,
                    category,
                    frequency=frequency,
                    preferred_time=preferred.strftime("%H:%M") if preferred else None,
                )
            )
            st.success(f"Added {task_title} for {pet.name}!")

    if not owner.get_all_tasks():
        st.info("No tasks yet. Add one above.")
    else:
        # Conflicts are shown next to the task list, so the owner sees them while they can still fix them.
        for warning in scheduler.detect_conflicts():
            st.warning(
                f"⚠️ {warning} Only one can start then; PawPal will move the other to the next free slot. "
                "Change a preferred time if that doesn't work for you."
            )

        st.markdown("**Your tasks** (sorted by time)")
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
        with col2:
            status_filter = st.radio("Show", ["To do", "Done", "All"], horizontal=True)
        shown = scheduler.sort_by_time(
            scheduler.filter_tasks(
                pet_name=None if pet_filter == "All pets" else pet_filter,
                completed={"To do": False, "Done": True, "All": None}[status_filter],
            )
        )
        if shown:
            st.table(
                [
                    {
                        "time": t.preferred_time or "any time",
                        "pet": t.pet_name,
                        "task": t.title,
                        "minutes": t.duration_minutes,
                        "priority": t.priority,
                        "repeats": t.frequency,
                        "due": t.due_date.isoformat(),
                        "status": "✅ done" if t.completed else "to do",
                    }
                    for t in shown
                ]
            )
        else:
            st.info("No tasks match these filters.")

        to_do = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
        if to_do:
            col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
            with col1:
                # The options are list positions, not Task objects: Streamlit can hand back a copy
                # of an object option, and marking a copy done would not change the real task.
                choice = st.selectbox(
                    "Mark a task done",
                    range(len(to_do)),
                    format_func=lambda i: f"{to_do[i].title} ({to_do[i].pet_name}, due {to_do[i].due_date.isoformat()})",
                )
            with col2:
                if st.button("Mark done"):
                    finished = to_do[choice]
                    next_task = scheduler.mark_task_complete(finished)
                    if next_task:
                        st.session_state.flash = (
                            f"Marked {finished.title} done. Next one is due {next_task.due_date.isoformat()}."
                        )
                    else:
                        st.session_state.flash = f"Marked {finished.title} done."
                    st.rerun()  # redraw the table and dropdown with the updated tasks
        if "flash" in st.session_state:
            st.success(st.session_state.pop("flash"))

st.divider()

st.subheader("Today's Schedule")
day_start = st.time_input("Day starts at", value=time(8, 0), step=900)
if st.button("Generate schedule", type="primary"):
    scheduler.day_start = day_start.strftime("%H:%M")
    plan = scheduler.generate_plan()
    if plan:
        used = sum(t.duration_minutes for t in plan)
        st.success(
            f"Scheduled {len(plan)} task(s) using {used} of {owner.available_minutes} minutes."
        )
        st.table(
            [
                {
                    "time": t.start_time,
                    "pet": t.pet_name,
                    "task": t.title,
                    "minutes": t.duration_minutes,
                    "why": t.reason,
                }
                for t in plan
            ]
        )
    else:
        st.info("Nothing to schedule today. Add tasks, or check that you have minutes available.")

    planned_ids = {id(t) for t in plan}
    skipped = [t for t in scheduler.get_todays_tasks() if id(t) not in planned_ids]
    if skipped:
        st.warning(
            "Not enough time today for: "
            + ", ".join(f"{t.title} ({t.pet_name}, {t.duration_minutes} min)" for t in skipped)
        )
    with st.expander("Plan explanation"):
        st.text(scheduler.explain_plan(plan))
