# Wordle Solver

A simple solver script for [Wordle](https://www.powerlanguage.co.uk/wordle/).

## Usage

```bash
python ./wordle_solver.py ./words.txt
```

## Input Mapping

Inputs are case insensitive so `Y` or `y` will both work.

| Wordle | `wordle_solver` | Hint                                   |
| ------ | --------------- | -------------------------------------- |
| 🟩      | `Y`             | **Y**es it's right                     |
| ⬜ or ⬛ | `N`             | **N**o it's not in the word            |
| 🟨      | `?`             | Maybe **?** it's somewhere in the word |

Input `R` if the generated guess was rejected by Wordle.
