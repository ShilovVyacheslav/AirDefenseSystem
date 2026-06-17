from src.cli import parse_args
from src.core.simulation import Simulation

if __name__ == "__main__":
    Simulation(parse_args()).run()
