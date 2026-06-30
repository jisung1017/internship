from baseball import create_answer, is_correct, judge_guess


def main() -> None:
    answer = create_answer()
    print("숫자 야구 게임을 시작합니다. 중복 없는 3자리 숫자를 입력하세요.")

    while True:
        guess = input("guess> ")

        try:
            result = judge_guess(answer, guess)
        except ValueError as error:
            print(f"잘못된 입력입니다: {error}")
            continue

        print(f"{result.strikes} strike, {result.balls} ball")

        if is_correct(result):
            print("정답입니다!")
            break


if __name__ == "__main__":
    main()
