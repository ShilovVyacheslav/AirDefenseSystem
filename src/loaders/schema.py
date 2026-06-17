class ScenarioError(ValueError):
    pass


_PREDATOR_FIELD_MAP = {"pos": "pos", "speed": "V_P", "V_P": "V_P"}
_EVADER_FIELD_MAP = {
    "pos": "pos",
    "speeds": "V_E", "V_E": "V_E",
    "center": "C_0", "C_0": "C_0",
    "radius": "D_0", "D_0": "D_0",
    "angles": "A_E", "A_E": "A_E",
    "height": "h", "h": "h",
    "speed": "v", "v": "v",
    "angle": "alpha", "alpha": "alpha",
    "phase": "beta", "beta": "beta",
}
_EVADER_ALLOWED = {
    "spiral": {"pos", "V_E", "v", "alpha"},
    "circular": {"C_0", "D_0", "V_E", "A_E", "v", "alpha", "beta"},
    "targeting": {"h", "v"},
}
_PREDATOR_ALLOWED = {
    "spiral": {"pos", "V_P"}, "circular": {"pos", "V_P"}, "targeting": {"V_P"},
}
_VALID_MODES = ("spiral", "circular", "targeting")

_VECTOR_FIELDS = {"pos", "C_0"}
_NUMBER_FIELDS = {"V_P", "D_0", "h", "v", "alpha", "beta"}
_LIST_FIELDS = {"V_E", "A_E"}
_POSITIVE_FIELDS = {"V_P", "D_0", "h"}


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _check_number(value, field, role, mode):
    if not _is_number(value):
        raise ScenarioError(
            f"{mode} {role}: field '{field}' must be a number, got {type(value).__name__}."
        )
    return float(value)


def _check_vector(value, field, role, mode):
    if not isinstance(value, (list, tuple)):
        raise ScenarioError(f"{mode} {role}: field '{field}' must be [x, y].")
    if len(value) != 2:
        raise ScenarioError(
            f"{mode} {role}: field '{field}' must have exactly 2 numbers, got {len(value)}."
        )
    for component in value:
        if not _is_number(component):
            raise ScenarioError(
                f"{mode} {role}: field '{field}' must contain numbers, "
                f"got {type(component).__name__}."
            )
    return tuple(float(c) for c in value)


def _check_number_list(value, field, role, mode):
    if not isinstance(value, (list, tuple)):
        raise ScenarioError(f"{mode} {role}: field '{field}' must be a list of numbers.")
    if len(value) == 0:
        raise ScenarioError(f"{mode} {role}: field '{field}' must not be empty.")
    out = []
    for element in value:
        if not _is_number(element):
            raise ScenarioError(
                f"{mode} {role}: field '{field}' must contain numbers, "
                f"got {type(element).__name__}."
            )
        out.append(float(element))
    return out


def _coerce_and_check(field, value, role, mode):
    if field in _VECTOR_FIELDS:
        return _check_vector(value, field, role, mode)
    if field in _NUMBER_FIELDS:
        number = _check_number(value, field, role, mode)
        if field in _POSITIVE_FIELDS and number <= 0:
            raise ScenarioError(f"{mode} {role}: field '{field}' must be positive.")
        return number
    if field in _LIST_FIELDS:
        numbers = _check_number_list(value, field, role, mode)
        if field == "V_E" and any(n <= 0 for n in numbers):
            raise ScenarioError(f"{mode} {role}: speeds in 'V_E' must be positive.")
        return numbers
    return value


def _normalize_entry(entry, field_map, allowed, role, mode):
    if not isinstance(entry, dict):
        raise ScenarioError(f"{mode} {role}: each entry must be a mapping.")
    result = {}
    seen = set()
    for raw_key, value in entry.items():
        if raw_key == "id":
            continue
        if raw_key not in field_map:
            raise ScenarioError(f"{mode} {role}: unknown field '{raw_key}'.")
        target = field_map[raw_key]
        if target in seen:
            raise ScenarioError(f"{mode} {role}: field '{target}' given twice.")
        if target not in allowed:
            raise ScenarioError(f"{mode} {role}: field '{raw_key}' is not valid in {mode} mode.")
        seen.add(target)
        result[target] = _coerce_and_check(target, value, role, mode)
    return result


def _evader_max_speed(evader, mode):
    if mode == "targeting":
        return evader["v"]
    return max(evader["V_E"])


def _validate_speeds(predators, evaders, mode):
    pred_speeds = sorted((p["V_P"] for p in predators), reverse=True)
    evad_max = sorted((_evader_max_speed(e, mode) for e in evaders), reverse=True)
    for i in range(min(len(pred_speeds), len(evad_max))):
        vp, ve = pred_speeds[i], evad_max[i]
        if not (vp > ve):
            raise ScenarioError(
                f"Speed feasibility failed at rank {i}: predator speed {vp:g} "
                f"is not strictly greater than evader max speed {ve:g} "
                f"(both ranked by descending speed). "
                f"Each ranked predator must outrun the matching ranked target."
            )


class ScenarioData:
    def __init__(self, mode, predator_entries, evader_entries):
        self.mode = mode
        self.predators = [
            _normalize_entry(e, _PREDATOR_FIELD_MAP, _PREDATOR_ALLOWED[mode], "predator", mode)
            for e in predator_entries
        ]
        self.evaders = [
            _normalize_entry(e, _EVADER_FIELD_MAP, _EVADER_ALLOWED[mode], "evader", mode)
            for e in evader_entries
        ]

        if len(self.predators) == 0:
            raise ScenarioError(f"{mode}: at least one predator is required.")
        if len(self.evaders) == 0:
            raise ScenarioError(f"{mode}: at least one evader is required.")
        if len(self.predators) != len(self.evaders):
            raise ScenarioError(
                f"{mode}: predator count ({len(self.predators)}) must equal evader "
                f"count ({len(self.evaders)}); the assignment matrix is square."
            )

        _validate_speeds(self.predators, self.evaders, mode)
