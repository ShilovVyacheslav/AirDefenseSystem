import argparse
from dataclasses import dataclass

from src import loaders

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
    scenario_path: str | None = None


class _ScenariosInfo(argparse.Action):
    def __init__(self, option_strings, dest, **kw):
        super().__init__(option_strings, dest, nargs=0, **kw)

    def __call__(self, parser, ns, values, option_string=None):
        print(loaders.read_reference())
        parser.exit()


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
    parser.add_argument(
        "--scenario", metavar="PATH",
        help="Load a scenario from a .json/.yaml file (sets mode and single/multi automatically).",
    )
    parser.add_argument(
        "--scenarios-info", action=_ScenariosInfo,
        help="Print the scenario file reference and exit.",
    )
    return parser


def parse_args(argv=None) -> AppConfig:
    args = build_parser().parse_args(argv)
    return AppConfig(
        mode=args.mode,
        respawn=args.respawn,
        matrix=args.matrix,
        scenario_path=args.scenario,
    )


def run() -> None:
    from src.core.simulation import Simulation
    Simulation(parse_args()).run()
