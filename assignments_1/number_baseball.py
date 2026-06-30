import random

class ConsoleIO:
    def validate_input(self, input_numbers):
        # 3개 정수 입력 확인
        if len(input_numbers) != 3:
            raise ValueError("3개의 숫자를 입력해야 합니다.")
        # 1~9 사이의 정수 입력 확인
        if not all(1 <= x <= 9 for x in input_numbers):
            raise ValueError("1부터 9 사이의 숫자여야 합니다.")
        # 중복된 값 확인
        if len(set(input_numbers)) != 3:
            raise ValueError("중복된 숫자는 입력할 수 없습니다.")

    def get_user_input(self, attempt):
       while True:
            try:
                # 사용자 입력
                print(f"Attempt {attempt}: ", end ="")
                input_numbers = list(map(int, input().split()))

                self.validate_input(input_numbers)

                return input_numbers

            
            # 정수 이외 값 예외 처리
            except ValueError as e:
                print(f"[오류] {e} 다시 입력해주세요.")
            
                
    def print_result(self, result):
        # 판정 결과 출력
        print(result)
            
    def print_win(self, answer, attempt):
        # 승리 결과 출력
        print("You Win!")
        print("Answer =", *answer, f", attempt = {attempt}")

    def print_defeat(self, answer, attempt):
        # 패배 결과 출력
        print("You Defeat...")
        print("Answer =", *answer, f", attempt = {attempt}")

    
class GameDomain:
    def __init__(self, n1, n2, n3):
        self.computer_nubmers = [n1, n2, n3]

    # 판정 로직
    def decision(self, user_numbers):
        # 스트라이크 계산
        strike = sum(1 for x, y in zip(self.computer_nubmers, user_numbers) if x == y)
        # 자리 상관없이 총 맞은 개수
        total = len(set(self.computer_nubmers) & set(user_numbers))
        # 총 개수 - 스트라이크 = 볼의 개수
        ball = total - strike
        
        if strike == 0 and ball == 0:
            return "OUT"
        
        result = ""
        if strike > 0:
            result += f'{strike}S'
        
        if strike > 0 and ball > 0:
            result += " "

        if ball > 0:
            result += f'{ball}B'

        return result
        


def main() :
    answer = random.sample(range(1, 10), 3)
    game = GameDomain(*answer)

    io = ConsoleIO()

    attempt = 0
    while (attempt < 7):
        attempt += 1

        u1, u2, u3 = io.get_user_input(attempt)

        result = game.decision([u1, u2, u3])

        # 판정 결과 출력
        io.print_result(result)

        # 승리 조건
        if result == "3S":
            io.print_win(answer, attempt)
            break

    else:
        # 패배 조건 
        io.print_defeat(answer, attempt)


if __name__ == '__main__':
    main()