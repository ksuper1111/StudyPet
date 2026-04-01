#
# task_storage.py
# Created by Kali Banghart on 2/28/26.
#
# task_storage.py Manages the to-do list. Tasks saved to data/tasks.json.
# Overdue tasks penalize the pet on idle ticks.

import json
import os
import datetime
from dataclasses import dataclass, asdict
from time import time
from typing import Optional

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATH = os.path.join(BASE_DIR, "data", "tasks.json")

TASK_SIZES = {
    "Small  (+30)":  30,
    "Medium (+60)":  60,
    "Large  (+120)": 120,
}

OVERDUE_PENALTY = 15  # health damage per overdue task on idle ticks when not playing


@dataclass
class Task:
    id:          int
    title:       str
    points:      int             = 60
    deadline_ts: Optional[float] = None  # timestamp of the due date, or None
    done:        bool            = False
    done_ts:     Optional[float] = None  # set when completed, cleared after points are collected
    treats:      int             = 0     # treat currency earned on completion

    def is_overdue(self) -> bool:
        if self.done or self.deadline_ts is None:  # can't be overdue if already done or no deadline
            return False
        return time() > self.deadline_ts

    def deadline_label(self) -> str:
        if self.deadline_ts is None:
            return ""
        delta = datetime.datetime.fromtimestamp(self.deadline_ts) - datetime.datetime.now()
        secs  = delta.total_seconds()
        if secs < 0:     return "OVERDUE"
        if secs < 3600:  return f"{int(secs // 60)}m left"
        if secs < 86400: return f"{int(secs // 3600)}h left"
        return f"{int(secs // 86400)}d left"


class TaskList:
    def __init__(self, tasks=None):
        self._tasks   = tasks or []
        self._next_id = max((t.id for t in self._tasks), default=0) + 1
        # next unique id

    def add(self, title, points, deadline_ts=None):
        t = Task(id=self._next_id, title=title, points=points, deadline_ts=deadline_ts)
        self._next_id += 1
        self._tasks.append(t)
        return t

    def complete(self, task_id):
        for t in self._tasks:
            if t.id == task_id and not t.done:
                t.done    = True
                t.done_ts = time()
                # award treats based on task size: small=1, medium=2, large=3
                if   t.points >= 120: t.treats = 3
                elif t.points >= 60:  t.treats = 2
                else:                 t.treats = 1
                return t
        return None  # not found or already done

    def delete(self, task_id):
        before      = len(self._tasks)
        self._tasks = [t for t in self._tasks if t.id != task_id]
        return len(self._tasks) < before

    def clear_done(self):
        before      = len(self._tasks)
        self._tasks = [t for t in self._tasks if not t.done]
        return before - len(self._tasks)

    def all(self):     return list(self._tasks)
    def pending(self): return [t for t in self._tasks if not t.done]
    def overdue(self): return [t for t in self._tasks if t.is_overdue()]

    def pop_pending_points(self):
        total = sum(t.points for t in self._tasks if t.done and t.done_ts is not None)
        for t in self._tasks:
            if t.done:
                t.done_ts = None  # clear so points aren't counted again next tick
        return total

    def total_treats(self):
        return sum(t.treats for t in self._tasks if t.done and t.treats > 0)

    def spend_treat(self):
        for t in self._tasks:
            if t.done and t.treats > 0:
                t.treats -= 1
                return True
        return False  # no treats available

    def overdue_penalty(self):
        return len(self.overdue()) * OVERDUE_PENALTY

    def __len__(self):
        return len(self._tasks)


def _task_from_dict(d):
    return Task(
        id          = int(d.get("id", 0)),
        title       = str(d.get("title", "")),
        points      = int(d.get("points", 60)),
        deadline_ts = d.get("deadline_ts"),
        done        = bool(d.get("done", False)),
        done_ts     = d.get("done_ts"),
        treats      = int(d.get("treats", 0)),
    )


def load_tasks(path=DEFAULT_PATH):
    if not os.path.exists(path):
        return TaskList()
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):  # expects a JSON array at the root
            return TaskList()
        return TaskList([_task_from_dict(d) for d in raw if isinstance(d, dict)])
    except Exception:
        return TaskList()
        #start empty if file is correputed


def save_tasks(task_list, path=DEFAULT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(t) for t in task_list.all()], f, indent=2)