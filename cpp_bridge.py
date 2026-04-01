#
# cpp_bridge.py
# Created by Kali Banghart on 2/28/26.
#
# cpp_bridge.py  replaced by engine_bridge.py.
# keeping this just in case

import json
import os
import subprocess
from time import time
from storage import AppState

ENGINE_PATH_DEFAULT = os.path.join("build", "pet_engine")


def run_engine(state: AppState, work_points: int, engine_path: str = ENGINE_PATH_DEFAULT):
    os.makedirs("data", exist_ok=True)

    now     = int(time())
    elapsed = max(0, now - int(state.last_update_epoch))

    payload = {
        "name":              state.name,
        "species":           state.species,
        "health":            state.health,
        "energy":            state.energy,
        "happiness":         state.happiness,
        "streak":            state.streak,
        "evolution":         state.evolution,
        "alive":             state.alive,
        "last_update_epoch": now,
        "seconds_elapsed":   elapsed,
        "work_points":       int(max(0, work_points)),
    }

    in_path  = os.path.join("data", "state_in.json")
    out_path = os.path.join("data", "state_out.json")

    with open(in_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)

    if not os.path.exists(engine_path):
        raise FileNotFoundError(f"Engine not found at {engine_path}. Build it first.")

    res = subprocess.run(
        [engine_path, "--in", in_path, "--out", out_path],
        capture_output=True, text=True
    )

    if res.returncode != 0:
        raise RuntimeError(f"Engine failed (code {res.returncode}).\n{res.stdout}\n{res.stderr}")

    with open(out_path, "r", encoding="utf-8") as f:
        out = json.load(f)

    new_state = AppState(
        name              = out["name"],
        species           = out["species"],
        health            = int(out["health"]),
        energy            = int(out["energy"]),
        happiness         = int(out["happiness"]),
        streak            = int(out["streak"]),
        evolution         = int(out["evolution"]),
        alive             = bool(out["alive"]),
        last_update_epoch = now,
    )

    return new_state, out.get("mood_sprite", "idle"), out.get("message", "")