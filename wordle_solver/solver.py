from . import constants, words


class WordleSolver:
    """
    Implementation to solve a Wordle game.

    Initial `guesses` and `answers` can be supplied to solve an in-progress game.

    Setting `hard_mode` to `True` enables compatibility with the hard mode rules (ie:
    subsequent guesses must use all previously revealed letters).
    """

    def __init__(
        self,
        guesses: list[str] = None,
        answers: list[constants.Answer] = None,
        hard_mode: bool = False,
    ):
        self.words = words.ALL_WORDS.copy()
        self.guesses: list[str] = []
        self.answers: list[constants.Answer] = []
        self.hard_mode = hard_mode

        answers = answers or []
        guesses = guesses or []

        if len(answers) != len(guesses):
            raise ValueError(
                f"Number of guesses ({len(guesses)}) must match "
                f"number of answers ({len(answers)})"
            )
        for guess, answer in zip(guesses, answers, strict=True):
            self.add_answer(guess=guess, answer=answer)

    def is_complete(self) -> bool:
        """Returns `True` if the Wordle game is complete."""
        return len(self.words) <= 1 or len(self.guesses) == 6

    def valid_guess(self, word: str) -> bool:
        """Check if a supplied `word` would be a valid guess for the current game."""
        if word in self.guesses:
            return False
        if self.hard_mode:
            return word in self.words
        return word in words.ALL_WORDS

    def next_word(self) -> str:
        """Return a suggested next word to guess."""
        letter_counts: dict[str, int] = {}
        for word in self.words:
            for letter in set(word):
                letter_counts.setdefault(letter, 0)
                letter_counts[letter] += 1

        max_score = -1
        max_word = self.words[0]
        search_words = self.words if self.hard_mode else words.ALL_WORDS
        for word in search_words:
            score = 0
            for letter in set(word):
                score += letter_counts.get(letter, 0)
            if score > max_score:
                max_score = score
                max_word = word

        return max_word

    def add_answer(self, *, guess: str, answer: constants.Answer):
        """Add an `guess` and `answer` combination to the current game."""
        if len(guess) != 5:
            raise ValueError("Guesses must be 5 letters long")
        if not self.valid_guess(guess):
            raise ValueError(f"'{guess}' is not a valid word")

        self.guesses.append(guess)
        self.answers.append(answer)
        self.words = self.filter_words(guess, answer)

    def filter_words(self, guess: str, answer: constants.Answer) -> list[str]:
        """Filter the current words list based on the `answer` for a `guess`."""
        new_words = []
        for word in self.words:
            match = word != guess
            for idx, (letter, part) in enumerate(zip(guess, answer.parts)):
                if part == constants.CORRECT:
                    if word[idx] != letter:
                        match = False
                if part == constants.IN_WORD:
                    if word[idx] == letter or letter not in word:
                        match = False
                if part == constants.INCORRECT:
                    if letter in word:
                        match = False
            if match:
                new_words.append(word)
        return new_words
