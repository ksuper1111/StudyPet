
from __future__ import annotations

import datetime
import os
from typing import Optional, List

from PySide6.QtCore import Qt, QDate, Signal, QTimer, QRect
from PySide6.QtGui import QPixmap, QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QProgressBar, QComboBox, QLineEdit, QMessageBox,
    QScrollArea, QFrame, QDateEdit, QCheckBox, QSizePolicy,
    QSpacerItem,
)

from task_storage import Task, TASK_SIZES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


def asset_path(filename: str) -> str:
    return os.path.join(ASSET_DIR, filename)


# ─────────────────────────────────────────────────────────────
# colours / style helpers
# ─────────────────────────────────────────────────────────────
_PALETTE = {
    "bg":          "#1e1e2e",
    "panel":       "#2a2a3e",
    "panel_alt":   "#24243a",
    "accent":      "#a78bfa",
    "accent_dim":  "#6d5fc7",
    "green":       "#4ade80",
    "red":         "#f87171",
    "orange":      "#fb923c",
    "text":        "#e2e8f0",
    "text_dim":    "#94a3b8",
    "bar_health":  "#4ade80",
    "bar_energy":  "#60a5fa",
    "bar_happy":   "#f472b6",
    "border":      "#3d3d5c",
}

_BASE_STYLE = f"""
    QWidget {{
        background-color: {_PALETTE['bg']};
        color: {_PALETTE['text']};
        font-family: 'Helvetica';
        font-size: 13px;
    }}
    QLabel {{
        background: transparent;
    }}
    QLineEdit, QComboBox, QDateEdit {{
        background: {_PALETTE['panel']};
        border: 1px solid {_PALETTE['border']};
        border-radius: 6px;
        padding: 5px 8px;
        color: {_PALETTE['text']};
        selection-background-color: {_PALETTE['accent_dim']};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border-color: {_PALETTE['accent']};
    }}
    QPushButton {{
        background: {_PALETTE['panel']};
        border: 1px solid {_PALETTE['border']};
        border-radius: 6px;
        padding: 6px 12px;
        color: {_PALETTE['text']};
    }}
    QPushButton:hover {{
        background: {_PALETTE['accent_dim']};
        border-color: {_PALETTE['accent']};
    }}
    QPushButton:pressed {{
        background: {_PALETTE['accent']};
    }}
    QPushButton:disabled {{
        color: {_PALETTE['text_dim']};
        background: {_PALETTE['panel_alt']};
        border-color: {_PALETTE['border']};
    }}
    QProgressBar {{
        background: {_PALETTE['panel_alt']};
        border: 1px solid {_PALETTE['border']};
        border-radius: 4px;
        height: 10px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        border-radius: 4px;
    }}
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollBar:vertical {{
        background: {_PALETTE['panel_alt']};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {_PALETTE['border']};
        border-radius: 4px;
        min-height: 20px;
    }}
    QCheckBox {{
        background: transparent;
        spacing: 6px;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1px solid {_PALETTE['border']};
        background: {_PALETTE['panel_alt']};
    }}
    QCheckBox::indicator:checked {{
        background: {_PALETTE['accent']};
        border-color: {_PALETTE['accent']};
    }}
"""


def _colored_bar(bar: QProgressBar, color: str):
    bar.setStyleSheet(
        f"QProgressBar::chunk {{ background: {color}; border-radius: 4px; }}"
    )


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(
        f"color: {_PALETTE['text_dim']}; font-size: 10px; letter-spacing: 1.5px; font-weight: 600;"
    )
    return lbl


# ─────────────────────────────────────────────────────────────
# pixel art pet renderer
# 16×16 grid, each cell = pixel_size px square
# sprites stored as {layer_name: [(col,row),...]}
# col 0 = left, row 0 = top
# ─────────────────────────────────────────────────────────────

PIXEL_SIZE = 13  # each pixel block is 13x13 real pixels

# colors for each animal
SPECIES_PALETTES = {
    "Cat": {
        "fur":       "#e8c99a",
        "fur_dark":  "#c4975a",
        "ear_inner": "#ffb6c1",
        "eye_white": "#ffffff",
        "pupil":     "#222222",
        "nose":      "#ff9999",
        "mouth":     "#8b4513",
        "cheek":     "#ffb6c1",
        "tear":      "#87ceeb",
        "outline":   "#3b2314",
        "x_eye":     "#cc2200",
        "bg":        "#1e1e2e",
    },
    "Dog": {
        "fur":       "#c68642",
        "fur_dark":  "#8b5e3c",
        "ear_inner": "#d4956a",
        "eye_white": "#ffffff",
        "pupil":     "#1a0a00",
        "nose":      "#111111",
        "mouth":     "#5c3317",
        "cheek":     "#e8a87c",
        "tear":      "#87ceeb",
        "outline":   "#3b2000",
        "x_eye":     "#cc2200",
        "bg":        "#1e1e2e",
    },
    "Owl": {
        "fur":       "#9b8060",
        "fur_dark":  "#5c4a2a",
        "ear_inner": "#d4aa70",
        "eye_white": "#f5e6c8",
        "pupil":     "#000000",
        "nose":      "#e8a000",
        "mouth":     "#c88000",
        "cheek":     "#c8a870",
        "tear":      "#87ceeb",
        "outline":   "#2a1a00",
        "x_eye":     "#cc2200",
        "bg":        "#1e1e2e",
    },
}


# (col, row) with 0,0 at top left

CAT = {
    "idle": {
        "fur": [
            (2,0),(3,0),          # left ear tip
            (11,0),(12,0),        # right ear tip
            (2,1),(3,1),(4,1),(10,1),(11,1),(12,1),
            (3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),
            (2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),
            (2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),
            (2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),
            (2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),(13,6),
            (2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),
            (2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(13,8),
            (2,9),(3,9),(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),(12,9),(13,9),
            (3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),
            (4,11),(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),(11,11),
            (4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),
            (3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),(12,13),
            (3,14),(4,14),(5,14),(6,14),(7,14),(8,14),(9,14),(10,14),(11,14),(12,14),
            (4,15),(5,15),(10,15),(11,15),
        ],
        "fur_dark": [
            (2,0),(3,0),(2,1),(3,1),        # left ear shadow
            (11,0),(12,0),(12,1),(11,1),    # right ear shadow - slightly different shape on purpose
            (12,13),(12,14),                # body shading on the right
        ],
        "ear_inner": [(3,1),(4,1),(10,1),(11,1)],
        "eye_white": [
            (4,5),(5,5),(4,6),(5,6),
            (9,5),(10,5),(9,6),(10,6),
        ],
        "pupil": [(5,6),(9,6)],
        "nose": [(7,8),(8,8)],
        "mouth": [(6,9),(7,9),(8,9),(9,9)],
    },
    "happy": {
        "fur":       "CAT_idle_fur",
        "fur_dark":  "CAT_idle_fur_dark",
        "ear_inner": "CAT_idle_ear_inner",
        "eye_white": [
            # squished upward = happy squint
            (4,5),(5,5),(6,5),
            (9,5),(10,5),(11,5),
        ],
        "pupil": [(5,6),(6,6),(9,6),(10,6)],  # wider pupils when happy
        "nose": [(7,8),(8,8)],
        "mouth": [(5,9),(6,8),(7,8),(8,8),(9,8),(10,9)],
        "cheek": [(3,7),(4,7),(11,7),(12,7)],
    },
    "sad": {
        "fur":       "CAT_idle_fur",
        "fur_dark":  "CAT_idle_fur_dark",
        "ear_inner": "CAT_idle_ear_inner",
        "eye_white": [
            # eyes lower on face
            (4,6),(5,6),(4,7),(5,7),
            (9,6),(10,6),(9,7),(10,7),
        ],
        "pupil": [(4,7),(9,7)],
        "nose":  [(7,8),(8,8)],
        "mouth": [(5,9),(6,10),(7,10),(8,10),(9,10),(10,9)],
        "tear":  [(4,8),(4,9),(9,8),(9,9)],
    },
    "dead": {
        "fur":       "CAT_idle_fur",
        "fur_dark":  "CAT_idle_fur_dark",
        "ear_inner": "CAT_idle_ear_inner",
        "x_eye": [
            (4,5),(6,5),(5,6),(4,7),(6,7),      # left X
            (9,5),(11,5),(10,6),(9,7),(11,7),    # right X
        ],
        "nose":  [(7,8),(8,8)],
        "mouth": [(5,9),(6,10),(7,10),(8,10),(9,10),(10,9)],
    },
}


DOG = {
    "idle": {
        "fur": [
            # left ear hangs down side
            (1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(2,8),(2,9),(3,9),
            # right ear
            (14,3),(14,4),(14,5),(14,6),(14,7),(14,8),(13,8),(13,9),(12,9),
            (3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),
            (2,2),(3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2),(13,2),
            (2,3),(3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),(13,3),
            (2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),
            (2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),
            (2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),(13,6),
            (2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),
            (2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(13,8),
            (3,9),(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),(12,9),
            # muzzle sticks out a bit
            (5,9),(6,9),(7,9),(8,9),(9,9),(10,9),
            (5,10),(6,10),(7,10),(8,10),(9,10),(10,10),
            (4,11),(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),(11,11),
            (3,12),(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),(12,12),
            (3,13),(4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),(12,13),
            (4,14),(5,14),(10,14),(11,14),
        ],
        "fur_dark": [
            (1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(2,8),(2,9),
            (14,3),(14,4),(14,5),(14,6),(14,7),(14,8),(13,8),(13,9),
        ],
        "ear_inner": [
            (2,4),(2,5),(2,6),(2,7),
            (13,4),(13,5),(13,6),(13,7),
        ],
        "eye_white": [
            (4,4),(5,4),(4,5),(5,5),
            (10,4),(11,4),(10,5),(11,5),
        ],
        "pupil": [(5,5),(10,5)],
        "nose":  [(7,8),(8,8),(7,9),(8,9)],  # dog has a bigger nose
        "mouth": [(6,10),(7,10),(8,10),(9,10)],
    },
    "happy": {
        "fur":       "DOG_idle_fur",
        "fur_dark":  "DOG_idle_fur_dark",
        "ear_inner": "DOG_idle_ear_inner",
        "eye_white": [(4,4),(5,4),(6,4),(9,4),(10,4),(11,4)],
        "pupil":     [(5,5),(6,5),(10,5),(11,5)],
        "nose":  [(7,8),(8,8),(7,9),(8,9)],
        "mouth": [(5,10),(6,9),(7,9),(8,9),(9,9),(10,10)],
        "cheek": [(3,6),(4,6),(11,6),(12,6)],
    },
    "sad": {
        "fur":       "DOG_idle_fur",
        "fur_dark":  "DOG_idle_fur_dark",
        "ear_inner": "DOG_idle_ear_inner",
        "eye_white": [
            (4,5),(5,5),(4,6),(5,6),
            (10,5),(11,5),(10,6),(11,6),
        ],
        "pupil": [(4,6),(10,6)],
        "nose":  [(7,8),(8,8),(7,9),(8,9)],
        "mouth": [(5,10),(6,11),(7,11),(8,11),(9,11),(10,10)],
        "tear":  [(4,7),(4,8),(11,7),(11,8)],
    },
    "dead": {
        "fur":       "DOG_idle_fur",
        "fur_dark":  "DOG_idle_fur_dark",
        "ear_inner": "DOG_idle_ear_inner",
        "x_eye": [
            (4,4),(6,4),(5,5),(4,6),(6,6),
            (10,4),(12,4),(11,5),(10,6),(12,6),
        ],
        "nose":  [(7,8),(8,8),(7,9),(8,9)],
        "mouth": [(5,10),(6,11),(7,11),(8,11),(9,11),(10,10)],
    },
}

# owl was hardest, big eyes took a while to get looking right
OWL = {
    "idle": {
        "fur": [
            (4,0),(5,0),(4,1),(5,1),          # left ear tuft
            (10,0),(11,0),(10,1),(11,1),       # right ear tuft
            (4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),
            (3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),
            (3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),
            (3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),
            (3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),
            (3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),
            (3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),
            (4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),
            # wings are wide
            (2,10),(3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),(13,10),
            (2,11),(3,11),(4,11),(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),(11,11),(12,11),(13,11),
            (3,12),(4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),(12,12),
            (4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),
            (5,14),(6,14),(9,14),(10,14),
        ],
        "fur_dark": [
            (4,0),(5,0),(4,1),(5,1),
            (10,0),(11,0),(10,1),(11,1),
            (2,10),(13,10),(2,11),(13,11),    # wing tips darker
            (11,12),(12,12),(11,13),
        ],
        "ear_inner": [(4,0),(5,0),(10,0),(11,0)],
        "eye_white": [
            # big 3x3 eyes, owls have huge eyes
            (4,4),(5,4),(6,4),
            (4,5),(5,5),(6,5),
            (4,6),(5,6),(6,6),
            (9,4),(10,4),(11,4),
            (9,5),(10,5),(11,5),
            (9,6),(10,6),(11,6),
        ],
        "pupil": [(5,5),(5,6),(10,5),(10,6)],
        "nose":  [(7,7),(8,7),(7,8),(8,8)],  # beak not nose but using same layer
        "mouth": [],
    },
    "happy": {
        "fur":       "OWL_idle_fur",
        "fur_dark":  "OWL_idle_fur_dark",
        "ear_inner": "OWL_idle_ear_inner",
        "eye_white": [
            # squint - just top half of big eyes
            (4,4),(5,4),(6,4),(4,5),(5,5),(6,5),
            (9,4),(10,4),(11,4),(9,5),(10,5),(11,5),
        ],
        "pupil": [(4,6),(5,6),(6,6),(9,6),(10,6),(11,6)],
        "nose":  [(7,7),(8,7),(7,8),(8,8)],
        "mouth": [(6,9),(7,9),(8,9),(9,9)],
        "cheek": [(3,6),(12,6)],  # just one pixel each side, owls dont blush much
    },
    "sad": {
        "fur":       "OWL_idle_fur",
        "fur_dark":  "OWL_idle_fur_dark",
        "ear_inner": "OWL_idle_ear_inner",
        "eye_white": [
            (4,5),(5,5),(6,5),(4,6),(5,6),(6,6),
            (9,5),(10,5),(11,5),(9,6),(10,6),(11,6),
        ],
        "pupil": [(5,6),(10,6)],
        "nose":  [(7,7),(8,7),(7,8),(8,8)],
        "mouth": [(5,9),(6,10),(7,10),(8,10),(9,10),(10,9)],
        "tear":  [(4,7),(4,8),(11,7),(11,8)],
    },
    "dead": {
        "fur":       "OWL_idle_fur",
        "fur_dark":  "OWL_idle_fur_dark",
        "ear_inner": "OWL_idle_ear_inner",
        "x_eye": [
            (4,4),(6,4),(5,5),(4,6),(6,6),
            (9,4),(11,4),(10,5),(9,6),(11,6),
        ],
        "nose":  [(7,7),(8,7),(7,8),(8,8)],
        "mouth": [(5,9),(6,10),(7,10),(8,10),(9,10),(10,9)],
    },
}

# just a dict so i can look up sprites by species name
ALL_SPRITES = {
    "Cat": CAT,
    "Dog": DOG,
    "Owl": OWL,
}

# some moods reuse body pixels from idle so i store them as a string
# and look up real list here instead of copying everything
def _get_pixels(species, mood, layer, sprite_data):
    val = sprite_data.get(layer, [])
    if isinstance(val, str):

        chunks = val.split("_")
        # chunks[0] = species prefix (cat/dog/owl), chunks[1] = mood, chunks[2] = layer
        ref_mood  = chunks[1]
        ref_layer = chunks[2]
        base = ALL_SPRITES.get(species, {})
        return base.get(ref_mood, {}).get(ref_layer, [])
    return val

# bob up and down a little each frame
_ANIM_OFFSETS = [(0,0),(0,-1),(0,-1),(0,-2),(0,-1),(0,-1),(0,0),(0,1),(0,0)]


class PixelPetWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mood    = "idle"
        self._species = "Cat"
        self._alive   = True
        self._frame   = 0

        size = 16 * PIXEL_SIZE + 8
        self.setFixedSize(size, size)

        # timer to animate bob
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(200)

    def set_mood(self, mood, species, alive):
        if not alive:
            self._mood = "dead"
        else:
            self._mood = mood
        if species in ALL_SPRITES:
            self._species = species
        else:
            self._species = "Cat"  # fallback
        self._alive  = alive
        self._frame  = 0
        self.update()

    def _tick(self):
        if self._alive:
            self._frame = (self._frame + 1) % len(_ANIM_OFFSETS)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(_PALETTE["bg"]))

        species = self._species
        mood    = self._mood
        pal     = SPECIES_PALETTES.get(species, SPECIES_PALETTES["Cat"])

        # get right sprite dict for this species + mood
        sprite_set = ALL_SPRITES.get(species, ALL_SPRITES["Cat"])
        sprite = sprite_set.get(mood, sprite_set["idle"])

        dx, dy = _ANIM_OFFSETS[self._frame]
        P  = PIXEL_SIZE
        ox = 4 + dx
        oy = 4 + dy

        # helper to draw one layer
        def draw_layer(layer_name, color_hex, alpha=255):
            pixels = _get_pixels(species, mood, layer_name, sprite)
            if not pixels:
                return
            c = QColor(color_hex)
            c.setAlpha(alpha)
            for col, row in pixels:
                painter.fillRect(ox + col*P, oy + row*P, P, P, c)

        # draw back to front so things layer correctly
        draw_layer("fur_dark",  pal["fur_dark"])
        draw_layer("fur",       pal["fur"])
        draw_layer("ear_inner", pal["ear_inner"])
        draw_layer("eye_white", pal["eye_white"])
        draw_layer("pupil",     pal["pupil"])
        draw_layer("x_eye",     pal["x_eye"])
        draw_layer("nose",      pal["nose"])
        draw_layer("mouth",     pal["mouth"])
        draw_layer("cheek",     pal["cheek"], alpha=160)  # semi transparent
        draw_layer("tear",      pal["tear"])

        painter.end()


class TaskRowWidget(QFrame):
    """
    Emits signals up to TaskPanel.
    complete_requested(task_id)
    delete_requested(task_id)
    """
    complete_requested = Signal(int)
    delete_requested   = Signal(int)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task_id = task.id

        overdue  = task.is_overdue()
        deadline = task.deadline_label()

        if task.done:
            bg = _PALETTE["panel_alt"]
        elif overdue:
            bg = "#3a1f1f"
        else:
            bg = _PALETTE["panel"]

        self.setStyleSheet(f"""
            QFrame {{
                background: {bg};
                border: 1px solid {'#5c2a2a' if overdue else _PALETTE['border']};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(58)

        self.chk = QCheckBox()
        self.chk.setChecked(task.done)
        self.chk.setEnabled(not task.done)
        self.chk.clicked.connect(self._on_clicked)

        title_lbl = QLabel(task.title)
        title_lbl.setStyleSheet(
            f"color: {_PALETTE['text_dim'] if task.done else _PALETTE['text']};"
            f"{'text-decoration: line-through;' if task.done else ''}"
            f"font-size: 13px;"
        )
        title_lbl.setWordWrap(False)
        title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # points badge - also show treat reward
        if task.done and task.treats > 0:
            pts_text = f"+{task.points} pts  🍬x{task.treats}"
        elif not task.done:
            if   task.points >= 120: treat_hint = "🍬x3"
            elif task.points >= 60:  treat_hint = "🍬x2"
            else:                    treat_hint = "🍬x1"
            pts_text = f"+{task.points} pts  {treat_hint}"
        else:
            pts_text = f"+{task.points} pts"
        pts_lbl = QLabel(pts_text)
        pts_lbl.setStyleSheet(
            f"color: {_PALETTE['accent']}; font-size: 11px; font-weight: 600;"
            f"background: transparent;"
        )

        deadline_lbl = QLabel(deadline)
        if deadline:
            color = _PALETTE["red"] if overdue else _PALETTE["orange"]
            deadline_lbl.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: 600;")

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {_PALETTE['text_dim']}; font-size: 14px;
            }}
            QPushButton:hover {{ color: {_PALETTE['red']}; }}
        """)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.task_id))

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 0, 8, 0)
        row.setSpacing(8)
        row.addWidget(self.chk)
        row.addWidget(title_lbl, stretch=1)
        if deadline:
            row.addWidget(deadline_lbl)
        row.addWidget(pts_lbl)
        row.addWidget(del_btn)

    def _on_clicked(self, checked):
        if checked:
            self.complete_requested.emit(self.task_id)


# ─────────────────────────────────────────────────────────────
# taskpanel  –  add-form + scrollable task list
# ─────────────────────────────────────────────────────────────

class TaskPanel(QWidget):
    on_add_task      = Signal(str, int, object)
    on_complete_task = Signal(int)
    on_delete_task   = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        header = QLabel("📋  Tasks")
        header.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {_PALETTE['text']}; background: transparent;"
        )
        root.addWidget(header)

        form_frame = QFrame()
        form_frame.setStyleSheet(f"""
            QFrame {{
                background: {_PALETTE['panel']};
                border: 1px solid {_PALETTE['border']};
                border-radius: 10px;
            }}
        """)
        form = QVBoxLayout(form_frame)
        form.setContentsMargins(10, 10, 10, 10)
        form.setSpacing(6)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task title…")
        self.title_input.returnPressed.connect(self._emit_add)

        size_row = QHBoxLayout()
        self.size_box = QComboBox()
        self.size_box.addItems(list(TASK_SIZES.keys()))
        self.size_box.setCurrentIndex(1)   # Medium default

        self.use_deadline = QCheckBox("Deadline")
        self.use_deadline.setStyleSheet(f"color: {_PALETTE['text_dim']}; font-size: 12px;")
        self.use_deadline.toggled.connect(self._toggle_deadline)

        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDate(QDate.currentDate().addDays(1))
        self.deadline_edit.setVisible(False)
        self.deadline_edit.setFixedWidth(120)

        size_row.addWidget(self.size_box, stretch=1)
        size_row.addWidget(self.use_deadline)
        size_row.addWidget(self.deadline_edit)

        self.add_btn = QPushButton("+ Add Task")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {_PALETTE['accent_dim']};
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 600;
                padding: 7px;
            }}
            QPushButton:hover {{ background: {_PALETTE['accent']}; }}
            QPushButton:disabled {{ background: {_PALETTE['panel_alt']}; color: {_PALETTE['text_dim']}; }}
        """)
        self.add_btn.clicked.connect(self._emit_add)

        form.addWidget(self.title_input)
        form.addLayout(size_row)
        form.addWidget(self.add_btn)
        root.addWidget(form_frame)

        self.summary_lbl = QLabel("")
        self.summary_lbl.setStyleSheet(f"color: {_PALETTE['text_dim']}; font-size: 11px;")
        root.addWidget(self.summary_lbl)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(6)
        self.list_layout.addStretch(1)

        self.scroll.setWidget(self.list_container)
        root.addWidget(self.scroll, stretch=1)

        footer = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Completed")
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {_PALETTE['border']};
                color: {_PALETTE['text_dim']};
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 5px;
            }}
            QPushButton:hover {{ color: {_PALETTE['red']}; border-color: {_PALETTE['red']}; }}
        """)
        footer.addStretch()
        footer.addWidget(self.clear_btn)
        root.addLayout(footer)

    def _toggle_deadline(self, checked: bool):
        self.deadline_edit.setVisible(checked)

    def _emit_add(self):
        title = self.title_input.text().strip()
        if not title:
            return

        points = TASK_SIZES.get(self.size_box.currentText(), 60)

        deadline_ts: Optional[float] = None
        if self.use_deadline.isChecked():
            qd = self.deadline_edit.date()
            dt = datetime.datetime(qd.year(), qd.month(), qd.day(), 23, 59, 59)
            deadline_ts = dt.timestamp()

        self.on_add_task.emit(title, points, deadline_ts)
        self.title_input.clear()

    def refresh(self, tasks: List[Task]):
        # remove all rows but keep trailing stretch
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pending = [t for t in tasks if not t.done]
        done    = [t for t in tasks if t.done]
        overdue = [t for t in tasks if t.is_overdue()]

        parts = [f"{len(pending)} pending"]
        if overdue:
            parts.append(f"⚠ {len(overdue)} overdue")
        if done:
            parts.append(f"{len(done)} done")
        self.summary_lbl.setText("  ·  ".join(parts))

        for task in (pending + done):
            row = TaskRowWidget(task)
            row.complete_requested.connect(self.on_complete_task)
            row.delete_requested.connect(self.on_delete_task)
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)

        if not tasks:
            empty = QLabel("No tasks yet — add one above!")
            empty.setStyleSheet(f"color: {_PALETTE['text_dim']}; font-size: 12px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.insertWidget(0, empty)

    def set_form_enabled(self, enabled: bool):
        """Disable add-form (e.g. when pet is dead)."""
        self.title_input.setEnabled(enabled)
        self.size_box.setEnabled(enabled)
        self.use_deadline.setEnabled(enabled)
        self.deadline_edit.setEnabled(enabled)
        self.add_btn.setEnabled(enabled)


# ─────────────────────────────────────────────────────────────
# graphicsui  –  main window (drop-in replacement)
# ─────────────────────────────────────────────────────────────

class GraphicsUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("StudyPet")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(_BASE_STYLE)

        # procedural pixel-art pet — no png files needed
        self.pet_widget = PixelPetWidget()

        self.msg = QLabel("Welcome!")
        self.msg.setWordWrap(True)
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setStyleSheet(
            f"color: {_PALETTE['text_dim']}; font-size: 12px; padding: 4px;"
        )

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Pet name")

        self.species_box = QComboBox()
        self.species_box.addItems(["Cat", "Dog", "Owl"])

        self.health_bar = QProgressBar()
        self.energy_bar = QProgressBar()
        self.happy_bar  = QProgressBar()
        for b in (self.health_bar, self.energy_bar, self.happy_bar):
            b.setRange(0, 100)
            b.setFixedHeight(10)
        _colored_bar(self.health_bar, _PALETTE["bar_health"])
        _colored_bar(self.energy_bar, _PALETTE["bar_energy"])
        _colored_bar(self.happy_bar,  _PALETTE["bar_happy"])

        self.btn_focus_10 = QPushButton("📖  Studied 10 min  (+50)")
        self.btn_focus_25 = QPushButton("🎯  Focus 25 min  (+120)")
        self.btn_sync     = QPushButton("🔄  Sync Grades (mock)")
        self.btn_tick     = QPushButton("⏱  Update Pet Now")
        self.btn_save     = QPushButton("💾  Save")
        self.btn_new      = QPushButton("🐣  New Pet")
        self.btn_treat    = QPushButton("🍬  Use Treat  (+25 energy)  [0]")

        self.task_panel = TaskPanel()

        self._build_layout()
        self.set_sprite("idle", alive=True)

    def _build_layout(self):
        # left: pet + message
        left = QVBoxLayout()
        left.setSpacing(8)
        left.addWidget(self.pet_widget, alignment=Qt.AlignHCenter)
        left.addWidget(self.msg)
        left.addStretch(1)

        # centre: identity + stats + actions
        centre = QVBoxLayout()
        centre.setSpacing(8)
        centre.setContentsMargins(0, 0, 0, 0)

        centre.addWidget(_section_label("Pet"))
        centre.addWidget(self.name_input)
        centre.addWidget(self.species_box)

        centre.addSpacing(8)
        centre.addWidget(_section_label("Stats"))

        def _stat_row(label: str, bar: QProgressBar) -> QHBoxLayout:
            lbl = QLabel(label)
            lbl.setFixedWidth(66)
            lbl.setStyleSheet(f"color: {_PALETTE['text_dim']}; font-size: 12px;")
            row = QHBoxLayout()
            row.addWidget(lbl)
            row.addWidget(bar)
            return row

        centre.addLayout(_stat_row("❤ Health",    self.health_bar))
        centre.addLayout(_stat_row("⚡ Energy",    self.energy_bar))
        centre.addLayout(_stat_row("😊 Happy",     self.happy_bar))

        centre.addSpacing(10)
        centre.addWidget(_section_label("Actions"))
        centre.addWidget(self.btn_focus_10)
        centre.addWidget(self.btn_focus_25)
        centre.addWidget(self.btn_sync)
        centre.addWidget(self.btn_tick)
        centre.addWidget(self.btn_save)
        centre.addWidget(self.btn_new)
        centre.addWidget(self.btn_treat)
        centre.addStretch(1)

        # right: task panel
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.addWidget(self.task_panel)

        def _vline() -> QFrame:
            f = QFrame()
            f.setFrameShape(QFrame.VLine)
            f.setStyleSheet(f"color: {_PALETTE['border']};")
            return f

        main = QHBoxLayout()
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(16)
        main.addLayout(left,   stretch=3)
        main.addWidget(_vline())
        main.addLayout(centre, stretch=2)
        main.addWidget(_vline())
        main.addLayout(right,  stretch=3)

        self.setLayout(main)

    def set_sprite(self, mood: str, alive: bool):
        species = self.species_box.currentText()
        self.pet_widget.set_mood(mood, species, alive)

    def set_bars(self, health: int, energy: int, happiness: int):
        self.health_bar.setValue(int(health))
        self.energy_bar.setValue(int(energy))
        self.happy_bar.setValue(int(happiness))

    def set_message(self, text: str):
        self.msg.setText(text)

    def set_inputs(self, name: str, species: str):
        self.name_input.setText(name)
        idx = self.species_box.findText(species)
        if idx >= 0:
            self.species_box.setCurrentIndex(idx)

    def set_treat_count(self, count: int):
        # update treat button label so player can see how many they have
        self.btn_treat.setText(f"🍬  Use Treat  (+25 energy)  [{count}]")
        self.btn_treat.setEnabled(count > 0 and True)

    def set_dead_mode(self, dead: bool):
        self.btn_focus_10.setEnabled(not dead)
        self.btn_focus_25.setEnabled(not dead)
        self.btn_sync.setEnabled(not dead)
        self.btn_treat.setEnabled(not dead)
        self.task_panel.set_form_enabled(not dead)

    def show_error(self, text: str):
        QMessageBox.critical(self, "Error", text)
