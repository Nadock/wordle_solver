import argparse

from . import __program__, __version__, constants


def parse_cli_args() -> argparse.Namespace:
    """Parse CLI arguments and return options as an `argparse.Namespace`."""
    parser = argparse.ArgumentParser(__program__)

    parser.add_argument(
        "--guess",
        "-g",
        action="append",
        default=[],
        dest="guesses",
        help=(
            "Add a word that has already been guessed, to solve an in-progress game. "
            "Combine with --result to include game feedback for guesses."
        ),
    )

    parser.add_argument(
        "--answer",
        "-a",
        action="append",
        default=[],
        dest="answers",
        help=(
            "Add the result for a guess from an in-progress game. Use "
            f"'{constants.CORRECT.symbol}' to represent a green letter, "
            f"'{constants.IN_WORD.symbol}' to represent a yellow letter, and "
            f"'{constants.INCORRECT.symbol}' to represent a grey letter."
        ),
    )

    parser.add_argument(
        "--hard-mode",
        action="store_true",
        default=False,
        help="Enable hard mode compatability",
    )

    parser.add_argument(
        "--disable-rich",
        action="store_true",
        default=False,
        help=(
            "Disables nice output formatting via Rich and falls back "
            "to plaintext terminal output"
        ),
    )

    parser.add_argument(
        "--suggest",
        "-s",
        action="store_true",
        default=False,
        help=(
            "Generate and output a single suggested word. (mutually "
            "exclusive with --remain/-r)"
        ),
    )

    parser.add_argument(
        "--remain",
        "-r",
        action="store_true",
        default=False,
        help=("List the remaining valid words. (mutually exclusive with --suggest/-s)"),
    )

    args = parser.parse_args()
    args.answers = [constants.Answer.from_string(answer) for answer in args.answers]

    if args.remain and args.suggest:
        raise ValueError("--suggest/-s and --remain/-r flags are mutually exclusive")

    return args
