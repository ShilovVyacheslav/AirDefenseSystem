def calculate_targeting_time(predator, evader):
    h = evader.pos.y
    V_P = predator.speed
    v = evader.speed
    if V_P <= v:
        return float('inf')
    return V_P * h / (V_P**2 - v**2)
