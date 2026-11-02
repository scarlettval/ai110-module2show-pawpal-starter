from datetime import time

import streamlit as st

from pawpal_system import PRIORITY_LEVELS, Owner, Pet, Scheduler, Task

CATEGORIES = ["walk", "feeding", "meds", "enrichment", "grooming", "general"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on your time and priorities.")

# Streamlit reruns this whole script on every click, so the Owner lives in
# st.session_state. It is only created the first time; later runs reuse it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner

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
        with col2:
            priority = st.selectbox("Priority", PRIORITY_LEVELS, index=2)
            category = st.selectbox("Type", CATEGORIES)
        preferred = st.time_input("Preferred time (leave empty if any time works)", value=None, step=300)
        if st.form_submit_button("Add task"):
            pet = owner.get_pet(task_pet)
            pet.add_task(
                Task(
                    task_title,
                    int(duration),
                    priority,
                    category,
                    preferred_time=preferred.strftime("%H:%M") if preferred else None,
                )
            )
            st.success(f"Added {task_title} for {pet.name}!")

    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.table(
            [
                {
                    "pet": t.pet_name,
                    "task": t.title,
                    "minutes": t.duration_minutes,
                    "priority": t.priority,
                    "type": t.category,
                    "preferred time": t.preferred_time or "any time",
                }
                for t in all_tasks
            ]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
day_start = st.time_input("Day starts at", value=time(8, 0), step=900)
if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(owner, day_start=day_start.strftime("%H:%M"))
    plan = scheduler.generate_plan()
    if plan:
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
    with st.expander("Plan explanation", expanded=not plan):
        st.text(scheduler.explain_plan(plan))
