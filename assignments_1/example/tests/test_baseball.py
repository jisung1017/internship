import unittest

from assignments_1.example.baseball import (
    validate_number,
    judge_guess,
    is_correct,
    GuessResult,
)


class NumberBaseballTest(unittest.TestCase):
    def test_validate_number_accepts_three_unique_digits(self):
        self.assertEqual(validate_number("123"), "123")

    def test_validate_number_rejects_invalid_numbers(self):
        for number in ["12", "1234", "12a", "112"]:
            with self.subTest(number=number):
                with self.assertRaises(ValueError):
                    validate_number(number)

    def test_judge_guess_counts_strikes_and_balls(self):
        # 핵심 로직: 같은 숫자가 같은 위치면 strike, 다른 위치면 ball이다.
        self.assertEqual(judge_guess("427", "472"), GuessResult(strikes=1, balls=2))

    def test_judge_guess_counts_out_when_no_digit_matches(self):
        # 핵심 로직: 포함된 숫자가 하나도 없으면 strike와 ball이 모두 0이다.
        self.assertEqual(judge_guess("123", "456"), GuessResult(strikes=0, balls=0))

    def test_is_correct_when_all_digits_are_strikes(self):
        # 핵심 로직: 3 strike가 게임의 성공 조건이다.
        self.assertTrue(is_correct(GuessResult(strikes=3, balls=0)))
        self.assertFalse(is_correct(GuessResult(strikes=2, balls=1)))


if __name__ == "__main__":
    unittest.main()
