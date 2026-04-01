
# engine_bridge.py
# Created by Kali Banghart on 2/28/26.
#
# engine_bridge.py Calls the C++ engine binary via subprocess.
# Writes state_in.json, runs the binary, reads state_out.json back.

import json
import os
import subprocess
from time import time
from typing import Tuple

from storage import AppState

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _candidate_engine_paths():
    REPO = "/Users/kalibanghart/CLionProjects/M3OEP-kbanghar"
    return [
        os.path.join(REPO, "cmake-build-debug",  "M1AP"),
        os.path.join(REPO, "cmake-build-debug",  "M1AP", "pet_engine"),
        os.path.join(REPO, "cmake-build-release", "M1AP"),
        os.path.join(REPO, "build", "pet_engine"),
    ]


def resolve_engine_path():
    for p in _candidate_engine_paths():
        if os.path.exists(p):
            return os.path.abspath(p)
    return _candidate_engine_paths()[0]


def run_engine(state: AppState, work_points: int, engine_path=None) -> Tuple[AppState, str, str]:
    data_dir = os.path.join(BASE_DIR, "data")
    os.makedirs(data_dir, exist_ok=True)

    now     = int(time())
    elapsed = max(0, now - int(state.last_update_epoch))

    payload = {
        "name":              state.name,
        "species":           state.species,
        "health":            int(state.health),
        "energy":            int(state.energy),
        "happiness":         int(state.happiness),
        "streak":            int(state.streak),
        "evolution":         int(state.evolution),
        "alive":             bool(state.alive),
        "last_update_epoch": int(state.last_update_epoch),
        "seconds_elapsed":   int(elapsed),
        "work_points":       int(max(0, work_points)),
    }

    in_path  = os.path.join(data_dir, "state_in.json")
    out_path = os.path.join(data_dir, "state_out.json")

    with open(in_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    engine = engine_path or resolve_engine_path()

    if not os.path.exists(engine):
        tried = "\n  ".join(os.path.abspath(p) for p in _candidate_engine_paths())
        raise FileNotFoundError(
            f"C++ engine not found.\n\nTried:\n  {tried}\n\n"
            "Rebuild in CLion: Build menu -> Build Project"
        )

    result = subprocess.run(
        [engine, "--in", in_path, "--out", out_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"C++ engine crashed (code {result.returncode})\n"
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )

    with open(out_path, "r", encoding="utf-8") as f:
        out = json.load(f)

    new_state = AppState(
        name              = out.get("name",      state.name),
        species           = out.get("species",   state.species),
        health            = int(out.get("health",    state.health)),
        energy            = int(out.get("energy",    state.energy)),
        happiness         = int(out.get("happiness", state.happiness)),
        streak            = int(out.get("streak",    state.streak)),
        evolution         = int(out.get("evolution", state.evolution)),
        alive             = bool(out.get("alive",    state.alive)),
        last_update_epoch = now,
    )

    return new_state, out.get("mood_sprite", "idle"), out.get("message", "")