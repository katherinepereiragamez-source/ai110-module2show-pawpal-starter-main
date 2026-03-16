from dataclasses import dataclass, field
from typing import List

@dataclass
class Pet:
    name: str
    age: int
    species: str
    breed: str

@dataclass
class Task:
    name: str
    duration: int  # in minutes
    priority: int  # 1 (high) to 5 (low)
    description: str = ""

class Owner:
    def __init__(self, name: str, pets: List[Pet]):
        self.name = name
        self.pets = pets

    def add_pet(self, pet: Pet):
        """Add a new pet to the owner's list of pets."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]

class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        """Add a new task to the schedule."""
        self.tasks.append(task)

    def generate_schedule(self):
        """Generate a daily schedule based on constraints and priorities."""
        # Placeholder for scheduling logic
        pass

    def explain_schedule(self):
        """Explain the reasoning behind the generated schedule."""
        # Placeholder for explanation logic
        pass