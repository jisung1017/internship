import pytest
from unittest.mock import patch
from number_baseball import ConsoleIO, GameDomain, InputValidator, main


@pytest.fixture
def console():
    return ConsoleIO()

@pytest.fixture
def validator():
    return InputValidator()

# 통합 테스트
@patch("random.sample", return_value=[1,2,3])
@patch("builtins.input", return_value="1 2 3")
def test_game_flow(mock_input, mock_random, capsys):

    main()

    captured = capsys.readouterr()

    assert "3S" in captured.out
    assert "You Win!" in captured.out

# 0. 올바른 사용자 입력 테스트
@patch('builtins.input', return_value = "1 2 3")
def test_get_user_input_valid(mock_input, console):
    result = console.get_user_input(attempt=1)

    assert result == [1, 2, 3]

# 1. 중복 에러 테스트
def test_get_user_input_duplicate_error(validator):
    invalid_input = [1, 1, 2]
    
    with pytest.raises(ValueError) as excinfo:
        validator.validate_input(invalid_input)
    assert str(excinfo.value) == "중복된 숫자는 입력할 수 없습니다."


# 2. 범위 초과 에러 테스트
def test_get_user_input_out_of_range(validator):
    invalid_input = [0, 13, -7]
    
    with pytest.raises(ValueError) as excinfo:
        validator.validate_input(invalid_input)
    assert str(excinfo.value) == "1부터 9 사이의 숫자여야 합니다."


# 3. 글자 수가 너무 많을 때 테스트
def test_get_user_input_more_length_error(validator):
    invalid_input = [1, 2, 3, 4]
    
    with pytest.raises(ValueError) as excinfo:
        validator.validate_input(invalid_input)
    assert str(excinfo.value) == "3개의 숫자를 입력해야 합니다."


# 4. 글자 수가 부족할 때 테스트
def test_get_user_input_less_length_error(validator):
    invalid_input = [1, 2]
    
    with pytest.raises(ValueError) as excinfo:
        validator.validate_input(invalid_input)
    assert str(excinfo.value) == "3개의 숫자를 입력해야 합니다."

# 5. 문자열 입력 시 재입력 흐름 테스트
@patch('builtins.input', side_effect=["abc 2 3", "1 2 3"])
def test_get_user_input_string_error(mock_input, console):
    result = console.get_user_input(attempt=1)
    assert result == [1, 2, 3]  
    assert mock_input.call_count == 2  

# 6. 소수점 입력 시 재입력 흐름 테스트
@patch('builtins.input', side_effect=["1.4 2 3", "1 2 3"])
def test_get_user_input_float_error(mock_input, console):
    result = console.get_user_input(attempt=1)
    assert result == [1, 2, 3]
    assert mock_input.call_count == 2


# 7. 판단 테스트
@pytest.mark.parametrize("computer, user, expected", [
    ([1,2,3], [1,2,3], "3S"),
    ([1,2,3], [4,5,6], "OUT"),
    ([1,2,3], [1,2,9], "2S"),
    ([1,2,3], [1,8,9], "1S"),
    ([1,2,3], [2,3,1], "3B"),
    ([1,2,3], [2,1,5], "2B"),
    ([1,2,3], [1,3,6], "1S 1B")
])
def test_decision_logic(computer, user, expected):
    game = GameDomain(*computer)

    result = game.decision(user)

    assert result == expected

# 8. 시도횟수 초과 실패 테스트 (attempt = 7)
@patch('random.sample', return_value = [7,8,9])
@patch('builtins.input', side_effect = ["1 2 3", "1 2 4", "1 2 5", "1 2 6", "1 2 7", "1 2 8", "1 2 9"])
def test_game_over_after_7_attempts(mock_input, mock_random, capsys):
    main()

    captured = capsys.readouterr()

    assert "You Defeat..." in captured.out
    assert "attempt = 7" in captured.out

# 9. 성공 테스트 (attempt = 3)
@patch('random.sample', return_value = [7,8,9])
@patch('builtins.input', side_effect = ["1 2 3", "1 2 4", "7 8 9"])
def test_game_win_at_3_attempts(mock_input, mock_random, capsys):
    main()

    captured = capsys.readouterr()

    assert "You Win!" in captured.out
    assert "attempt = 3" in captured.out

# 10. 시도횟수 출력 테스트
@patch('random.sample', return_value = [7,8,9])
@patch('builtins.input', side_effect = ["1 2 3", "1 2 4", "7 8 9"])
def test_game_input_prompt_print_correct_attempts(mock_input, mock_random, capsys):
    main()

    captured = capsys.readouterr()

    assert "Attempt 1: " in captured.out
    assert "Attempt 2: " in captured.out
    assert "Attempt 3: " in captured.out

# 11. decision 함수 자체 검증 테스트 
@pytest.mark.parametrize("computer,user", [
    ([1, 2, 3], [1, 2, 3]),
    ([1, 2, 3], [1, 3, 2]),
    ([1, 2, 3], [2, 1, 3]),
    ([1, 2, 3], [4, 5, 6]),
    ([1, 2, 3], [1, 4, 5]),
    ([1, 2, 3], [2, 3, 1]),
    ([4, 5, 6], [6, 5, 4]),
    ([7, 8, 9], [7, 9, 8]),
])
def test_decision_property(computer, user):
    game = GameDomain(*computer)

    result = game.decision(user)

    # 1. 반환값은 문자열이다.
    assert isinstance(result, str)

    # 2. OUT이 아니면 S 또는 B를 포함해야 한다.
    if result != "OUT":
        assert "S" in result or "B" in result

    # 3. Strike와 Ball의 합은 항상 3 이하이다.
    strike = 0
    ball = 0

    for token in result.split():
        if token.endswith("S"):
            strike = int(token[:-1])
        elif token.endswith("B"):
            ball = int(token[:-1])

    assert strike + ball <= 3

    # 4. Strike는 같은 위치의 숫자 개수와 같다.
    expected_strike = sum(
        c == u for c, u in zip(computer, user)
    )
    assert strike == expected_strike

    # 5. Ball은 같은 숫자이지만 위치가 다른 개수이다.
    expected_ball = len(set(computer) & set(user)) - expected_strike
    assert ball == expected_ball

    # 6. 겹치는 숫자가 하나도 없으면 반드시 OUT이다.
    if expected_strike == 0 and expected_ball == 0:
        assert result == "OUT"