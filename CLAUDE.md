# CLAUDE.md

## 프로젝트
공개 소스(HF Daily Papers, arXiv RSS, AINews, Google Alerts RSS, Hacker News)에서 AI 동향을 수집·선별·요약해
GitHub Pages에 게시하고 메일·푸시로 전달하는 일일 배치. 요구사항은 SPEC.md가 기준이다.

## 명령
- 설치: `uv sync`
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- dry-run: `uv run python -m briefing.main --dry-run --date 2026-09-29 --fixtures tests/fixtures`

## pstack 워크플로우 적용
실질적인 코딩 작업(기능, 리팩토링, 버그 수정, PR 리뷰) 시, 저장소에 포함된 pstack 스킬을 읽고 적용한다.

### 에이전트: 코딩 작업 전에 다음 파일을 읽어라

**`.cursor/skills/pstack/poteto-mode/SKILL.md`**

이 파일은 다음을 포함한다:
- 워크플로우 트리거 (언제 어떤 접근법 사용할지)
- 핵심 원칙 (Prove It Works, Fix Root Causes, Laziness Protocol 등)
- 플레이북 선택 로직 (bug fix, feature, refactoring 등)
- ai-news-bot 프로젝트 제약사항

### Cursor 에이전트

Cursor는 `.cursor/skills/use-pstack-workflows/` 스킬을 자동 발견한다.
해당 스킬은 **`.cursor/skills/pstack/poteto-mode/SKILL.md` 읽기**를 지시한다.

명시적 호출: `/poteto-mode [작업]` (선택사항, disable-model-invocation: true로 자동 안 됨)

### Claude Code 에이전트

코딩 작업 시 이 섹션을 읽고 **`.cursor/skills/pstack/poteto-mode/SKILL.md` 파일 내용**을 직접 읽어라.

명시적 호출 (전체 플러그인 설치 시):
- `/plugin marketplace add cursor/plugins`
- `/plugin install pstack@cursor-plugins`
- `/pstack:poteto-mode [작업]`

### Grok Bot 에이전트

코딩 위임 시 이 섹션 및 **`.cursor/skills/pstack/poteto-mode/SKILL.md`**를 읽어라.

Grok Bot은 소스 제어에서 저장소 파일을 읽을 수 있다. 코딩 에이전트에게 poteto-mode SKILL.md 읽기를 지시하라.

명시적 호출 (계정 플러그인 설치 시): `Skill("poteto-mode")` 또는 "pstack 워크플로우로 [작업]"

### 프로젝트 요구사항 (poteto-mode SKILL.md에 포함)

- 한 PR = 하나의 SPEC.md 마일스톤
- 테스트: `uv run pytest`
- 린트: `uv run ruff check .`
- 외부 호출은 인터페이스 뒤에, 테스트는 fixture 사용
- 프롬프트는 `prompts/`, 설정은 `sources.yaml`
- Pydantic 검증 + HTML 이스케이프
- 한 소스 실패가 전체를 멈추지 않음
- 비밀값 코드에 금지

**Upstream**: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack
**License**: MIT (Copyright 2026 Lauren Tan) - 전체 라이선스는 `.cursor/skills/pstack/LICENSE` 참조
**이 저장소**: poteto-mode 스킬 및 프로젝트 적응 버전 포함. 전체 플러그인은 upstream에서 설치 가능.

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
