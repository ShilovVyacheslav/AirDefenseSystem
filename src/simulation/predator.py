from src.simulation.entity import Entity


class Predator(Entity):
    def __init__(self, pos, vel):
        super().__init__(pos, vel, radius_world=0.15, color=(90, 180, 240))
