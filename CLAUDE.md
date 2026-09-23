# CLAUDE.md

## 프로젝트
LinkedIn 알림 메일을 읽어 AI 관련 게시물을 요약·발송하는 일일 배치. 상세 요구사항은 SPEC.md가 기준이다.

## 명령
- 설치: `uv sync`
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- 로컬 dry-run: `uv run python -m briefing.main --dry-run --fixtures tests/fixtures`

## 규칙
- 한 PR에는 SPEC.md의 마일스톤 하나만 구현한다. 범위 밖 변경은 제안만 하고 구현하지 않는다.
- 새 기능에는 fixture 기반 테스트를 함께 추가하고, PR 전에 테스트와 린트를 통과시킨다.
- 외부 호출(IMAP, SMTP, Anthropic, ntfy)은 인터페이스 뒤에 두고 테스트에서는 가짜 구현을 쓴다.
- 프롬프트는 코드에 하드코딩하지 않고 `prompts/`에서 읽는다.
- 모델 출력은 pydantic 스키마로 검증한다.
- PR 설명에 변경 요약, 테스트 결과, 수동 확인 방법을 적는다.

## 금지
- LinkedIn 로그인 자동화, 게시물 페이지 크롤링 코드 추가
- 비밀값을 코드·로그·fixture에 포함 (fixture의 메일 주소는 마스킹)
- `state/sent.json`을 수동 로직 외 방식으로 삭제·초기화
