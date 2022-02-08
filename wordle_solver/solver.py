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
        guesses: list[str] | None = None,
        answers: list[constants.Answer] | None = None,
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

        word_scores = [(word, score) for word, score in self._score_words().items()]
        word_scores.sort(key=lambda ws: ws[1], reverse=True)
        return word_scores[0][0]

    def _score_words(self) -> dict[str, int]:
        """
        Score each remaining word according to how well it matches the existing guesses.
        """
        guesses = self.words if self.hard_mode else words.ALL_WORDS
        answers = self.words
        scores: dict[str, int] = {}

        for answer in answers:
            for guess in guesses:
                score = 0
                letters = []
                for idx, letter in enumerate(guess):
                    # duplicates=-1, green=5, yellow=3, grey=1
                    if letter in letters:
                        score += -1
                    if answer[idx] == letter:
                        score = 5
                    elif letter in answer:
                        score += 3
                    else:
                        score += 1
                    letters.append(letter)

                scores.setdefault(guess, 0)
                scores[guess] += score

        return scores

    def add_answer(self, *, guess: str, answer: constants.Answer) -> None:
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
