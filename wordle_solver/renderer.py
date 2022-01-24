import argparse
import dataclasses
from typing import Callable

from rich import console, panel, table

from . import constants, solver, version


@dataclasses.dataclass
class _Action:
    symbol: str
    label: str
    action: Callable[[], bool]


class RichWordleRenderer:
    """Mangage user I/O via the terminal with formatting via `rich`."""

    def __init__(self, args: argparse.Namespace):
        self.solver = solver.WordleSolver(
            guesses=args.guesses, answers=args.answers, hard_mode=args.hard_mode
        )
        self.console = console.Console()
        self.error_console = console.Console(stderr=True, style="bold red")
        self.actions = [
            _Action("S", "Suggestion", self._action_suggestion),
            _Action("R", "Remaining Words", self._action_remaining_words),
            _Action("G", "Add Guess", self._action_guess),
            _Action("Q", "Quit", self._action_quit),
        ]

    def solve(self) -> None:
        """Run the solver until the game is complete."""
        if not self.console.is_interactive:
            self.error_console.print(
                f"{version.__program__} is running in interactive mode"
            )
            return

        self._render_header()
        dirty = True

        while not self.solver.is_complete():
            if dirty:
                self._render_gamestate()

            action = self._prompt_action()
            if action:
                dirty = action.action()
                self.console.print()

        self._render_endgame()

    def remaining(self) -> None:
        """Display the remaining words."""
        if not self.console.is_interactive:
            self.console.print("\n".join(self.solver.words))
        else:
            self.console.print(*self.solver.words)

    def suggest(self) -> None:
        """Suggest one word as a guess."""
        guess = self.solver.next_word()
        if not self.console.is_interactive:
            self.console.print(guess)
        else:
            self.console.print(f"Try '[bold yellow]{guess}[/bold yellow]'")

    def _render_header(self) -> None:
        """Render the header message to the console."""
        _table = table.Table.grid()
        _table.add_column(justify="center")
        _table.add_row(f"{version.__program__} (v{version.__version__})")
        _table.add_row(
            (
                f"| {constants.CORRECT.emoji} -> {constants.CORRECT.symbol} | "
                f"{constants.IN_WORD.emoji} -> {constants.IN_WORD.symbol} | "
                f"{constants.INCORRECT.emoji} -> {constants.INCORRECT.symbol} |"
            )
        )
        _table.add_row(
            "| "
            + " | ".join(
                [f"{action.symbol}: {action.label}" for action in self.actions]
            )
            + " |"
        )

        self.console.print(_table)
        self.console.print()

    def _render_gamestate(self) -> None:
        """Render the current gamestate to the console"""
        if not self.solver.guesses:
            return

        _table = table.Table.grid()
        _table.add_column(justify="left")
        _table.add_column(justify="center")
        _table.add_column(justify="right")

        for guess, answer in zip(self.solver.guesses, self.solver.answers):
            guess_table = table.Table.grid()
            guess_table.add_row(*[p.emoji for p in answer.parts])
            _table.add_row(guess_table, " | ", guess)

        self.console.print(
            panel.Panel(
                _table, expand=False, subtitle=f"{len(self.solver.words)} Remaining"
            )
        )
        self.console.print()

    def _render_endgame(self) -> None:
        """Render the end of game message to the console."""
        self._render_gamestate()
        if len(self.solver.guesses) == 6:
            self.console.print("Maximum guesses exceeded")
        if len(self.solver.words) == 1:
            self.console.print(
                f"The answer is '[bold green]{self.solver.words[0]}[/bold green]'"
            )
        if not self.solver.words:
            self.console.print("No valid words remain, check your guesses and answers")

    def _prompt_action(self) -> _Action | None:
        """Prompt the user for an action."""
        user_action = self.console.input("> ").strip().upper()
        for action in self.actions:
            if action.symbol == user_action:
                return action
        return None

    def _prompt_guess(self) -> str | None:
        """Prompt the user for a word guess."""
        guess = self.console.input("guess: ")
        if self.solver.valid_guess(guess):
            return guess

        self.console.print(f"'[bold red]{guess}[/bold red]' is not a valid guess")
        return None

    def _prompt_answer(self) -> constants.Answer | None:
        """Prompt the user for an answer for a guess."""
        answer = self.console.input("answer: ")
        try:
            return constants.Answer.from_string(answer)
        except ValueError:
            self.console.print(f"'[bold red]{answer}[/bold red]' is not a valid answer")
            return None

    def _action_suggestion(self) -> bool:
        """Suggestion action."""
        guess = self.solver.next_word()
        self.console.print(f"Try '[bold yellow]{guess}[/bold yellow]'")

        answer = self._prompt_answer()
        if not answer:
            return False

        return self._guess(guess, answer)

    def _action_remaining_words(self) -> bool:
        """Remaining words action"""
        self.console.print(*self.solver.words)
        return False

    def _action_guess(self) -> bool:
        """Add guess action"""
        guess = self._prompt_guess()
        if not guess:
            return False

        answer = self._prompt_answer()
        if not answer:
            return False

        return self._guess(guess=guess, answer=answer)

    def _action_quit(self) -> bool:  # pylint: disable=no-self-use
        """Quit action"""
        raise KeyboardInterrupt

    def _guess(self, guess: str | None, answer: constants.Answer | None) -> bool:
        """Record a user's guess and it's corresponding answer."""
        if guess and answer:
            self.solver.add_answer(guess=guess, answer=answer)
        return bool(guess) and bool(answer)
