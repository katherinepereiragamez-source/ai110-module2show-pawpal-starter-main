from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Task:
    name: str
    description: str
    duration: int       # in minutes
    frequency: str      # e.g., "daily", "weekly"
    time: str = "00:00" # scheduled time in "HH:MM" format
    pet_name: str = ""  # owner pet's name, used for filtering
    completed: bool = False

    def mark_complete(self):
        """Mark the task as completed."""
        self.completed = True

    def reset_completion(self):
        """Reset the task's completion status."""
        self.completed = False


@dataclass
class Pet:
    name: str
    age: int
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a new task to the pet's task list."""
        task.pet_name = self.name  # stamp the pet name onto the task
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task by name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_tasks(self):
        """Retrieve all tasks for the pet."""
        return self.tasks


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a new pet to the owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self):
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add a new task to the schedule."""
        self.tasks.append(task)

    def generate_schedule(self):
        """Generate a daily schedule: sort incomplete tasks before complete,
        then by duration within each group."""
        self.tasks.sort(key=lambda t: (t.completed, t.duration))

    # ── NEW: Sorting ──────────────────────────────────────────────────────────
    def sort_by_time(self) -> List[Task]:
        """Return tasks sorted chronologically by their 'HH:MM' time attribute.
        Uses a lambda that splits the string and converts each part to an int
        so '09:00' correctly sorts before '12:30'."""
        return sorted(
            self.tasks,
            key=lambda t: (int(t.time.split(":")[0]), int(t.time.split(":")[1]))
        )

    # ── NEW: Filtering ────────────────────────────────────────────────────────
    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Filter tasks by completion status and/or pet name.

        Args:
            completed: True → only completed tasks, False → only pending,
                       None → no filter on status.
            pet_name:  Case-insensitive pet name to match.
                       None → no filter on pet.
        Returns:
            A new list containing only the tasks that match every supplied filter.
        """
        result = self.tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        return result

    def explain_schedule(self):
        """Explain the reasoning behind the generated schedule."""
        lines = []
        for t in self.tasks:
            lines.append(
                f"Task '{t.name}' is scheduled for {t.duration} minutes. "
                f"Completed: {'Yes' if t.completed else 'No'}."
            )
        return "\n".join(lines)

    def get_pending_tasks(self):
        """Retrieve all pending tasks."""
        return [t for t in self.tasks if not t.completed]

    # ── NEW: Conflict Detection ───────────────────────────────────────────────
    def detect_conflicts(self) -> List[str]:
        """Check for tasks that overlap in time for the same pet.

        Strategy (lightweight — no exceptions raised):
          1. Compute each task's end time from its start time + duration.
          2. Compare every unique pair of tasks belonging to the same pet.
          3. Two tasks conflict when one starts before the other ends.
          4. Collect a human-readable warning string per conflict and return
             the full list so the caller decides how to display it.

        Returns:
            A list of warning strings. Empty list means no conflicts.
        """
        warnings = []

        def to_minutes(t: str) -> int:
            """Convert 'HH:MM' to total minutes since midnight."""
            h, m = t.split(":")
            return int(h) * 60 + int(m)

        def to_hhmm(mins: int) -> str:
            """Convert total minutes back to 'HH:MM' for display."""
            return f"{mins // 60:02d}:{mins % 60:02d}"

        # Group tasks by pet name
        from collections import defaultdict
        by_pet: dict = defaultdict(list)
        for task in self.tasks:
            by_pet[task.pet_name].append(task)

        # Check every unique pair within each pet's task list
        for pet_name, pet_tasks in by_pet.items():
            for i in range(len(pet_tasks)):
                for j in range(i + 1, len(pet_tasks)):
                    a, b = pet_tasks[i], pet_tasks[j]
                    a_start = to_minutes(a.time)
                    a_end   = a_start + a.duration
                    b_start = to_minutes(b.time)
                    b_end   = b_start + b.duration

                    # Overlap when one starts before the other ends
                    if a_start < b_end and b_start < a_end:
                        warnings.append(
                            f"⚠️  CONFLICT [{pet_name}]: "
                            f"'{a.name}' ({a.time}–{to_hhmm(a_end)}) "
                            f"overlaps with "
                            f"'{b.name}' ({b.time}–{to_hhmm(b_end)})"
                        )
        return warnings