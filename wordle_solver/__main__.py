import sys

from . import cli, renderer


def main() -> None:
    """Parse CLI args and run wordle_solver"""
    args = cli.parse_cli_args()
    render = renderer.RichWordleRenderer(args)
    if args.remain:
        render.remaining()
    elif args.suggest:
        render.suggest()
    else:
        render.solve()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
