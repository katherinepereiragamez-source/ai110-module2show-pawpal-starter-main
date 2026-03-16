"""
test_pawpal.py — pytest suite for PawPal+
Run with:  pytest test_pawpal.py -v
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_task(name="Task", duration=10, time="08:00",
              frequency="daily", pet_name="Biscuit", completed=False):
    """Factory that creates a Task with sensible defaults."""
    t = Task(name=name, description="", duration=duration,
             frequency=frequency, time=time, pet_name=pet_name,
             completed=completed)
    return t


def make_scheduler(*tasks) -> Scheduler:
    """Create a Scheduler pre-loaded with the given tasks."""
    s = Scheduler()
    for t in tasks:
        s.add_task(t)
    return s


# ══════════════════════════════════════════════════════════════════════════════
# 1. Task — basic behaviour
# ══════════════════════════════════════════════════════════════════════════════

class TestTask:

    def test_defaults(self):
        t = make_task()
        assert t.completed is False

    def test_mark_complete(self):
        t = make_task()
        t.mark_complete()
        assert t.completed is True

    def test_reset_completion(self):
        t = make_task(completed=True)
        t.reset_completion()
        assert t.completed is False


# ══════════════════════════════════════════════════════════════════════════════
# 2. Pet — task management
# ══════════════════════════════════════════════════════════════════════════════

class TestPet:

    def test_add_task_stamps_pet_name(self):
        pet = Pet(name="Luna", age=5, species="Cat", breed="Siamese")
        t = make_task(pet_name="")
        pet.add_task(t)
        assert t.pet_name == "Luna"

    def test_add_multiple_tasks(self):
        pet = Pet(name="Luna", age=5, species="Cat", breed="Siamese")
        pet.add_task(make_task("Feed"))
        pet.add_task(make_task("Play"))
        assert len(pet.get_tasks()) == 2

    def test_remove_task(self):
        pet = Pet(name="Luna", age=5, species="Cat", breed="Siamese")
        pet.add_task(make_task("Feed"))
        pet.add_task(make_task("Play"))
        pet.remove_task("Feed")
        names = [t.name for t in pet.get_tasks()]
        assert "Feed" not in names
        assert "Play" in names


# ══════════════════════════════════════════════════════════════════════════════
# 3. Owner — pet & task aggregation
# ══════════════════════════════════════════════════════════════════════════════

class TestOwner:

    def test_add_pet(self):
        owner = Owner("Jordan")
        dog = Pet("Biscuit", 3, "Dog", "Golden Retriever")
        owner.add_pet(dog)
        assert dog in owner.pets

    def test_remove_pet(self):
        owner = Owner("Jordan")
        dog = Pet("Biscuit", 3, "Dog", "Golden Retriever")
        owner.add_pet(dog)
        owner.remove_pet("Biscuit")
        assert dog not in owner.pets

    def test_get_all_tasks_aggregates(self):
        owner = Owner("Jordan")
        dog = Pet("Biscuit", 3, "Dog", "Golden Retriever")
        cat = Pet("Luna",    5, "Cat", "Siamese")
        dog.add_task(make_task("Walk"))
        cat.add_task(make_task("Feed"))
        owner.add_pet(dog)
        owner.add_pet(cat)
        assert len(owner.get_all_tasks()) == 2


# ══════════════════════════════════════════════════════════════════════════════
# 4. Sorting correctness
# ══════════════════════════════════════════════════════════════════════════════

class TestSorting:

    def test_sort_by_time_chronological(self):
        """Tasks added out of order must come back in HH:MM order."""
        s = make_scheduler(
            make_task("C", time="12:00"),
            make_task("A", time="06:30"),
            make_task("B", time="09:45"),
        )
        sorted_names = [t.name for t in s.sort_by_time()]
        assert sorted_names == ["A", "B", "C"]

    def test_sort_by_time_same_hour_different_minute(self):
        """Minute component must be respected within the same hour."""
        s = make_scheduler(
            make_task("Late",  time="07:45"),
            make_task("Early", time="07:05"),
        )
        sorted_names = [t.name for t in s.sort_by_time()]
        assert sorted_names == ["Early", "Late"]

    def test_sort_by_time_does_not_mutate_scheduler(self):
        """sort_by_time() returns a new list; original order is unchanged."""
        t1 = make_task("C", time="12:00")
        t2 = make_task("A", time="06:30")
        s = make_scheduler(t1, t2)
        s.sort_by_time()
        assert s.tasks[0].name == "C"   # original still first


# ══════════════════════════════════════════════════════════════════════════════
# 5. Recurrence logic
# ══════════════════════════════════════════════════════════════════════════════

class TestRecurrence:

    def test_recur_daily_returns_new_task(self):
        """Completing a daily task and calling recur() gives a fresh task."""
        t = make_task(name="Feed", frequency="daily")
        t.mark_complete()
        next_t = t.recur()
        assert next_t.completed is False

    def test_recur_preserves_metadata(self):
        """The recurred task keeps the same name, duration, time, and pet."""
        t = make_task(name="Walk", duration=30, time="07:00",
                      frequency="daily", pet_name="Biscuit")
        t.mark_complete()
        next_t = t.recur()
        assert next_t.name     == "Walk"
        assert next_t.duration == 30
        assert next_t.time     == "07:00"
        assert next_t.pet_name == "Biscuit"

    def test_recur_weekly(self):
        """Weekly tasks also recur correctly."""
        t = make_task(frequency="weekly")
        t.mark_complete()
        next_t = t.recur()
        assert next_t.completed is False
        assert next_t.frequency == "weekly"

    def test_recur_unsupported_frequency_raises(self):
        """Unsupported frequency values must raise ValueError."""
        t = make_task(frequency="monthly")
        with pytest.raises(ValueError, match="monthly"):
            t.recur()

    def test_recur_does_not_mutate_original(self):
        """Calling recur() must not change the original task."""
        t = make_task(frequency="daily")
        t.mark_complete()
        t.recur()
        assert t.completed is True   # original stays completed


# ══════════════════════════════════════════════════════════════════════════════
# 6. Conflict detection
# ══════════════════════════════════════════════════════════════════════════════

class TestConflictDetection:

    def test_exact_same_time_flagged(self):
        """Two tasks for the same pet at identical times are a conflict."""
        s = make_scheduler(
            make_task("Feed",  time="06:45", duration=5,  pet_name="Luna"),
            make_task("Litter",time="06:45", duration=10, pet_name="Luna"),
        )
        assert len(s.detect_conflicts()) == 1

    def test_partial_overlap_flagged(self):
        """Task B starting inside Task A's window is a conflict."""
        s = make_scheduler(
            make_task("Walk",  time="07:00", duration=30, pet_name="Biscuit"),
            make_task("Brush", time="07:15", duration=15, pet_name="Biscuit"),
        )
        assert len(s.detect_conflicts()) == 1

    def test_no_conflict_when_sequential(self):
        """Task B starting exactly when Task A ends is NOT a conflict."""
        s = make_scheduler(
            make_task("Feed",  time="06:30", duration=5,  pet_name="Biscuit"),
            make_task("Walk",  time="06:35", duration=30, pet_name="Biscuit"),
        )
        assert s.detect_conflicts() == []

    def test_different_pets_no_conflict(self):
        """Same time slots for DIFFERENT pets should not conflict."""
        s = make_scheduler(
            make_task("Feed Dog", time="07:00", duration=5, pet_name="Biscuit"),
            make_task("Feed Cat", time="07:00", duration=5, pet_name="Luna"),
        )
        assert s.detect_conflicts() == []

    def test_conflict_message_contains_pet_and_task_names(self):
        """Warning strings must mention the pet and both task names."""
        s = make_scheduler(
            make_task("Walk",  time="07:00", duration=30, pet_name="Biscuit"),
            make_task("Brush", time="07:15", duration=15, pet_name="Biscuit"),
        )
        warning = s.detect_conflicts()[0]
        assert "Biscuit" in warning
        assert "Walk"    in warning
        assert "Brush"   in warning

    def test_multiple_conflicts_all_reported(self):
        """If two pairs conflict, both warnings are returned."""
        s = make_scheduler(
            make_task("A", time="06:45", duration=5,  pet_name="Luna"),
            make_task("B", time="06:45", duration=10, pet_name="Luna"),
            make_task("C", time="07:00", duration=30, pet_name="Biscuit"),
            make_task("D", time="07:15", duration=15, pet_name="Biscuit"),
        )
        assert len(s.detect_conflicts()) == 2