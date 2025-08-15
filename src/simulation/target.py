from src.simulation.entity import Entity


class Target(Entity):
    def __init__(self, pos, vel):
        super().__init__(pos, vel, radius_world=0.2, color=(220, 90, 90))
