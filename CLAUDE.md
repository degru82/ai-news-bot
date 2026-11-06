# CLAUDE.md

## 프로젝트
공개 소스(HF Daily Papers, arXiv RSS, AINews, Google Alerts RSS, Hacker News)에서 AI 동향을 수집·선별·요약해
GitHub Pages에 게시하고 메일·푸시로 전달하는 일일 배치. 요구사항은 SPEC.md가 기준이다.

## 명령
- 설치: `uv sync`
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- dry-run: `uv run python -m briefing.main --dry-run --date 2026-09-29 --fixtures tests/fixtures`

## pstack 통합 (선택적)
실질적인 코딩 작업(기능, 리팩토링, 버그 수정, PR 리뷰)에는 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 원칙과 워크플로우를 적용한다.
pstack은 MIT 라이선스의 고품질 코드 작성 스킬셋이다(Copyright 2026 Lauren Tan).

### 설치 (1회)
- **Cursor**: `/add-plugin pstack` → `/setup-pstack`
- **Claude Code**: `/plugin marketplace add cursor/plugins` → `/plugin install pstack@cursor-plugins` → `/pstack:setup-pstack`
- **Grok Bot**: 이미 설치됨 (플러그인 9717366)

### 사용
- 버그 수정/기능: `/poteto-mode` (Cursor), `/pstack:poteto-mode` (Claude Code), "pstack 워크플로우로" (Grok Bot)
- PR 리뷰: `/interrogate` (Cursor), `/pstack:interrogate` (Claude Code)
- 코드 이해: `/how`, `/why`

pstack을 명시적으로 호출하지 않아도 `.cursor/rules/pstack-coding.mdc`의 핵심 원칙(실제 검증, 최소 변경, 근본 원인 수정 등)이 자동으로 적용된다.

**참조**: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack

## 규칙
- 한 PR에는 SPEC.md의 마일스톤 하나만 구현한다. 범위 밖 변경은 PR 설명에 제안만 한다.
- 소스 수집기는 `sources/` 아래 모듈 하나씩, 모두 `Item` 리스트를 반환하는 같은 인터페이스를 따른다.
- 한 소스의 예외가 전체 실행을 멈추게 하지 않는다. 실패는 결과 객체에 기록한다.
- 외부 호출(HTTP, Anthropic, SMTP, ntfy)은 인터페이스 뒤에 두고, 테스트는 fixture와 가짜 구현만 쓴다.
- 새 기능에는 테스트를 함께 추가하고 PR 전에 테스트·린트를 통과시킨다.
- 프롬프트는 `prompts/`, 설정은 `sources.yaml`에서 읽는다. 하드코딩 금지.
- 모델 출력은 pydantic 스키마로 검증하고, 렌더링 시 HTML 이스케이프한다.
- 요구사항·중요 설계를 추가·변경하는 PR은 결정의 배경·이유를 `docs/wiki/<섹션>/<문서>.md`에 함께 작성하고
  관련 문서끼리 상대 링크로 연결한다 (작성법: `docs/wiki/00-guide/how-to-write.md`). 머지 시 위키로 동기화된다.
- PR 설명에 변경 요약, 테스트 결과, 휴대폰에서 확인하는 방법을 적는다.

## 금지
- 로그인이 필요한 수집, 스크래핑, 유료 수집 API 추가
- 수집한 원문 문장을 페이지·메일에 그대로 게재 (요약은 자체 문장, 원문은 링크로)
- 비밀값·구독자 주소를 코드, 로그, fixture, `site/`에 포함
- `state/published.json`을 정해진 로직 외 방식으로 삭제·초기화
