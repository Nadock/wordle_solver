"""
A puzzle solver for the word game "Wordle"

https://www.powerlanguage.co.uk/wordle/
"""
import argparse
import enum
import pathlib
import random
import string
import sys


class SolverStart(enum.Enum):
    """The posible starting conditions for the Wordle Solver."""

    RANDOM = "random"
    BEST = "best"
    MANUAL = "manual"


class Solver:
    """
    Solver for a game of Wordle.

    Preload it with a list of possible words to use as guesses, then call the `play`
    function to run the process of solving a Wordle puzzle.
    """

    def __init__(self, *, words: list[str], start: SolverStart, show_all: bool = False):
        self.words = words
        self.guesses: list[str] = []
        self.results: list[list[bool | None]] = []
        self.start = start
        self.show_all = show_all

    def complete(self) -> str | None:
        """
        Check to see if the game is complete.

        A return value of `None` indicates the game is not complete, a `str` return
        value describes why the game is complete.
        """
        if len(self.results) == 6:
            return "Sorry, too many attempts without a result"
        if self.results and all(self.results[-1]):
            return "Congrats, that's the right answer"
        return None

    def random_guess(self) -> str:
        """Choose a random word from the remaining words as the next guess."""
        if not self.words:
            raise ValueError("No more words to choose from")
        if len(self.words) == 1:
            return self.words[0]
        return self.words[random.randint(0, len(self.words) - 1)]

    def best_guess(self) -> str:
        """
        Choose the "best" possible guess to reduce the search space most effectively.

        Currently the implementation selects a word with the most unique letters, of the
         words remaining.
        """
        scores = []
        for word in self.words:
            count: dict[str, int] = {}
            for letter in word:
                count.setdefault(letter, 0)
                count[letter] += 1
            scores.append((word, len(count)))
        scores.sort(key=lambda s: s[1], reverse=True)
        return scores[0][0]

    def first_guess(self) -> str:
        """
        Generate the first guess of the game, based on how to solver was configured.
        """
        if self.start == SolverStart.RANDOM:
            guess = self.random_guess()
        elif self.start == SolverStart.BEST:
            # https://old.reddit.com/r/wordle/comments/s2orah/finding_the_best_starting_word_using_a_brute/
            guess = "raise"
        elif self.start == SolverStart.MANUAL:
            guess = input("Input your first guess: ")
            guess = guess.strip().lower()
            while not guess or guess not in self.words:
                guess = input("Input your first guess: ")
        else:
            raise ValueError(f"{self.start} starts are not yet implemented")

        return guess

    def next_guess(self) -> str:
        """Generate the next guess for the current game of Wordle"""
        guess = None
        if not self.guesses:
            guess = self.first_guess()
        else:
            guess = self.best_guess()

        self.guesses.append(guess)
        return guess

    def filter_words(self, guess: str, result: list[bool | None]):
        """
        Based on a guess and the result of that guess, filter the remaining words to
        only those that are possible.
        """

        yellow_letters = {}
        for idx, _result in enumerate(result):
            if _result is None:
                yellow_letters[guess[idx]] = idx

        grey_letters: dict[str, int] = {}
        for idx, _result in enumerate(result):
            grey_letters.setdefault(guess[idx], 0)
            if _result is None or _result is True:
                grey_letters[guess[idx]] += 1

        remaining_words = []
        for word in self.words:
            good = word != guess

            # Green letters must be in the word at the same location
            for idx, _result in enumerate(result):
                if _result is True and word[idx] != guess[idx]:
                    good = False

            # Yellow letters must be in word, but not at the same location
            for letter, idx in yellow_letters.items():
                if letter not in word or word[idx] == letter:
                    good = False

            # Grey letters must not be in word unless offset by yellow letters
            for letter, count in grey_letters.items():
                if count == 0 and letter in word:
                    good = False

            if good:
                remaining_words.append(word)

        self.words = remaining_words

    def record_result(self, result: str) -> list[bool | None]:
        """Record an inputted result from the user."""
        if len(result) != 5 or result.lower().strip("yn?") != "":
            raise ValueError(f"{result} is not a valid result")

        converted_result: list[bool | None] = []
        for col in result.lower():
            if col == "y":
                converted_result.append(True)
            elif col == "n":
                converted_result.append(False)
            else:
                converted_result.append(None)

        self.results.append(converted_result)
        return converted_result

    def results_to_board(self) -> list[str]:
        """
        Convert the stored results to the emoji board Wordle uses to represent the
        gamestate.
        """
        board = []
        for result in self.results:
            result_str = ""
            for col in result:
                if col is True:
                    result_str += "🟩"
                elif col is False:
                    result_str += "⬜"
                else:
                    result_str += "🟨"
            board.append(result_str)
        return board

    def play(self):
        """Play a game of Wordle"""
        print(
            f"Welcome to wordle_solver, {len(self.words)} words loaded!",
            file=sys.stderr,
        )
        print("|  🟩 -> Y  |  ⬜ -> N  |  🟨 -> ?  |  New Guess -> R  |", file=sys.stderr)
        print("", file=sys.stderr)

        while not self.complete():
            guess = self.next_guess()

            while True:
                try:
                    result_input = input(f"Try '{guess}': ")
                    if result_input.strip().lower() == "r":
                        guess = self.next_guess()
                    else:
                        result = self.record_result(result_input)
                        break
                except ValueError as ex:

                    print(ex, file=sys.stderr)

            self.filter_words(guess, result)
            print("\n".join(self.results_to_board()), file=sys.stderr)
            print(f"{len(self.words)} remaining", file=sys.stderr)
            if self.show_all:
                all_str = ""
                for idx, word in enumerate(self.words):
                    if idx % 20 == 0 and idx != 0:
                        all_str += "\n"
                    all_str += word
                    if idx + 1 != len(self.words):
                        all_str += "\t"
                print(all_str)
            print("", file=sys.stderr)
        print(self.complete(), file=sys.stderr)


def count_letter(word: str, letter: str) -> int:
    """Count the number of times the `letter` appears in the given `word`."""
    count = 0
    for char in word:
        if char == letter:
            count += 1
    return count


def load_words(path: str) -> list[str]:
    """
    Load a words file and return the list of individual words.

    A words file must be a plaintext UTF-8 file with each new word delimited by a
    newline.

    Any words that aren't exactly 5 English characters in length are filtered out.
    """
    words_path = pathlib.Path(path)
    if not words_path.is_file():
        raise ValueError(f"{path} is not a file")

    words = words_path.read_text(encoding="utf-8").split("\n")

    # Clean duplicates, words that aren't 5 characters, and words that aren't all
    # ascii charaters
    five_letter_words = set()
    for word in words:
        word = word.strip().lower()
        if len(word) == 5 and not word.strip(string.ascii_lowercase):
            five_letter_words.add(word)

    return list(five_letter_words)


def do_argparse() -> argparse.Namespace:
    """Parse CLI arguments with `argparse`, returning the parsed options."""
    parser = argparse.ArgumentParser()

    parser.add_argument("words_file")
    parser.add_argument(
        "--start",
        default=SolverStart.RANDOM.value,
        choices=[s.value for s in SolverStart],
    )
    parser.add_argument("--show-all", default=False, action="store_true")

    return parser.parse_args()


def main():
    """Parse args and run the Wordle Solver."""
    args = do_argparse()

    solver = Solver(
        words=load_words(args.words_file),
        start=SolverStart(args.start),
        show_all=args.show_all,
    )
    solver.play()


if __name__ == "__main__":
    main()
