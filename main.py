from pawpal_system import Task, Pet, Owner, Scheduler


# ── Owner ──────────────────────────────────────────────────────────────────────
owner = Owner(name="Jordan Rivera")

# ── Pets ───────────────────────────────────────────────────────────────────────
dog = Pet(name="Biscuit", age=3, species="Dog", breed="Golden Retriever")
cat = Pet(name="Luna",    age=5, species="Cat", breed="Siamese")

owner.add_pet(dog)
owner.add_pet(cat)

# ── Tasks ──────────────────────────────────────────────────────────────────────
# Biscuit's tasks
morning_walk = Task(
    name="Morning Walk",
    description="30-minute walk around the neighbourhood",
    duration=30,
    frequency="daily",
)
feeding_dog = Task(
    name="Feed Biscuit",
    description="One cup of dry kibble with warm water",
    duration=5,
    frequency="daily",
)
grooming = Task(
    name="Brush Coat",
    description="Brush Biscuit's coat to reduce shedding",
    duration=15,
    frequency="weekly",
)

# Luna's tasks
feeding_cat = Task(
    name="Feed Luna",
    description="Half a can of wet food in the morning",
    duration=5,
    frequency="daily",
)
litter_box = Task(
    name="Clean Litter Box",
    description="Scoop and replace litter as needed",
    duration=10,
    frequency="daily",
)

dog.add_task(morning_walk)
dog.add_task(feeding_dog)
dog.add_task(grooming)
cat.add_task(feeding_cat)
cat.add_task(litter_box)

# ── Scheduler ─────────────────────────────────────────────────────────────────
scheduler = Scheduler()
for task in owner.get_all_tasks():
    scheduler.add_task(task)

scheduler.generate_schedule()

# ── Print Today's Schedule ────────────────────────────────────────────────────
print("=" * 50)
print(f"  🐾 Today's Schedule — Owner: {owner.name}")
print("=" * 50)

for pet in owner.pets:
    print(f"\n  🐶 {pet.name} ({pet.breed})")
    print(f"  {'─' * 40}")
    for task in pet.get_tasks():
        status = "✅" if task.completed else "⬜"
        print(f"  {status} {task.name:<20} {task.duration:>3} min  [{task.frequency}]")
        print(f"       {task.description}")

print("\n" + "=" * 50)
pending = scheduler.get_pending_tasks()
print(f"  Pending tasks: {len(pending)} / {len(scheduler.tasks)}")
print("=" * 50)