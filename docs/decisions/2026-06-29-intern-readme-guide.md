# Intern README Guide

Date: 2026-06-29
Status: Completed
Scope: Repository documentation

## Request
인턴이 과제를 진행할 때 폴더와 Markdown 파일을 만들고, 코드를 작성하고, 적절한 단위로 커밋할 수 있도록 루트 `README.md`에 가이드를 작성한다.

## Why
과제 제출 방식과 커밋 기준을 명확히 해 인턴의 작업 이력을 읽기 쉽고 리뷰하기 쉽게 만들기 위함이다.

## Requirements
- 과제별 폴더 생성 규칙을 설명한다.
- 과제별 `README.md`에 적을 내용을 안내한다.
- 커밋 메시지 규칙과 커밋 분리 기준을 제시한다.
- 한국어로 실무적으로 바로 따라 할 수 있게 작성한다.

## Development Context
- Relevant files: `README.md`, `assignments_1/README.md`
- Observed: 현재 루트 README는 "과제 폴더 만들고 md파일 작성과 코드 작성."만 포함한다.
- Observed: `assignments_1/README.md`는 placeholder 상태다.
- Constraints: 문서 변경이며 기존 프로젝트 구조를 크게 바꾸지 않는다.

## Assumptions And Unknowns
- 과제는 `assignments_1`처럼 과제별 디렉터리 단위로 추가되는 것으로 가정한다.
- 특정 조직의 커밋 컨벤션이 없으므로 Conventional Commits 형식을 기반으로 간단한 규칙을 제안한다.

## Plan
1. 루트 `README.md`를 인턴 온보딩 가이드 형태로 확장한다.
2. 커밋 메시지 예시와 커밋 분리 기준을 포함한다.
3. 변경 내용을 확인하고 결정 기록을 완료 상태로 업데이트한다.

## Decisions
- Conventional Commits 형식을 사용한다: 짧고 널리 알려져 있어 과제 이력을 검색하고 리뷰하기 쉽다.
- 커밋 분리 기준은 "리뷰 가능한 논리 단위"로 설명한다: 너무 세밀하거나 큰 커밋을 모두 피하기 위함이다.

## Execution Notes
- Changed `README.md` from a short placeholder into an intern assignment guide.
- Included folder naming, assignment README template, commit message format, commit splitting criteria, and pre-commit checklist.
- Used four-backtick Markdown fencing around the assignment README template so nested `bash` code blocks render correctly.
- Ran `sed -n '1,260p' README.md` to verify the written content.
- Ran `git status --short`; observed pre-existing staged changes for `assignments_1/README.md` and `assignments_1/number_baseball.py` that were not modified by this task.

## Outcome
루트 `README.md`가 인턴이 과제를 시작하고 문서화하고 커밋을 나눌 때 따를 수 있는 가이드로 업데이트되었다.

## Follow-ups
- 필요하면 각 과제 폴더의 `README.md` 템플릿도 같은 형식으로 업데이트할 수 있다.
