import argparse
from dataclasses import dataclass

MODES = [
    "single_spiral", "multiple_spiral",
    "single_circular", "multiple_circular",
    "single_targeting", "multiple_targeting",
]


@dataclass(frozen=True)
class AppConfig:
    mode: str = "single_spiral"
    respawn: bool = False
    matrix: bool = True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gadci",
        description="Global Air Defense Command Interface simulation",
    )
    parser.add_argument(
        "-m", "--mode",
        choices=MODES,
        default=AppConfig.mode,
        metavar="MODE",
        help="Initial simulation mode (default: %(default)s)",
    )
    parser.add_argument(
        "--respawn",
        action="store_true",
        help="Auto-respawn entities after all interceptions",
    )
    parser.add_argument(
        "--no-matrix",
        dest="matrix",
        action="store_false",
        help="Disable the matrix overlay in 'multiple' modes",
    )
    return parser


def parse_args(argv=None) -> AppConfig:
    args = build_parser().parse_args(argv)
    return AppConfig(mode=args.mode, respawn=args.respawn, matrix=args.matrix)


def run() -> None:
    from src.core.simulation import Simulation
    Simulation(parse_args()).run()
