import random

class ConsoleIO:
    def get_user_input(self, attempt):
        while True:
            try:
                # 사용자 입력
                print(f"Attmept {attempt}: ", end ="")
                input_numbers = list(map(int, input().split()))

                # 3개 정수 입력 확인
                if (len(input_numbers) != 3):
                    print("Input 3 integers.")
                    continue

                # 1~9 사이의 정수 입력 확인
                if not all(1 <= x <= 9 for x in input_numbers) :
                    print("Input 1~9 integers.")
                    continue

                # 중복된 값 확인
                if (len(set(input_numbers)) != 3):
                    print("Input 3 different integers.")
                    continue
                
                return input_numbers

            # 정수 이외 값 예외 처리
            except ValueError:
                print("Input 3 different integers.")
                continue
                
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
        strike = 0
        ball = 0
        
        for i in range(3):
            if user_numbers[i] == self.computer_nubmers[i]:
                strike += 1
            elif user_numbers[i] in self.computer_nubmers:
                ball += 1
        
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