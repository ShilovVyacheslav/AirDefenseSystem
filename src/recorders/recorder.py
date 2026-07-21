import datetime
import json
import os

from src.core.modes import Mode
from src.domain.entities.predator import Predator

_CIRCULAR_MODES = (Mode.SINGLE_CIRCULAR, Mode.MULTIPLE_CIRCULAR)


def _output_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(here))
    return os.path.join(project_root, "output")


def _entity_id(entity) -> str:
    prefix = "P" if isinstance(entity, Predator) else "E"
    return f"{prefix}-{entity.track_id}"


def _serialize_setup_entity(entity, mode) -> dict:
    data = {
        "id": _entity_id(entity),
        "pos": [round(float(entity.pos.x), 6), round(float(entity.pos.y), 6)],
        "speed": round(float(entity.speed), 6),
    }
    if not isinstance(entity, Predator):
        data["V_E"] = [round(float(v), 6) for v in entity.V_E]
        data["A_E"] = [round(float(a), 6) for a in entity.A_E]
        if mode in _CIRCULAR_MODES:
            data["C_0"] = [round(float(entity.C_0.x), 6), round(float(entity.C_0.y), 6)]
            data["D_0"] = round(float(entity.D_0), 6)
    return data


class Recorder:

    def __init__(self, mode, source: str, scenario_path, operation_time: float, interval: float):
        self.mode = mode
        self.source = source
        self.scenario_path = scenario_path
        self.operation_time = operation_time
        self.interval = max(interval, 1e-6)

        self.initial_predators = []
        self.initial_evaders = []
        self.assignment = {}
        self.trajectory: dict[str, list] = {}

        self._next_sample_t = 0.0
        self.completed = False
        self._finalized = False

    def is_finalized(self) -> bool:
        return self._finalized

    def capture_initial(self, entity_manager) -> None:
        self.initial_predators = [_serialize_setup_entity(p, self.mode) for p in entity_manager.predators]
        self.initial_evaders = [_serialize_setup_entity(e, self.mode) for e in entity_manager.evaders]
        self.assignment = {
            _entity_id(evader): _entity_id(predator)
            for evader, predator in entity_manager.assignments.items()
        }
        self.trajectory = {}
        for predator in entity_manager.predators:
            self.trajectory[_entity_id(predator)] = []
        for evader in entity_manager.evaders:
            self.trajectory[_entity_id(evader)] = []

        self._next_sample_t = 0.0
        self._sample(0.0, entity_manager.assignments)
        self._next_sample_t += self.interval

    def sample(self, timer: float, assignments) -> None:
        if self._finalized or timer + 1e-9 < self._next_sample_t:
            return
        self._sample(timer, assignments)
        self._next_sample_t += self.interval

    def _sample(self, timer, assignments) -> None:
        for evader, predator in assignments.items():
            self._append(predator, timer)
            self._append(evader, timer)

    def _append(self, entity, timer) -> None:
        bucket = self.trajectory.get(_entity_id(entity))
        if bucket is not None:
            bucket.append([round(timer, 6), round(float(entity.pos.x), 6), round(float(entity.pos.y), 6)])

    def finalize(self, completed: bool) -> None:
        if self._finalized:
            return
        self.completed = completed
        self._finalized = True

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "source": self.source,
            "scenario_path": self.scenario_path,
            "entity_count": len(self.initial_predators),
            "completed": self.completed,
            "operation_time": round(self.operation_time, 6),
            "sample_interval": self.interval,
            "initial_setup": {
                "predators": self.initial_predators,
                "evaders": self.initial_evaders,
            },
            "assignment": self.assignment,
            "trajectory": self.trajectory,
        }

    def save(self, name: str | None) -> str:
        output_dir = _output_dir()
        os.makedirs(output_dir, exist_ok=True)
        filename = self._build_filename(name)
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, separators=(",", ":"))
        return path

    def _build_filename(self, name: str | None) -> str:
        if name:
            base = name
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base = f"{self.mode.value}_{self.source}_{len(self.initial_predators)}_{timestamp}"
        if base.lower().endswith(".json"):
            base = base[:-5]
        return base + ".json"
