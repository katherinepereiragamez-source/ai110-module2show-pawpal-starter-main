from pawpal_system import Task, Pet, Owner, Scheduler

# ── Owner ──────────────────────────────────────────────────────────────────────
owner = Owner(name="Jordan Rivera")

# ── Pets ───────────────────────────────────────────────────────────────────────
dog = Pet(name="Biscuit", age=3, species="Dog", breed="Golden Retriever")
cat = Pet(name="Luna",    age=5, species="Cat", breed="Siamese")

owner.add_pet(dog)
owner.add_pet(cat)

# ── Tasks ─────────────────────────────────────────────────────────────────────
# Biscuit's tasks
morning_walk = Task(
    name="Morning Walk",
    description="30-minute walk around the neighbourhood",
    duration=30,
    frequency="daily",
    time="07:00",   # 07:00 – 07:30
)
feeding_dog = Task(
    name="Feed Biscuit",
    description="One cup of dry kibble with warm water",
    duration=5,
    frequency="daily",
    time="06:30",
)
grooming = Task(
    name="Brush Coat",
    description="Brush Biscuit's coat to reduce shedding",
    duration=15,
    frequency="weekly",
    time="07:15",   # ⚠️ starts at 07:15, inside Morning Walk (07:00–07:30)
)

# Luna's tasks
feeding_cat = Task(
    name="Feed Luna",
    description="Half a can of wet food in the morning",
    duration=5,
    frequency="daily",
    time="06:45",
)
litter_box = Task(
    name="Clean Litter Box",
    description="Scoop and replace litter as needed",
    duration=10,
    frequency="daily",
    time="06:45",   # ⚠️ exact same start time as Feed Luna
)

dog.add_task(morning_walk)
dog.add_task(feeding_dog)
dog.add_task(grooming)
cat.add_task(feeding_cat)
cat.add_task(litter_box)

# Mark one task complete for demo
grooming.mark_complete()

# ── Scheduler ─────────────────────────────────────────────────────────────────
scheduler = Scheduler()
for task in owner.get_all_tasks():
    scheduler.add_task(task)

# ── Conflict Detection (run BEFORE schedule is printed) ───────────────────────
print("=" * 52)
print("  🔍 Conflict Check")
print("=" * 52)
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  ✅ No conflicts detected.")

# ── Sort by Time ───────────────────────────────────────────────────────────────
print("\n" + "=" * 52)
print("  🕐 Today's Schedule (sorted by time)")
print("=" * 52)
for task in scheduler.sort_by_time():
    status = "✅" if task.completed else "⬜"
    h, m   = task.time.split(":")
    end_m  = int(h) * 60 + int(m) + task.duration
    end    = f"{end_m // 60:02d}:{end_m % 60:02d}"
    print(f"  {status} {task.time}–{end}  {task.name:<20} [{task.pet_name}]")

# ── Filter: Pending only ───────────────────────────────────────────────────────
print("\n" + "=" * 52)
print("  ⬜ Pending tasks")
print("=" * 52)
for task in scheduler.filter_tasks(completed=False):
    print(f"  ⬜ {task.time}  {task.name:<22} [{task.pet_name}]")

# ── Filter: By pet ─────────────────────────────────────────────────────────────
for pet_name in ["Biscuit", "Luna"]:
    print("\n" + "=" * 52)
    print(f"  🐾 {pet_name}'s tasks")
    print("=" * 52)
    for task in scheduler.filter_tasks(pet_name=pet_name):
        status = "✅" if task.completed else "⬜"
        print(f"  {status} {task.time}  {task.name:<22} {task.duration} min")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 52)
pending = scheduler.get_pending_tasks()
print(f"  Pending : {len(pending)} / {len(scheduler.tasks)} tasks")
print(f"  Conflicts detected: {len(conflicts)}")
print("=" * 52)