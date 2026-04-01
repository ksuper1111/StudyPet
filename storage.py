#
# storage.py
# Created by Kali Banghart on 2/28/26.
#
# storage.py Handles saving/loading pet state to JSON.

import json
import os
from dataclasses import dataclass, asdict, fields  # dataclass auto-generates __init__; asdict converts to dict; fields lists all field names
from time import time  # unix timestamp

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))  # folder this script lives in
DEFAULT_PATH = os.path.join(BASE_DIR, "data", "state.json")  # full path to the save file


@dataclass
class AppState:
    name:              str  = "KaliPet"
    species:           str  = "Cat"   # Cat, Dog, or Owl
    health:            int  = 80      # 0-100
    energy:            int  = 70      # 0-100
    happiness:         int  = 70      # 0-100
    streak:            int  = 0       # consecutive productive ticks
    evolution:         int  = 1       # stage 1-3
    alive:             bool = True
    last_update_epoch: int  = 0       # unix timestamp, Python sets this not C++


def _filter_keys(obj: dict) -> dict:
    allowed = {f.name for f in fields(AppState)}  # set of valid field names
    return {k: obj[k] for k in obj if k in allowed}  # drops keys so it doesnt crash on old things


def load_state(path: str = DEFAULT_PATH) -> AppState:
    if not os.path.exists(path):  # return defaults if no save file
        s = AppState()
        s.last_update_epoch = int(time())
        return s

    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except Exception:
        s = AppState()  # if the file is corupt it starts freash
        s.last_update_epoch = int(time())
        return s

    if not isinstance(obj, dict):  # root is a dict
        s = AppState()
        s.last_update_epoch = int(time())
        return s

    s = AppState(**_filter_keys(obj))  #  unpacks as a keyword argument (yhe dict)
    if s.last_update_epoch == 0:
        s.last_update_epoch = int(time())  # fix missing timestamp so elapsed calc works
    return s


def save_state(state: AppState, path: str = DEFAULT_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)  # create data/ if it doesn't exist
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(state), f, indent=2)  # asdict converts the dataclass to a plain dict