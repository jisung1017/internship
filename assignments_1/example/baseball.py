from dataclasses import dataclass
from random import sample


NUMBER_LENGTH = 3


@dataclass(frozen=True)
class GuessResult:
    strikes: int
    balls: int


def validate_number(number: str) -> str:
    if len(number) != NUMBER_LENGTH:
        raise ValueError("number must be exactly 3 digits")

    if not number.isdigit():
        raise ValueError("number must contain only digits")

    if len(set(number)) != NUMBER_LENGTH:
        raise ValueError("number must not contain duplicate digits")

    return number


def judge_guess(answer: str, guess: str) -> GuessResult:
    answer = validate_number(answer)
    guess = validate_number(guess)

    # 핵심 로직: 같은 위치의 같은 숫자는 strike다.
    strikes = sum(
        answer_digit == guess_digit
        for answer_digit, guess_digit in zip(answer, guess, strict=True)
    )

    # 핵심 로직: 포함은 되지만 위치가 다르면 ball이다.
    matched_digits = len(set(answer) & set(guess))
    balls = matched_digits - strikes

    return GuessResult(strikes=strikes, balls=balls)


def is_correct(result: GuessResult) -> bool:
    # 핵심 로직: 모든 자리가 strike면 정답이다.
    return result.strikes == NUMBER_LENGTH


def create_answer() -> str:
    return "".join(sample("0123456789", NUMBER_LENGTH))
