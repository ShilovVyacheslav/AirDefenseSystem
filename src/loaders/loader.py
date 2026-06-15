import json
import os

from src.loaders.schema import ScenarioData, ScenarioError, _VALID_MODES

_REFERENCE_FILENAME = "_scenarios.txt"
_SCENARIO_EXTENSIONS = (".yaml", ".yml", ".json")


def _scenarios_dir() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(here))
    return os.path.join(project_root, "scenarios")


def _read_raw(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8") as f:
        if ext == ".json":
            return json.load(f)
        if ext in (".yaml", ".yml"):
            try:
                import yaml
            except ImportError as exc:
                raise ScenarioError(
                    "PyYAML is required to read .yaml scenarios "
                    "(pip install pyyaml), or use the .json file instead."
                ) from exc
            return yaml.safe_load(f)
        raise ScenarioError(
            f"Unsupported scenario extension '{ext}'. Use .json, .yaml or .yml."
        )


def load_scenario(path: str) -> ScenarioData:
    if not os.path.isfile(path):
        raise ScenarioError(f"Scenario file not found: {path}")

    raw = _read_raw(path)
    if not isinstance(raw, dict):
        raise ScenarioError("Scenario root must be a mapping with a 'mode' key.")

    mode = raw.get("mode")
    if mode is None:
        raise ScenarioError("Scenario is missing the required 'mode' field.")
    if mode not in _VALID_MODES:
        raise ScenarioError(
            f"Unknown mode '{mode}'. Expected one of: {', '.join(_VALID_MODES)}."
        )

    predators = raw.get("predators", []) or []
    evaders = raw.get("evaders", []) or []

    return ScenarioData(mode, predators, evaders)


def load_default(scenario: str) -> ScenarioData | None:
    for ext in _SCENARIO_EXTENSIONS:
        path = os.path.join(_scenarios_dir(), scenario + ext)
        if os.path.isfile(path):
            return load_scenario(path)
    return None


def read_reference() -> str:
    path = os.path.join(_scenarios_dir(), _REFERENCE_FILENAME)
    if not os.path.isfile(path):
        return f"Scenario reference not found at {path}."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def mode_from_scenario(data) -> str:
    multi = len(data.predators) > 1 or len(data.evaders) > 1
    prefix = "multiple" if multi else "single"
    return f"{prefix}_{data.mode}"
