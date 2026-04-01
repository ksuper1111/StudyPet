#
# main.py
# Created by Kali Banghart on 2/28/26.
#
# main.py Controller - connects the UI, engine, and task list together.

import sys
from time import time

from PySide6.QtWidgets import QApplication

from storage       import AppState, load_state, save_state
from task_storage  import TaskList, load_tasks, save_tasks
from engine_bridge import run_engine
from ui            import GraphicsUI


def validate_name(name: str) -> bool:
    name = name.strip()
    return 0 < len(name) <= 24


class StudyPetApp:
    def __init__(self):
        self.ui    = GraphicsUI()
        self.state = load_state()
        self.tasks = load_tasks()

        self.ui.btn_focus_10.clicked.connect(lambda: self.engine_tick(50))
        self.ui.btn_focus_25.clicked.connect(lambda: self.engine_tick(120))
        self.ui.btn_sync.clicked.connect(self.mock_sync)
        self.ui.btn_tick.clicked.connect(lambda: self.engine_tick(0))
        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_new.clicked.connect(self.new_pet)
        self.ui.btn_treat.clicked.connect(self.use_treat)

        self.ui.task_panel.on_add_task.connect(self.handle_add_task)
        self.ui.task_panel.on_complete_task.connect(self.handle_complete_task)
        self.ui.task_panel.on_delete_task.connect(self.handle_delete_task)
        self.ui.task_panel.clear_btn.clicked.connect(self.handle_clear_done)

        self.ui.set_inputs(self.state.name, self.state.species)
        self.ui.task_panel.refresh(self.tasks.all())
        self.startup_tick()
        self.refresh_ui(mood="idle", message="Welcome back!")

    def handle_add_task(self, title, points, deadline_ts):
        self.tasks.add(title, points, deadline_ts)
        save_tasks(self.tasks)
        self.ui.task_panel.refresh(self.tasks.all())

    def handle_complete_task(self, task_id):
        task = self.tasks.complete(task_id)
        if task is None:
            return
        save_tasks(self.tasks)
        self.engine_tick(task.points, _already_collected=True)

    def handle_delete_task(self, task_id):
        self.tasks.delete(task_id)
        save_tasks(self.tasks)
        self.ui.task_panel.refresh(self.tasks.all())

    def handle_clear_done(self):
        self.tasks.clear_done()
        save_tasks(self.tasks)
        self.ui.task_panel.refresh(self.tasks.all())

    def apply_identity_changes(self):
        name    = self.ui.name_input.text().strip()
        species = self.ui.species_box.currentText().strip()
        if validate_name(name):
            self.state.name = name
        if species in ("Cat", "Dog", "Owl"):
            self.state.species = species

    def refresh_ui(self, mood, message):
        self.ui.set_inputs(self.state.name, self.state.species)
        self.ui.set_bars(self.state.health, self.state.energy, self.state.happiness)
        self.ui.set_sprite(mood, alive=self.state.alive)
        self.ui.setWindowTitle(
            f"StudyPet  |  {self.state.name} the {self.state.species}"
            f"  |  Stage {self.state.evolution}  |  Streak {self.state.streak}"
        )
        self.ui.set_message(message)
        self.ui.set_treat_count(self.tasks.total_treats())
        self.ui.set_dead_mode(dead=not self.state.alive)
        self.ui.task_panel.refresh(self.tasks.all())

    def startup_tick(self):
        now     = int(time())
        elapsed = max(0, now - int(self.state.last_update_epoch))
        if elapsed < 30:
            return
        try:
            self.apply_identity_changes()
            new_state, mood, msg = run_engine(self.state, work_points=0)
            penalty = self.tasks.overdue_penalty()
            if penalty > 0 and new_state.alive:
                new_state.health = max(0, new_state.health - penalty // 10)
                if new_state.health <= 0:
                    new_state.alive = False
                msg += f"  ({len(self.tasks.overdue())} overdue task(s) hurt your pet!)"
            self.state = new_state
            save_state(self.state)
            self.refresh_ui(mood=mood, message=msg)
        except Exception as e:
            self.ui.show_error(str(e))

    def engine_tick(self, work_points: int, _already_collected: bool = False):
        try:
            self.apply_identity_changes()
            if not _already_collected:
                work_points += self.tasks.pop_pending_points()
            penalty = self.tasks.overdue_penalty() if work_points == 0 else 0
            new_state, mood, msg = run_engine(self.state, work_points=work_points)
            if penalty > 0 and new_state.alive:
                new_state.health = max(0, new_state.health - penalty // 10)
                if new_state.health <= 0:
                    new_state.alive = False
                    mood = "dead"
                msg += f"  ({len(self.tasks.overdue())} overdue task(s) are hurting your pet!)"
            self.state = new_state
            save_state(self.state)
            save_tasks(self.tasks)
            self.refresh_ui(mood=mood, message=msg)
        except Exception as e:
            self.ui.show_error(str(e))

    def use_treat(self):
        # spend one treat to give the pet +25 energy directly
        # bypasses the C++ engine since we're just bumping a stat
        if not self.tasks.spend_treat():
            return
        self.state.energy = min(100, self.state.energy + 25)
        save_state(self.state)
        save_tasks(self.tasks)
        msg = "Your pet enjoyed the treat! (+25 energy)"
        if self.state.energy >= 80:
            msg = "Your pet is fully energized!"
        self.refresh_ui(mood="happy", message=msg)

    def mock_sync(self):
        self.engine_tick(80)

    def save(self):
        try:
            self.apply_identity_changes()
            save_state(self.state)
            save_tasks(self.tasks)
            self.refresh_ui(mood="idle", message="Saved.")
        except Exception as e:
            self.ui.show_error(str(e))

    def new_pet(self):
        self.state = AppState()
        self.state.last_update_epoch = int(time())
        save_state(self.state)
        self.refresh_ui(mood="idle", message="New pet created!")


def main():
    app        = QApplication(sys.argv)
    controller = StudyPetApp()
    controller.ui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()