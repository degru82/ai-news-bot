# pstack 통합

## 결정

실질적인 코딩 작업(기능, 버그 수정, 리팩토링, PR 리뷰) 시 [pstack](https://github.com/cursor/plugins/tree/main/pstack) 워크플로우를 기본 적용한다.

통합 방식: **완전한 upstream pstack 번들 (573 files, 8MB) + 저장소 내 포함 (MIT 라이선스 준수)**

## 배경·이유

### 문제

AI 코딩 도구(Cursor, Claude Code, Grok Bot)로 작업 시, 매번 고품질 코드 작성 가이드라인을 수동으로 지시하는 것은 비효율적이다.
요약이나 원칙만 제공하는 것은 부족하며, **실제 워크플로우 스킬과 참조된 모든 의존성**이 필요하다.

### pstack 선택 이유

- MIT 라이선스 오픈소스 (Copyright 2026 Lauren Tan, Cursor 팀 제공)
- 검증 중심 워크플로우 (Prove It Works, Fix Root Causes 등)
- 58개 스킬, 23개 플레이북 (bug-fix, feature, refactoring, PR review 등)
- 참조 체계: poteto-mode가 how, why, interrogate 등 스킬 참조, playbook 참조
- 다중 모델 활용 및 병렬 작업 지원
- 프로젝트 정책(SPEC.md, pytest, ruff)과 호환

### 통합 제약 및 해결

**MIT 라이선스 준수**:
- MIT는 재배포 허용 (copyright, permission, disclaimer 보존 시)
- **완전한 upstream LICENSE 파일 byte-for-byte 포함**
- **Provenance 메타데이터로 출처 추적**
- 원본 변경 금지, 적응은 별도 파일에 명시

**완전성 요구사항**:
- poteto-mode만으로는 부족: 참조된 스킬/playbook이 "not bundled" 되면 작동 불가
- **해결: 완전한 upstream pstack 트리 (573 files) 복사**
- 크기는 허용 범위 (8MB), 의존성 누락 문제 해결

**저장소 기반 해결**:
- `.cursor/skills/pstack/` 에 **완전한 upstream pstack** 포함
- `MANIFEST.sha256`: 571개 파일의 SHA256 해시
- `PROVENANCE.md`: upstream commit SHA, 날짜, 출처
- `scripts/sync-pstack.sh`: 재현 가능한 동기화 스크립트
- 저장소 상대 경로로 접근 가능

**플랫폼 차이**:
- Cursor: description 기반 스킬 발견 (always-applied 아님)
- Claude Code: `CLAUDE.md` 읽기, poteto-mode 및 참조 스킬 순차 읽기
- Grok Bot: 소스 제어 읽기, 코딩 에이전트에 스킬 읽기 지시

## 검토한 대안

### 대안 1: 문서만 작성 (기각)

`docs/pstack-integration.md`에 pstack 사용 가이드 작성

**장점**: 간단, 저작권 문제 없음
**단점**:
- 수동 슬래시 명령 필요 (`/poteto-mode`)
- 매번 명시적 호출 요구
- 기본 적용 아님

**결정**: 기각 (사용자 요구사항 "기본으로 사용" 미충족)

### 대안 2: 원칙 요약만 (기각)

`.cursor/rules/pstack-coding.mdc`에 핵심 8원칙 요약 포함

**장점**: 간결함, 저작권 문제 없음
**단점**:
- 실제 스킬 읽기 없음 (요약만 제공)
- 플레이북 로직 누락
- "원칙 요약 = pstack 사용"이라는 잘못된 전제
- Attack the Premise 테스트 실패

**결정**: 기각 (사용자 명시적 거부 - 실제 스킬 읽기 필요)

### 대안 3: 캐시 경로 라우터 (기각)

`~/.cursor/plugins/cache/cursor-public/.../pstack/` 경로로 라우팅

**장점**: 중복 저장 회피
**단점**:
- 미문서화 speculative 경로
- 사용자가 플러그인 설치 필요
- 경로 불안정 (캐시 삭제 시 손실)
- Cursor 외 플랫폼 불가

**결정**: 기각 (사용자 명시적 거부 - "저장소에 반영 불가?" 요구)

### 대안 4: poteto-mode만 + "playbooks not bundled" 주석 (기각)

핵심 poteto-mode SKILL.md만 포함, 참조 파일은 "not bundled" 명시

**장점**: 작은 번들 크기
**단점**:
- **참조 파일 누락으로 실제 작동 불가**
- poteto-mode가 참조하는 how, why, playbooks/*.md 없음
- "condensed version" 레이블 = 완전한 스킬셋 아님

**결정**: 기각 (사용자 명시적 거부 - "의존성 갭 해결" 요구)

### 대안 5: 완전한 upstream pstack 번들 (채택)

**완전한 upstream pstack 트리 (573 files, 8MB) 저장소 포함**

**구조**:
1. `.cursor/skills/pstack/`: 완전한 upstream pstack (byte-for-byte)
   - `LICENSE`: 원본 MIT 라이선스 (변경 없음)
   - `MANIFEST.sha256`: 571개 파일 SHA256 해시
   - `PROVENANCE.md`: upstream commit SHA, 날짜, 출처 (별도 메타데이터)
   - `skills/`: 58개 스킬 (poteto-mode, how, why, architect, principle-*, 등)
   - `skills/poteto-mode/playbooks/`: 23개 playbook (bug-fix.md, feature.md, 등)
   - `agents/`, `docs/`, `plugin.json`, 등 모든 upstream 파일
2. `.cursor/skills/use-pstack-workflows/SKILL.md`: 라우터 (local adaptation, 명시 레이블)
3. `CLAUDE.md`: 모든 에이전트에게 poteto-mode + 참조 스킬 읽기 지시
4. `scripts/sync-pstack.sh`: 재현 가능한 동기화 스크립트
5. `scripts/verify-pstack-integration.sh`: 무결성 검증 + 부정 테스트

**장점**:
- **실제 완전한 스킬셋** (요약 아님, condensed 아님)
- **모든 참조 의존성 포함** (playbooks, principles, references)
- MIT 라이선스 준수 (원본 LICENSE byte-for-byte 보존)
- SHA256 manifest로 무결성 검증
- 재현 가능 (sync script)
- 사용자 플러그인 설치 불필요
- Cursor, Claude Code, Grok Bot 모두 동일 파일 읽기

**단점**:
- 8MB 크기 (git 저장소에 포함)
- Upstream 업데이트 수동 동기화 필요

**결정**: 채택 (사용자 명시 "573 files ACCEPTABLE", MIT 허용, 의존성 갭 해결)

## 구현 상세

### 1. 완전한 upstream pstack 번들

**위치**: `.cursor/skills/pstack/`

**내용** (573 files, 8MB, byte-for-byte upstream copy):
```
.cursor/skills/pstack/
├── LICENSE                          # 원본 MIT 라이선스 (변경 없음)
├── MANIFEST.sha256                  # 573 files SHA256 해시 (local)
├── PROVENANCE.md                    # upstream commit SHA, 출처 (local)
├── README.md                        # upstream README
├── plugin.json                      # upstream plugin metadata
├── agents/                          # poteto-agent, comment-sicko 등
├── docs/                            # guide/, harness/ (claude-code.md 등)
├── skills/                          # 58개 스킬 디렉토리
│   ├── poteto-mode/
│   │   ├── SKILL.md                 # entry point (disable-model-invocation: true)
│   │   ├── playbooks/               # 23개 playbook (bug-fix, feature, 등)
│   │   ├── references/
│   │   └── scripts/
│   ├── how/, why/, interrogate/, architect/, arena/, swarm/, ...
│   └── principle-*/ (prove-it-works, fix-root-causes, 등)
└── assets/
```

**Provenance 추적**:
- `PROVENANCE.md`: upstream 출처, commit SHA `2776ddd2355d6d6c8747d3964600f28daf62f049`
- `MANIFEST.sha256`: 571개 파일의 SHA256 해시 (무결성 검증)

**동기화 스크립트**:
- `scripts/sync-pstack.sh [commit-sha]`: upstream에서 재복사, manifest 재생성

### 2. 라우터 스킬 (local adaptation)

**파일**: `.cursor/skills/use-pstack-workflows/SKILL.md`

**Frontmatter**: description 기반 발견 (코딩 작업 시 매칭)

**내용**:
- Entry point 경로: `.cursor/skills/pstack/skills/poteto-mode/SKILL.md`
- 참조 의존성 경로 안내: `skills/[name]/SKILL.md`, `playbooks/[name].md`
- ai-news-bot 프로젝트 제약사항 (SPEC.md, pytest, ruff)
- **명시 레이블**: "This router is a LOCAL ADAPTATION"

### 3. CLAUDE.md 통합

**섹션**: "pstack 워크플로우 (코딩 작업 시 필수 읽기)"

**지시사항**:
1. Entry point 읽기: `.cursor/skills/pstack/skills/poteto-mode/SKILL.md`
2. 참조된 스킬/playbook 읽기 (모두 번들됨)
3. Cursor: description 발견 → router → poteto-mode
4. Claude Code: CLAUDE.md → poteto-mode → 참조 스킬
5. Grok Bot: 소스 제어 → CLAUDE.md → 코딩 에이전트에 지시

**번들 정보**: 573 files, 8MB, commit 2776ddd, MIT 라이선스

### 4. 호스트별 작동 방식

**Cursor**:
1. 사용자: "briefing/sources/hf.py에 키워드 필터링 추가해줘"
2. Cursor: description 매칭 → `use-pstack-workflows` 발견
3. 에이전트: router 읽음 → entry point 경로 확인
4. 에이전트: `.cursor/skills/pstack/skills/poteto-mode/SKILL.md` 읽기
5. poteto-mode: playbook 참조 → `playbooks/feature.md` 읽기
6. 워크플로우 적용

**Claude Code**:
1. 세션 시작: `CLAUDE.md` 읽기
2. 코딩 요청: pstack 섹션 참조
3. 에이전트: poteto-mode 경로 확인 → 읽기
4. poteto-mode: 참조 스킬 (`how`, `why`, 등) 읽기
5. 워크플로우 적용

**Grok Bot**:
1. 소스 제어: `CLAUDE.md` 읽기
2. 코딩 에이전트 호출 시: poteto-mode 읽기 지시
3. 에이전트: poteto-mode + 참조 스킬 읽기
4. 워크플로우 적용

## 검증

### 정적 검증 (자동)

**`scripts/verify-pstack-integration.sh`** - 완전성 검증:
1. 번들 구조: pstack/, LICENSE, PROVENANCE.md, MANIFEST.sha256
2. **무결성**: 571개 파일 SHA256 해시 검증 (`sha256sum -c`)
3. **의존성 해결**: 참조된 스킬/playbook 실존 확인 (how, why, principle-*, playbooks/*)
4. **condensed 아님**: "condensed version" 레이블 없음, "playbooks not bundled" 문구 없음
5. 라우터: `use-pstack-workflows` 존재, 올바른 entry point 경로 참조
6. CLAUDE.md: poteto-mode 경로 참조, "완전한 upstream" 언급
7. README.md: 삭제된 `.cursor/rules/pstack-coding.mdc` 참조 없음
8. Provenance: commit SHA `2776ddd`, 573 files 언급
9. 동기화 스크립트: 존재, 실행 가능, manifest 생성 로직
10. 보안: API key, 이메일 누출 확인

**`tests/test_pstack_integration.py`** - 부정 테스트 (9개):
- **실제 production validator 실행**: 변조된 fixture에서 `verify-pstack-integration.sh` 실행
- 실패 케이스 (비제로 exit code 검증):
  1. pstack/ 디렉토리 누락
  2. MANIFEST.sha256 누락
  3. 파일 손상 (hash mismatch)
  4. poteto-mode 누락
  5. playbooks/ 누락
  6. 참조 의존성 누락 (how, why, 등)
  7. 라우터 누락
  8. README.md 내 stale 참조 (`pstack-coding.mdc`)

### 런타임 검증 (수동, 환경 필요)

**정적 검증 완료 후 수동 런타임 테스트**:

**Cursor에서**:
1. 코딩 요청: "briefing/sources/hf.py에 키워드 필터링 추가해줘"
2. 확인: 에이전트가 `.cursor/skills/pstack/skills/poteto-mode/SKILL.md` 읽기 여부
3. 확인: playbook 참조 (`playbooks/feature.md`) 읽기 여부
4. 트랜스크립트: Read tool call로 poteto-mode 및 참조 파일 확인

**Claude Code에서**:
1. 새 세션: `CLAUDE.md` 자동 읽기 확인
2. 코딩 요청 시: poteto-mode 경로 참조 확인
3. 트랜스크립트: 실제 스킬 읽기 흔적 확인

**제한사항**: 정적 검증만 자동화 (runtime은 IDE 환경 필요)

## 라이선스 및 출처

**Upstream**: https://github.com/cursor/plugins
**Commit**: 2776ddd2355d6d6c8747d3964600f28daf62f049
**License**: MIT (Copyright 2026 Lauren Tan)
**Full license**: `.cursor/skills/pstack/LICENSE` (byte-for-byte upstream copy)

### MIT 라이선스 준수

**조건**:
- Copyright notice 보존 (✓ LICENSE 파일)
- Permission text 보존 (✓ LICENSE 파일)
- Disclaimer 보존 (✓ LICENSE 파일)
- 원본 변경 금지 (✓ byte-for-byte copy)

**적응과 원본 분리**:
- **원본 (upstream)**: `.cursor/skills/pstack/` 내 모든 파일 (변경 없음)
- **적응 (local)**:
  - `.cursor/skills/use-pstack-workflows/SKILL.md` (라우터, "LOCAL ADAPTATION" 명시)
  - `CLAUDE.md` pstack 섹션 (프로젝트 지침)
  - `scripts/verify-pstack-integration.sh` (검증)
  - `scripts/sync-pstack.sh` (동기화)

**Provenance 추적**:
- `.cursor/skills/pstack/PROVENANCE.md`: 출처 URL, commit SHA, 날짜
- `.cursor/skills/pstack/MANIFEST.sha256`: 573 files 무결성 해시

## 유지보수

### Upstream 업데이트

```bash
# Upstream 변경 확인
git log --oneline 2776ddd2355d6d6c8747d3964600f28daf62f049..HEAD \
  --repo https://github.com/cursor/plugins -- pstack/

# 새 commit으로 동기화
bash scripts/sync-pstack.sh <new-commit-sha>

# 검증
bash scripts/verify-pstack-integration.sh
uv run pytest tests/test_pstack_integration.py

# 커밋
git add .cursor/skills/pstack
git commit -m "Update pstack to <new-commit-sha>"
```

### 무결성 수동 검증

```bash
cd .cursor/skills/pstack
sha256sum -c MANIFEST.sha256 --quiet && echo "OK: All 573 files intact"
```

## 변경 이력

- 2026-11-07 PR #18 (43330a4 → HEAD): **완전한 upstream pstack 번들 (573 files)**
  - 대안 1-4 기각 (문서만, 요약, 캐시 경로, poteto-mode만)
  - 대안 5 채택: 완전한 upstream 복사 + SHA256 manifest + 동기화 스크립트
  - 이유: 의존성 갭 해결, MIT 준수, 재현 가능성
  - 검증: 정적 validator + 9개 부정 테스트 (production validator 실행)

관련: [operations-and-security](operations-and-security.md)
