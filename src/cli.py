import argparse
from dataclasses import dataclass

from src import loaders
from src.core.modes import Mode

MODES = [m.value for m in Mode]
MODE_CHOICES = MODES + [str(i) for i in range(1, len(MODES) + 1)]

DEFAULT_MODE = Mode.SINGLE_SPIRAL.value


def _parse_mode(value: str) -> str:
    if value.isdigit():
        idx = int(value) - 1
        if 0 <= idx < len(MODES):
            return MODES[idx]
        raise argparse.ArgumentTypeError(f"Invalid mode index: {value}. Must be 1-{len(MODES)}")
    if value not in MODES:
        raise argparse.ArgumentTypeError(f"Invalid mode: {value}. Available: {', '.join(MODES)}")
    return value


@dataclass(frozen=True)
class AppConfig:
    mode: str = DEFAULT_MODE
    respawn: bool = False
    matrix: bool = True
    preview: bool = True
    random: bool = False
    count: int | None = None
    scenario_path: str | None = None


class _ScenariosInfo(argparse.Action):
    def __init__(self, option_strings, dest, **kw):
        super().__init__(option_strings, dest, nargs=0, **kw)

    def __call__(self, parser, ns, values, option_string=None):
        print(loaders.read_reference())
        parser.exit()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ads",
        description="Air-defense optimal-pursuit simulation.",
        epilog=(
            "World source is one of: --scenario (from file), --random "
            "(procedural), or neither (default scenario for the mode). "
            "--mode/--count/--random cannot be combined with --scenario."
        ),
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "-s", "--scenario", metavar="PATH", dest="scenario_path",
        help="Load setup from a .json/.yaml file (sets mode and count from the file).",
    )
    source.add_argument(
        "-r", "--random", action="store_true",
        help="Procedural random setup. Not allowed with --scenario.",
    )

    mode_help_lines = []
    for i, mode in enumerate(MODES, 1):
        mode_help_lines.append(f"  {i}: {mode}")
    mode_help = "Simulation mode. Can be specified as name or number (1-6):\n" + "\n".join(mode_help_lines)
    mode_help += f"\n(default: {DEFAULT_MODE})"

    parser.add_argument(
        "-m", "--mode", type=_parse_mode, choices=MODE_CHOICES, default=None, metavar="MODE",
        help=mode_help,
    )
    parser.add_argument(
        "-c", "--count", type=int, default=None, metavar="N",
        help="Entity count for 'multiple' modes.",
    )

    parser.add_argument(
        "--respawn", action="store_true",
        help="Auto-respawn entities after all interceptions.",
    )
    parser.add_argument(
        "--no-matrix", dest="matrix", action="store_false",
        help="Disable the pursuit-matrix overlay in 'multiple' modes.",
    )
    parser.add_argument(
        "--no-preview", dest="preview", action="store_false",
        help="Skip the boot/loading intro.",
    )

    parser.add_argument(
        "--scenario-info", action=_ScenariosInfo,
        help="Print the scenario-file reference and exit.",
    )
    return parser


def _validate(parser, args) -> None:
    if args.scenario_path is not None:
        offenders = []
        if args.mode is not None:
            offenders.append("--mode")
        if args.count is not None:
            offenders.append("--count")
        if offenders:
            joined = ", ".join(offenders)
            parser.error(
                f"{joined} cannot be combined with --scenario; "
                f"the scenario file defines the mode and entity count."
            )

    if args.count is not None and args.count < 1:
        parser.error("--count must be a positive integer.")


def parse_args(argv=None) -> AppConfig:
    parser = build_parser()
    args = parser.parse_args(argv)
    _validate(parser, args)

    return AppConfig(
        mode=args.mode if args.mode is not None else DEFAULT_MODE,
        respawn=args.respawn,
        matrix=args.matrix,
        preview=args.preview,
        random=args.random,
        count=args.count,
        scenario_path=args.scenario_path,
    )


def run() -> None:
    from src.core.simulation import Simulation
    Simulation(parse_args()).run()
