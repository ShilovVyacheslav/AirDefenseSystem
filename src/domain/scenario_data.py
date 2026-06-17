def entity_blocks(data):
    evaders = data.evaders if (data and hasattr(data, "evaders")) else []
    predators = data.predators if (data and hasattr(data, "predators")) else []
    return list(evaders), list(predators)


def block_at(blocks, index):
    return blocks[index] if index < len(blocks) else {}


def resolve_count(data, evaders, predators, default):
    if data:
        return max(len(evaders), len(predators))
    return default
