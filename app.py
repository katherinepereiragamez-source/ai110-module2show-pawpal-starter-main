import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Your personal pet care scheduling assistant.")
st.divider()

# ── Session State Initialization ───────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = {}       # { pet_name: Pet }
if "tasks" not in st.session_state:
    st.session_state.tasks = []      # raw dicts for the table display
if "schedule" not in st.session_state:
    st.session_state.schedule = None

# ── SECTION 1: Owner Setup ─────────────────────────────────────────────────────
st.subheader("👤 Owner")
owner_name = st.text_input("Your name", value="Jordan Rivera")

if st.button("Set Owner"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.pets = {}
    st.session_state.tasks = []
    st.session_state.schedule = None
    st.success(f"Owner set to **{owner_name}**!")

if st.session_state.owner:
    st.info(f"Current owner: **{st.session_state.owner.name}**")

st.divider()

# ── SECTION 2: Add a Pet ───────────────────────────────────────────────────────
st.subheader("🐶 Add a Pet")

col1, col2 = st.columns(2)
with col1:
    pet_name    = st.text_input("Pet name",  value="Biscuit")
    pet_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
with col2:
    pet_breed = st.text_input("Breed", value="Golden Retriever")
    pet_age   = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    if not st.session_state.owner:
        st.error("Please set an owner first.")
    elif pet_name in st.session_state.pets:
        st.warning(f"**{pet_name}** is already added.")
    else:
        new_pet = Pet(name=pet_name, age=pet_age,
                      species=pet_species, breed=pet_breed)
        st.session_state.owner.add_pet(new_pet)
        st.session_state.pets[pet_name] = new_pet
        st.success(f"Added **{pet_name}** the {pet_breed}!")

if st.session_state.pets:
    st.write("**Your pets:**")
    pet_rows = [
        {"Name": p.name, "Species": p.species, "Breed": p.breed, "Age": p.age}
        for p in st.session_state.pets.values()
    ]
    st.table(pet_rows)

st.divider()

# ── SECTION 3: Add a Task ──────────────────────────────────────────────────────
st.subheader("📋 Add a Task")

if not st.session_state.pets:
    st.info("Add at least one pet above before creating tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning Walk")
        assign_to  = st.selectbox("Assign to pet", list(st.session_state.pets.keys()))
    with col2:
        task_desc  = st.text_input("Description", value="Walk around the block")
        duration   = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
    with col3:
        frequency  = st.selectbox("Frequency", ["daily", "weekly", "monthly"])

    if st.button("Add Task"):
        new_task = Task(
            name=task_title,
            description=task_desc,
            duration=duration,
            frequency=frequency,
        )
        pet = st.session_state.pets[assign_to]
        pet.add_task(new_task)

        st.session_state.tasks.append({
            "Pet":         assign_to,
            "Task":        task_title,
            "Description": task_desc,
            "Duration":    f"{duration} min",
            "Frequency":   frequency,
        })
        st.success(f"Task **{task_title}** added to {assign_to}!")

    if st.session_state.tasks:
        st.write("**Current tasks:**")
        st.table(st.session_state.tasks)

st.divider()

# ── SECTION 4: Generate Schedule ──────────────────────────────────────────────
st.subheader("📅 Generate Today's Schedule")

if st.button("Generate Schedule"):
    if not st.session_state.owner:
        st.error("Please set an owner first.")
    elif not st.session_state.pets:
        st.error("Please add at least one pet.")
    elif not st.session_state.tasks:
        st.error("Please add at least one task.")
    else:
        scheduler = Scheduler()
        for task in st.session_state.owner.get_all_tasks():
            scheduler.add_task(task)
        scheduler.generate_schedule()
        st.session_state.schedule = scheduler

if st.session_state.schedule:
    scheduler = st.session_state.schedule
    owner     = st.session_state.owner

    st.success(f"Schedule generated for **{owner.name}**!")

    for pet in owner.pets:
        st.markdown(f"### 🐾 {pet.name} ({pet.breed})")
        if not pet.get_tasks():
            st.caption("No tasks assigned.")
        else:
            for task in pet.get_tasks():
                status = "✅" if task.completed else "⬜"
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{status} **{task.name}** — {task.description}")
                with col2:
                    st.caption(f"⏱ {task.duration} min")
                with col3:
                    st.caption(f"🔁 {task.frequency}")

                # Mark complete button
                btn_key = f"complete_{pet.name}_{task.name}"
                if not task.completed:
                    if st.button("Mark complete", key=btn_key):
                        task.mark_complete()
                        st.rerun()
                else:
                    if st.button("Undo", key=btn_key):
                        task.reset_completion()
                        st.rerun()

    st.divider()
    pending = scheduler.get_pending_tasks()
    total   = len(scheduler.tasks)
    done    = total - len(pending)
    st.progress(done / total if total else 0)
    st.caption(f"{done} of {total} tasks completed today.")