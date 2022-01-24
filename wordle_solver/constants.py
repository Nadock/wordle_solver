from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class AnswerPart:
    """
    An `AnswerPart` is the `symbol` used as input via the terminal and the `emoji` used
    in to render the gamestate.
    """

    symbol: str
    emoji: str


CORRECT = AnswerPart(symbol="Y", emoji="🟩")
IN_WORD = AnswerPart(symbol="I", emoji="🟨")
INCORRECT = AnswerPart(symbol="N", emoji="⬜")


@dataclasses.dataclass
class Answer:
    """
    An `Answer` is a set of five `AnswerParts` corresponding to the feedback for a
    single guess.
    """

    parts: list[AnswerPart]

    def __post_init__(self):
        if len(self.parts) != 5:
            raise ValueError(f"An {self.__class__.__name__} must have exactly 5 parts")

    @classmethod
    def from_string(cls, _input: str) -> Answer:
        """Convert a string of `AnswerPart` symbols into a single `Answer`."""
        _input = _input.upper().strip()
        if len(_input) != 5:
            raise ValueError(
                f"An {cls.__name__} can only be created from a string of length 5"
            )

        parts = []
        for letter in _input:
            if letter == CORRECT.symbol:
                parts.append(CORRECT)
            elif letter == IN_WORD.symbol:
                parts.append(IN_WORD)
            elif letter == INCORRECT.symbol:
                parts.append(INCORRECT)
            else:
                raise ValueError(f"'{letter}' is not a valid letter in input")

        return cls(parts=parts)
