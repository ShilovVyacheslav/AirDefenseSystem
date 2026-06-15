def single_blocks(data):
    evader = data.evader if data and hasattr(data, "evader") else {}
    predator = data.predator if data and hasattr(data, "predator") else {}
    return evader, predator


def multiple_blocks(data):
    evaders = data.evaders if (data and hasattr(data, "evaders")) else {}
    predators = data.predators if (data and hasattr(data, "predators")) else {}
    return evaders, predators


def resolve_count(data, evaders_data, predators_data, default):
    if data:
        return max(len(evaders_data), len(predators_data))
    return default
