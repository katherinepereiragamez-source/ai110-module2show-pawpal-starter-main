from dataclasses import dataclass, field
from typing import List

@dataclass
class Task:
    name: str
    description: str
    duration: int  # in minutes
    frequency: str  # e.g., "daily", "weekly"
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
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task by name."""
        self.tasks = [task for task in self.tasks if task.name != task_name]

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
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

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
        """Generate a daily schedule based on constraints and priorities."""
        # Example: Sort tasks by priority and duration
        self.tasks.sort(key=lambda task: (task.completed, task.duration))

    def explain_schedule(self):
        """Explain the reasoning behind the generated schedule."""
        explanation = []
        for task in self.tasks:
            explanation.append(
                f"Task '{task.name}' is scheduled for {task.duration} minutes. "
                f"Completed: {'Yes' if task.completed else 'No'}."
            )
        return "\n".join(explanation)

    def get_pending_tasks(self):
        """Retrieve all pending tasks."""
        return [task for task in self.tasks if not task.completed]