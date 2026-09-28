# CLAUDE.md

## 프로젝트
공개 소스(HF Daily Papers, arXiv RSS, AINews, Google Alerts RSS, Hacker News)에서 AI 동향을 수집·선별·요약해
GitHub Pages에 게시하고 메일·푸시로 전달하는 일일 배치. 요구사항은 SPEC.md가 기준이다.

## 명령
- 설치: `uv sync`
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- dry-run: `uv run python -m briefing.main --dry-run --date 2026-09-29 --fixtures tests/fixtures`

## 규칙
- 한 PR에는 SPEC.md의 마일스톤 하나만 구현한다. 범위 밖 변경은 PR 설명에 제안만 한다.
- 소스 수집기는 `sources/` 아래 모듈 하나씩, 모두 `Item` 리스트를 반환하는 같은 인터페이스를 따른다.
- 한 소스의 예외가 전체 실행을 멈추게 하지 않는다. 실패는 결과 객체에 기록한다.
- 외부 호출(HTTP, Anthropic, SMTP, ntfy)은 인터페이스 뒤에 두고, 테스트는 fixture와 가짜 구현만 쓴다.
- 새 기능에는 테스트를 함께 추가하고 PR 전에 테스트·린트를 통과시킨다.
- 프롬프트는 `prompts/`, 설정은 `sources.yaml`에서 읽는다. 하드코딩 금지.
- 모델 출력은 pydantic 스키마로 검증하고, 렌더링 시 HTML 이스케이프한다.
- PR 설명에 변경 요약, 테스트 결과, 휴대폰에서 확인하는 방법을 적는다.

## 금지
- 로그인이 필요한 수집, 스크래핑, 유료 수집 API 추가
- 수집한 원문 문장을 페이지·메일에 그대로 게재 (요약은 자체 문장, 원문은 링크로)
- 비밀값·구독자 주소를 코드, 로그, fixture, `site/`에 포함
- `state/published.json`을 정해진 로직 외 방식으로 삭제·초기화
