# CLAUDE.md

## 프로젝트
공개 소스(HF Daily Papers, arXiv RSS, AINews, Google Alerts RSS, Hacker News)에서 AI 동향을 수집·선별·요약해
GitHub Pages에 게시하고 메일·푸시로 전달하는 일일 배치. 요구사항은 SPEC.md가 기준이다.

## 명령
- 설치: `uv sync`
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- dry-run: `uv run python -m briefing.main --dry-run --date 2026-09-29 --fixtures tests/fixtures`

## pstack 워크플로우 (코딩 작업 시 필수 읽기)
실질적인 코딩 작업(기능, 리팩토링, 버그 수정, PR 리뷰) 시, 저장소에 번들된 **완전한 upstream pstack**을 읽고 적용한다.

### 에이전트: 코딩 작업 전 필수

**1단계: Entry point 읽기**

`.cursor/skills/pstack/skills/poteto-mode/SKILL.md`

**2단계: 참조된 스킬/플레이북 읽기**

poteto-mode가 참조하는 파일들을 읽어라 (모두 `.cursor/skills/pstack/`에 번들됨):
- 스킬: `skills/[skill-name]/SKILL.md` (예: how, why, interrogate, architect 등)
- 원칙: `skills/principle-[name]/SKILL.md` (예: principle-prove-it-works 등)
- 플레이북: `skills/poteto-mode/playbooks/[name].md` (예: bug-fix.md, feature.md 등)

### Cursor 에이전트

Always-applied project rule: `.cursor/rules/use-pstack.mdc`

코딩 작업 전:
1. Always-applied rule이 poteto-mode 경로 안내
2. `.cursor/skills/pstack/skills/poteto-mode/SKILL.md` 읽기
3. poteto-mode가 참조하는 스킬/플레이북 읽기
4. 워크플로우 적용

### Claude Code 에이전트

1. 이 `CLAUDE.md` 섹션 읽기
2. `.cursor/skills/pstack/skills/poteto-mode/SKILL.md` 읽기
3. Poteto-mode가 참조하는 스킬/플레이북 읽기 (위 경로 참조)
4. 워크플로우 적용

### Grok Bot 에이전트

1. 소스 제어에서 이 `CLAUDE.md` 읽기
2. 코딩 에이전트에게 poteto-mode 읽기 지시
3. 에이전트가 `.cursor/skills/pstack/skills/poteto-mode/SKILL.md` 및 참조 파일 읽기
4. 워크플로우 적용

### ai-news-bot 프로젝트 제약 (항상 준수)

- 한 PR = 하나의 SPEC.md 마일스톤
- 테스트: `uv run pytest`
- 린트: `uv run ruff check . && uv run ruff format --check .`
- 외부 호출은 인터페이스 뒤에, 테스트는 fixture 사용
- 프롬프트는 `prompts/`, 설정은 `sources.yaml`
- Pydantic 검증 + HTML 이스케이프
- 한 소스 실패가 전체를 멈추지 않음
- 비밀값 코드에 금지

### 에이전트 권한 제한 (원본 사용자 승인 필수)

**파괴적 Git 작업**: 푸시된 브랜치의 force-push, 리베이스, 브랜치 삭제는 명시적 사용자 확인 후에만 수행

**병합 작업**: PR 병합, auto-merge 활성화는 명시적 지시 없이 금지

**외부 메시지**: Slack, Linear, GitHub discussions 메시지 게시는 명시적 요청 후에만

**호스트 정책 우선**: Cursor/Claude/Grok 호스트 네이티브 정책이 스킬 제안과 충돌 시 호스트 정책 우선

모든 되돌릴 수 없는 작업은 실행 전 사용자 확인 필수.

### 번들 정보

**완전한 upstream pstack** (573 files, 8MB):
- **소스**: https://github.com/cursor/plugins
- **커밋**: 2776ddd2355d6d6c8747d3964600f28daf62f049
- **라이선스**: MIT (Copyright 2026 Lauren Tan) - `.cursor/skills/pstack/LICENSE` 참조
- **Provenance**: `.cursor/skills/pstack/PROVENANCE.md`
- **무결성**: `.cursor/skills/pstack/MANIFEST.sha256` (573 file hashes, strict SHA256 validation)
- **검증**: `bash scripts/verify-upstream.sh` (byte-comparison with upstream)

모든 58개 스킬, 플레이북, 참조, 원칙, dotfiles가 byte-for-byte 포함됨. 요약 아님, 완전한 upstream.

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
