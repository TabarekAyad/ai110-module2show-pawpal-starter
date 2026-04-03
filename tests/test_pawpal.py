from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", category="walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age_years=3, energy_level="high")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Breakfast", category="feeding", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Evening walk", category="walk", duration_minutes=20, priority="medium"))
    assert len(pet.tasks) == 2
