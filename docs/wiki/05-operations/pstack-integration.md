# pstack 통합

## 결정

실질적인 코딩 작업(기능, 버그 수정, 리팩토링, PR 리뷰) 시 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 워크플로우를 기본 적용한다.

통합 방식: **실제 pstack 스킬 번들 + 저장소 내 포함 (MIT 라이선스 준수)**

## 배경·이유

### 문제

AI 코딩 도구(Cursor, Claude Code, Grok Bot)로 작업 시, 매번 고품질 코드 작성 가이드라인을 수동으로 지시하는 것은 비효율적이다.

### pstack 선택 이유

- MIT 라이선스 오픈소스 (Copyright 2026 Lauren Tan, Cursor 팀 제공)
- 검증 중심 워크플로우 (Prove It Works, Fix Root Causes 등)
- 23개 플레이북 (bug-fix, feature, refactoring, PR review 등)
- 다중 모델 활용 및 병렬 작업 지원
- 프로젝트 정책(SPEC.md, pytest, ruff)과 호환

### 통합 제약 및 해결

**MIT 라이선스 이해**:
- MIT는 재배포 허용 (full copyright/permission/disclaimer notices 보존 시)
- 58개 전체 스킬 복사는 과도하나, 핵심 poteto-mode 스킬은 포함 가능
- 전체 LICENSE 파일 포함 필수

**저장소 기반 해결**:
- `.cursor/skills/pstack/` 에 poteto-mode SKILL.md 포함
- LICENSE 파일 전체 포함
- Upstream 고정 참조 (commit 2776ddd)
- 저장소 상대 경로로 접근 가능

**플랫폼 차이**:
- Cursor: 네이티브 플러그인 및 스킬 발견 지원
- Claude Code: pstack prefix 필요 (`/pstack:poteto-mode`)
- Grok Bot: 계정 플러그인, 명시적 호출 필요

## 검토한 대안

### 대안 1: pstack 전체 복사 (부분 채택 → 핵심만)

`.cursor/skills/`에 pstack 58개 스킬 전체 복사

**장점**: 저장소만으로 완전 자급자족  
**단점**:
- 58개 전체는 과도함
- Upstream 업데이트 추적 필요
- 저장소 크기 증가

**결정**: **핵심 poteto-mode만 포함** (MIT 라이선스 준수, LICENSE 파일 포함)

### 대안 2: 원칙 요약만 (기각)

`.cursor/rules/pstack-coding.mdc`에 핵심 8원칙 요약 포함

**장점**: 간결함, 저작권 문제 없음  
**단점**:
- 실제 스킬 읽기 없음 (요약만 제공)
- 플레이북 로직 누락
- "원칙 요약 = pstack 사용"이라는 잘못된 전제

**결정**: 기각 (사용자 요구사항 미충족 - 실제 스킬 읽기 필요)

### 대안 3: 저장소 내 실제 스킬 번들 (채택)

`.cursor/skills/pstack/poteto-mode/SKILL.md`: 실제 pstack 스킬을 저장소에 포함

**구조**:
1. `.cursor/skills/pstack/LICENSE`: MIT 라이선스 전체 텍스트
2. `.cursor/skills/pstack/poteto-mode/SKILL.md`: 실제 poteto-mode 스킬
3. `.cursor/skills/use-pstack-workflows/SKILL.md`: 에이전트를 poteto-mode 읽기로 라우팅
4. `CLAUDE.md`: 모든 에이전트에게 poteto-mode SKILL.md 읽기 지시

**장점**:
- **실제 스킬 파일** 저장소 내 포함 (요약 아님)
- MIT 라이선스 준수 (전체 LICENSE 포함)
- 사용자 플러그인 설치 불필요
- 저장소 상대 경로로 접근 가능
- Cursor, Claude Code, Grok Bot 모두 동일 파일 읽기

**단점**:
- Upstream 업데이트 수동 동기화 필요
- 핵심 스킬만 포함 (전체 58개 아님)

**결정**: 채택 (MIT 재배포 허용, 실제 스킬 포함, 플랫폼 무관)

## 구현 상세

### Cursor 통합

**파일**: `.cursor/skills/use-pstack-for-coding/SKILL.md`

**내용**:
- Frontmatter: 자동 발견을 위한 description (코딩 작업 시 매칭)
- 지시사항: "설치된 pstack 플러그인에서 poteto-mode SKILL.md 읽기"
- 폴백: 플러그인 미접근 시 핵심 원칙 8개 적용
- 프로젝트 정책: SPEC.md, pytest, ruff 요구사항

**작동**:
1. 사용자: "briefing/sources/hf.py에 키워드 필터링 추가해줘" (슬래시 명령 없음)
2. Cursor: description 기반 자동 스킬 발견 → `use-pstack-for-coding` 로드
3. 에이전트: 스킬 내용 읽음 → "플러그인에서 poteto-mode 읽기" 지시 확인
4. 에이전트: `~/.cursor/plugins/cache/.../skills/poteto-mode/SKILL.md` 접근 시도
5. 성공 시: 실제 플레이북 로직 따름 / 실패 시: 폴백 원칙 적용

### Claude Code / Grok Bot 통합

**파일**: `CLAUDE.md`의 "pstack 워크플로우 적용" 섹션

**내용**:
- 플러그인 설치 방법
- 명시적 호출 방법 (`/pstack:poteto-mode`)
- 폴백 핵심 원칙 8개

**작동**:
- 에이전트가 CLAUDE.md 읽음 (프로젝트 레벨 지침)
- 플러그인 설치 시: 명시적 호출로 전체 워크플로우
- 플러그인 미설치 시: 폴백 원칙 적용

### 핵심 원칙 (폴백)

Upstream pstack에서 추출한 8가지 핵심 원칙:

1. **Prove It Works**: 실제 아티팩트로 검증 (명령 출력, 프록시 아님)
2. **Laziness Protocol**: 최소 변경, 삭제 선호
3. **Fix Root Causes**: 증상이 아닌 근본 원인 수정
4. **Type System Discipline**: Pydantic 검증, 경계에서 파싱
5. **Boundary Discipline**: 시스템 경계 가드, 순수 비즈니스 로직
6. **Test Behavior**: 사용자 관찰 가능 동작 테스트
7. **Sequence Verifiable Units**: 작은 검증 가능 커밋
8. **Never Block on Human**: 진행 후 결과 제시, 되돌릴 수 없는 작업만 확인

## 검증

### 정적 검증 (자동)

`scripts/verify-pstack-integration.sh`:
- `.cursor/skills/use-pstack-for-coding/SKILL.md` 존재 및 유효 frontmatter
- Upstream 불변 참조 (commit SHA)
- MIT 라이선스 및 저작권 표시
- CLAUDE.md 통합
- 비밀값 누출 확인
- **부정 테스트**: 스킬 파일 삭제 시 실패, frontmatter 손상 시 실패

### 런타임 검증 (수동, 환경 필요)

**Cursor에서**:
1. pstack 플러그인 설치: `/add-plugin pstack`, `/setup-pstack`
2. 코딩 요청: "tests/test_normalize.py 설명해줘"
3. 확인: 에이전트가 poteto-mode 또는 관련 스킬 참조 여부
4. 로그/트랜스크립트: 실제 스킬 읽기 흔적 확인

**Claude Code에서**:
1. 플러그인 설치 확인
2. CLAUDE.md 읽기 확인
3. `/pstack:poteto-mode` 명시적 호출 테스트

**제한사항**: 이 통합 PR에서는 런타임 검증 미수행 (Cursor IDE 환경 부재)

## 라이선스 및 출처

**Upstream**: https://github.com/cursor/plugins/tree/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack  
**License**: MIT (Copyright 2026 Lauren Tan)  
**Plugin version**: 0.15.36

**Full license text**: https://github.com/cursor/plugins/blob/2776ddd2355d6d6c8747d3964600f28daf62f049/pstack/LICENSE

이 저장소에 커밋된 파일 (`.cursor/skills/use-pstack-for-coding/SKILL.md`, `CLAUDE.md`의 핵심 원칙)은 pstack의 파생 저작물이 아니라 **로더 및 폴백 요약**이다. 실제 워크플로우는 사용자가 설치하는 upstream pstack 플러그인에서 제공된다.

## 변경 이력

- 2026-11-06 PR #18: 초기 통합 (스킬 로더 방식 채택)
  - 대안 1 (전체 복사) 기각: 저작권 및 유지보수
  - 대안 2 (원칙 요약만) 기각: 실제 스킬 읽기 없음
  - 대안 3 (로더 + 폴백) 채택: 요구사항 충족

관련: [operations-and-security](operations-and-security.md)
