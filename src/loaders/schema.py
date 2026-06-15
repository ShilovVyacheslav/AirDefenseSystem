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


def _as_vector_fields(entry):
    out = dict(entry)
    for key in ("pos", "C_0"):
        if key in out and isinstance(out[key], (list, tuple)):
            out[key] = tuple(out[key])
    return out


def _normalize_entry(entry, field_map, allowed, role, mode):
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
        result[target] = value
    return _as_vector_fields(result)


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
