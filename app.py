(.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % /Users/kalibanghart/CLionProjects/M3OEP-kbanghar/cmake-build-debug/M1AP/pet_engine \
                                --in data/state_in.json \
                                --out data/state_out.json
zsh: not a directory: /Users/kalibanghart/CLionProjects/M3OEP-kbanghar/cmake-build-debug/M1AP/pet_engine
(.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % /Users/kalibanghart/CLionProjects/M3OEP-kbanghar/cmake-build-debug/M1AP \
                                --in data/state_in.json \
                                --out data/state_out.json
Failed to read input file: data/state_in.json
(.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % >....
"health": 80,
"energy": 70,
"happiness": 70,
"streak": 0,
"evolution": 1,
"alive": true,
"last_update_epoch": 0,
"work_points": 50,
"seconds_elapsed": 600
}
JSON
    (.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % /Users/kalibanghart/CLionProjects/M3OEP-kbanghar/cmake-build-debug/M1AP --in data/state_in.json --out data/state_out.json
    (.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % mkdir -p data && echo '{"name":"KaliPet","species":"Cat","health":80,"energy":70,"happiness":70,"streak":0,"evolution":1,"alive":true,"last_update_epoch":0,"work_points":50,"seconds_elapsed":600}' > data/state_in.json
    (.venv) kalibanghart@ip0af52812 M3OEP-kbanghar % /Users/kalibanghart/CLionProjects/M3OEP-kbanghar/cmake-build-debug/M1AP --in data/state_in.json --out data/state_out.json
cat data/state_out.json
{"message":"Nice work! Your pet feels cared for.","alive":true,"last_update_epoch":0,"evolution":1,"happiness":78,"mood_sprite":"happy","energy":69,"species":"Cat","streak":1,"health":87,"name":"KaliPet"}%                                                                                                                                 (.venv) kalibanghart@ip0af52812 M3OEP-kbanghar %

from PySide6.QtWidgets import (
QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
QProgressBar, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

ASSET_DIR = os.path.join("app_py", "assets")


def asset_path(filename: str) -> str:
    return os.path.join(ASSET_DIR, filename)


class GraphicsUI(QWidget):
    def __init__(self):
        super().__init__()

        # Basic window setup
        self.setWindowTitle("StudyPet")
        self.setMinimumSize(720, 480)

        # Main pet sprite area
        self.pet_img = QLabel()
        self.pet_img.setAlignment(Qt.AlignCenter)
        self.pet_img.setText("[pet image]")

        # Inputs
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Pet name")

        self.species_box = QComboBox()
        self.species_box.addItems(["Cat", "Dog", "Owl"])

        # Bars
        self.health_bar = QProgressBar()
        self.energy_bar = QProgressBar()
        self.happy_bar = QProgressBar()

        for b in (self.health_bar, self.energy_bar, self.happy_bar):
            b.setRange(0, 100)

        # Message output
        self.msg = QLabel("Welcome!")
        self.msg.setWordWrap(True)

        # Buttons (simple on purpose)
        self.btn_focus_10 = QPushButton("I studied (10 min)  +50")
        self.btn_focus_25 = QPushButton("Focus session (25 min) +120")
        self.btn_sync = QPushButton("Sync Brightspace (Mock)")
        self.btn_tick = QPushButton("Update Pet Now")
        self.btn_save = QPushButton("Save")

        # ----- Layout -----
        left = QVBoxLayout()
        left.addWidget(self.pet_img, stretch=2)
        left.addWidget(self.msg)

        right = QVBoxLayout()
        right.addWidget(QLabel("Pet Name:"))
        right.addWidget(self.name_input)
        right.addWidget(QLabel("Species:"))
        right.addWidget(self.species_box)

        right.addWidget(QLabel("Health"))
        right.addWidget(self.health_bar)
        right.addWidget(QLabel("Energy"))
        right.addWidget(self.energy_bar)
        right.addWidget(QLabel("Happiness"))
        right.addWidget(self.happy_bar)

        right.addSpacing(10)
        right.addWidget(self.btn_focus_10)
        right.addWidget(self.btn_focus_25)
        right.addWidget(self.btn_sync)
        right.addWidget(self.btn_tick)
        right.addWidget(self.btn_save)
        right.addStretch(1)

        main = QHBoxLayout()
        main.addLayout(left, stretch=2)
        main.addLayout(right, stretch=1)
        self.setLayout(main)

        # Start with default sprite (if it exists)
        self.set_sprite("idle", alive=True)

    def set_sprite(self, mood: str, alive: bool):
        # Pick which png to show based on mood
        if not alive:
            img = asset_path("pet_dead.png")
        else:
            if mood == "happy":
                img = asset_path("pet_happy.png")
            elif mood == "sad":
                img = asset_path("pet_sad.png")
            else:
                img = asset_path("pet_idle.png")

        if os.path.exists(img):
            pix = QPixmap(img)
            self.pet_img.setPixmap(pix.scaled(320, 320, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.pet_img.setText("")  # clear placeholder
        else:

            self.pet_img.setPixmap(QPixmap())
            self.pet_img.setText(f"[Missing {os.path.basename(img)}]")

    def show_error(self, text: str):
        QMessageBox.critical(self, "Error", text)