# 에스프레스토 인턴 과제 가이드

이 저장소는 인턴 과제를 진행하고 제출하기 위한 공간입니다. 과제는 폴더 단위로 관리하고, 각 과제 폴더에는 설명 문서와 실행 가능한 코드를 함께 남깁니다.

## 기본 작업 흐름

1. 새 과제를 시작하면 과제별 폴더를 만듭니다.
2. 과제 폴더 안에 `README.md`를 작성합니다.
3. 요구사항을 이해한 뒤 작게 나누어 코드를 작성합니다.
4. 동작 확인 또는 테스트를 실행합니다.
5. 변경 내용을 의미 있는 단위로 커밋합니다.
6. 과제 완료 후 최종 실행 방법과 결과를 `README.md`에 정리합니다.

## 폴더 규칙

```text
assignments_1/
  README.md
  number_baseball.py

assignments_2/
  README.md
  main.py
```

권장 폴더 이름은 다음과 같습니다.

- `assignments_1`, `assignments_2`처럼 순번이 명확한 이름

```text
good: number_baseball.py
good: calculator_service.py
avoid: 숫자야구.py
avoid: NumberBaseballFinal.py
```

## 과제별 README 작성 규칙

각 과제 폴더의 `README.md`에는 최소한 아래 내용을 작성합니다.

````markdown
# 과제 제목

## 목표

이 과제에서 구현해야 하는 내용을 짧게 설명합니다.

## 요구사항

- 필수 기능 1
- 필수 기능 2
- 예외 처리 또는 제한 조건

## 실행 방법

```bash
python number_baseball.py
```

## 구현 내용

- 어떤 방식으로 문제를 해결했는지 설명합니다.
- 주요 함수나 클래스의 역할을 설명합니다.
````

README는 코드를 읽기 전에도 과제의 목적, 실행 방법, 구현 방향을 이해할 수 있게 작성합니다. 실행하고 확인할 수 있는 정보를 남깁니다.

## 커밋 메시지 규칙

커밋 메시지는 아래 형식을 사용합니다. 한글 사용해도 상관없음.

```text
type(scope): summary
```

- `type`: 변경의 종류
- `scope`: 영향을 받은 과제나 영역
- `summary`: 무엇을 변경했는지 한 줄로 설명

자주 쓰는 `type`은 다음과 같습니다.

| type       | 의미                     | 예시                                                |
| ---------- | ------------------------ | --------------------------------------------------- |
| `feat`     | 새 기능 추가             | `feat(assignments_1): add number input validation`  |
| `fix`      | 버그 수정                | `fix(assignments_1): handle duplicate digits`       |
| `docs`     | 문서 변경                | `docs(assignments_1): add execution guide`          |
| `refactor` | 동작 변경 없는 코드 개선 | `refactor(assignments_1): split game loop function` |
| `test`     | 테스트 추가 또는 수정    | `test(assignments_1): add invalid input cases`      |
| `chore`    | 설정, 정리, 기타 작업    | `chore: organize assignment folders`                |

좋은 커밋 메시지 예시입니다.

```text
feat(assignments_1): implement number baseball game loop
fix(assignments_1): reject non-numeric user input
docs(assignments_1): document rules and run command
refactor(assignments_1): extract score calculation function
```

피해야 할 커밋 메시지 예시입니다.

```text
update
fix
final
과제함
수정수정
```

커밋 메시지는 "내가 무엇을 왜 바꿨는지"를 나중에 봐도 알 수 있어야 합니다.

## 커밋을 나누는 기준

커밋은 시간 단위가 아니라 의미 단위로 나눕니다. 하나의 커밋은 하나의 목적만 가지는 것이 좋습니다.

좋은 커밋 분리 예시입니다.

1. 과제 폴더와 기본 README 추가
2. 핵심 기능 구현
3. 입력값 검증 추가
4. 예외 케이스 수정
5. 실행 방법과 구현 설명 문서화

이렇게 나누면 리뷰어가 각 변경의 의도를 쉽게 확인할 수 있고, 문제가 생겼을 때 어떤 변경에서 발생했는지 추적하기 쉽습니다.

## 커밋을 나눠야 하는 경우

아래 경우에는 커밋을 분리하는 것을 권장합니다.

- 새 기능을 추가한 경우
- 버그를 고친 경우
- 문서만 수정한 경우
- 코드 구조만 정리한 경우
- 테스트를 추가한 경우
- 과제 요구사항과 별개의 정리 작업을 한 경우

예를 들어, 숫자 야구 과제를 진행한다면 아래처럼 커밋할 수 있습니다.

```text
docs(assignments_1): add assignment description
feat(assignments_1): generate random answer digits
feat(assignments_1): calculate strike and ball counts
feat(assignments_1): add user input loop
fix(assignments_1): prevent duplicate input digits
docs(assignments_1): add run command and examples
```

## 하나의 커밋에 함께 넣어도 되는 경우

서로 강하게 연결되어 따로 보면 의미가 없는 변경은 하나의 커밋에 넣어도 됩니다.

- 함수 이름 변경과 그에 따른 호출부 수정
- 새 기능 구현과 해당 기능을 위한 작은 README 설명 추가
- 버그 수정과 그 버그를 확인하는 간단한 테스트 추가

다만 여러 기능, 여러 버그 수정, 문서 정리, 코드 리팩터링을 한 커밋에 모두 섞지 않습니다.

## 커밋 전 체크리스트

커밋하기 전에 아래 항목을 확인합니다.

- 코드가 실행되는가?
- 불필요한 디버그 출력이 남아 있지 않은가?
- 파일명이 과제 내용과 맞는가?
- README에 실행 방법이 적혀 있는가?
- 커밋 메시지만 봐도 변경 내용을 이해할 수 있는가?
- 이번 커밋이 하나의 목적만 가지고 있는가?

상태 확인 명령어입니다.

```bash
git status
git diff
```

커밋 예시입니다.

```bash
git add assignments_1/README.md assignments_1/number_baseball.py
git commit -m "feat(assignments_1): implement number baseball game"
```

## 리뷰 받기 좋은 작업 방식

- 처음부터 완벽하게 만들려고 하기보다 작은 단위로 구현하고 확인합니다.
- 요구사항을 모르면 추측해서 크게 만들기 전에 질문합니다.
- 코드가 길어지면 함수로 나누되, 불필요하게 복잡한 구조를 먼저 만들지 않습니다.
- README에는 실행 방법, 구현 의도, 확인한 내용을 구체적으로 적습니다.
- 커밋 이력은 과제를 풀어 간 순서와 생각의 흐름이 보이도록 남깁니다.

좋은 제출물은 코드만 있는 제출물이 아니라, 리뷰어가 과제를 이해하고 실행하고 변경 이력을 따라갈 수 있는 제출물입니다.
