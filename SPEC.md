# LinkedIn AI 모닝 브리핑 — SPEC

## 0. 목표
매일 07:30(KST)까지, 내가 지정한 LinkedIn 계정들의 지난 24시간 AI 관련 게시물 중
중요한 것 최대 7건을 한국어로 요약해 **아이폰 푸시(짧은 버전)**와 **메일(긴 버전)**로 받는다.

## 1. 범위
**MVP 포함**
- LinkedIn 알림 메일 수집 → 워치리스트 필터 → Claude 선별·요약 → 메일/푸시 발송
- GitHub Actions cron 실행, 수동 실행(`workflow_dispatch`), dry-run 모드

**MVP 제외 (하지 않음)**
- LinkedIn 로그인·스크래핑, 게시물 페이지 직접 크롤링
- 웹 대시보드, 다중 사용자, 네이티브 iOS 앱
- 이미지/동영상 내용 분석

## 2. 사전 준비 (사람이 직접 할 일)
| # | 작업 | 비고 |
|---|------|------|
| P1 | 워치리스트 계정 팔로우 + 프로필의 🔔 알림 켜기 | 15~30명으로 시작 |
| P2 | LinkedIn 설정 → 알림 → 이메일 알림에서 게시물 관련 알림 켜기 | |
| P3 | **1주일간 실제 도착 메일 관찰** | 게시물당 1통인지, 다이제스트인지, 본문이 얼마나 잘리는지 확인 |
| P4 | 수집 전용 Gmail 생성, 2단계 인증 + 앱 비밀번호 발급 | 메인 메일 권한을 GitHub에 주지 않기 위함 |
| P5 | 메인 메일에 필터: `from:linkedin.com` → 수집용 Gmail로 자동 전달 | |
| P6 | ntfy 앱 설치, 추측 어려운 토픽 이름 생성 | |
| P7 | GitHub **private** 저장소 생성, Secrets 등록 (휴대폰 브라우저에서) | 아래 9장 목록 |
| P8 | 실제 LinkedIn 알림 메일 5~10건을 fixture로 확보 | M0 워크플로로 자동화 가능 |

## 3. 처리 흐름
```
[cron 21:30 UTC] → collect(IMAP) → parse → filter(워치리스트·중복·24h)
   → select(Haiku, 점수화) → summarize(Sonnet) → render(push/email)
   → deliver → state 갱신·커밋
```

## 4. 수집 규칙
- IMAP(`imap.gmail.com`)으로 수집용 Gmail 접속, 발신 도메인 `linkedin.com` 메일만 대상
- IMAP `SINCE`는 날짜 단위이므로, 코드에서 `Date` 헤더로 **최근 26시간** 재필터
- 파싱 항목: 작성자 이름, 작성자 프로필 URL(가능 시), 게시물 본문 스니펫, 게시물 URL, 수신 시각
- **URL 정규화**: 추적 파라미터가 붙은 링크에서 `urn:li:activity:<ID>` 또는 `/posts/...` 경로를 추출해 `activity_id`를 중복 키로 사용
- **워치리스트 필터**: `config.yaml`의 계정 목록에 있는 작성자만 통과
  (LinkedIn 메일에 섞여 오는 추천 게시물, 채용, "알 수도 있는 사람" 등은 버림)
- 파싱 실패 메일은 버리지 말고 `logs/unparsed/`에 제목과 발신자만 기록
- 본문은 **메일에 담긴 스니펫만 사용**. 원문 페이지를 가져오지 않음

## 5. 선별 규칙 (1단계, 저가 모델)
- 모델: `claude-haiku-4-5-20251001`
- 게시물별 1~5점과 한 줄 근거를 JSON으로 반환
- **가점 주제**: 신규 모델·논문·벤치마크, 엔터프라이즈 도입 사례, RAG/에이전트/LLMOps 실무, AI 규제·거버넌스, 금융권 AI
- **제외**: 채용 공고, 행사·강의 홍보, 참여 유도형 글("동의하면 댓글"), 내용 없는 축하·근황
- 3점 이상만 통과, 점수순 최대 7건
- 좋은 예/나쁜 예: `prompts/examples.md`에 각 3건 (P8 fixture에서 선택)

## 6. 요약 형식 (2단계, 상위 모델)
- 모델: `claude-sonnet-5`
- 한국어 요약, 전문 용어는 원문 병기 (예: 검색 증강 생성(RAG))
- 게시물별: `제목(15자 내외)`, `작성자`, `요약 3줄`, `왜 중요한가 1줄`, `링크`
- 맨 위 "오늘의 헤드라인" 1~2줄

**푸시 (ntfy, 500자 이내)**
```
🤖 AI 브리핑 9/16 (5건)
오늘의 헤드라인: ...
1. [제목] 작성자
2. [제목] 작성자
→ 자세한 내용은 메일
```

**메일 (HTML + 텍스트 대체본)**
- 제목: `[AI 브리핑] 2026-09-16 (5건) — 헤드라인 앞부분`
- 본문: 헤드라인 → 게시물 카드 목록 → 하단에 "선별 제외 N건" 통계

## 7. 전달·스케줄
- cron: `30 21 * * *` (KST 06:30, 실행 지연 감안해 여유 둠)
- 주말 포함 매일
- 메일: 수집용 Gmail SMTP로 메인 메일에 발송
- **0건일 때**: 푸시만 "오늘은 주요 게시물 없음" 발송, 메일 생략

## 8. 상태·실패 처리
- `state/sent.json`: `{activity_id: 발송일}`, 30일 지난 항목 삭제, 실행 후 봇 커밋
- 같은 activity_id는 재발송 금지
- Claude API 실패: 지수 백오프 3회 재시도
- 선별 단계 실패 시: 선별 없이 최신순 7건으로 요약 진행
- 전체 실패 시: 푸시로 "브리핑 실패 + Actions 로그 링크" 발송
- 로그: 수집 건수, 필터 후 건수, 선별 통과 건수, 토큰 사용량

## 9. 비용·보안
- 월 API 비용 상한 목표: $5 (요청마다 토큰 수 로깅)
- **GitHub Secrets**: `ANTHROPIC_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `MAIL_TO`, `NTFY_TOPIC`
- 비밀값은 로그에 출력 금지
- 게시물 본문은 신뢰할 수 없는 입력으로 취급: 프롬프트에서 데이터 영역을 태그로 구분하고, 모델 출력은 JSON 스키마로 검증 (프롬프트 인젝션 대비)
- LinkedIn 로그인 자동화·크롤링 코드는 추가하지 않음

## 10. 기술 스택·구조
- Python 3.12, uv, pytest, ruff
- 라이브러리: `anthropic`, `pydantic`, `beautifulsoup4`, `pyyaml`, `httpx`, 표준 `imaplib`/`smtplib`

```
.
├── CLAUDE.md
├── SPEC.md
├── config.yaml
├── prompts/  (select.md, summarize.md, examples.md)
├── src/briefing/  (collect.py, parse.py, filter.py, select.py,
│                   summarize.py, render.py, deliver.py, state.py, main.py)
├── state/sent.json
├── tests/  (fixtures/*.eml, test_*.py)
└── .github/workflows/  (daily.yml, ci.yml, fetch-fixtures.yml)
```

## 11. config.yaml 예시
```yaml
timezone: Asia/Seoul
lookback_hours: 26
max_items: 7
min_score: 3
watchlist:
  - name: "Andrew Ng"
    profile: "https://www.linkedin.com/in/andrewyng"
  - name: "홍길동"
    profile: "https://www.linkedin.com/in/..."
delivery:
  push: true
  email: true
  send_when_empty: push_only
```

## 12. 마일스톤 (PR 단위)
| # | 내용 | 완료 조건 |
|---|------|-----------|
| M0 | 수동 실행 워크플로로 최근 LinkedIn 메일 10건을 artifact로 저장 | 휴대폰에서 artifact 다운로드 확인 |
| M1 | fixture `.eml` → 파싱 → 워치리스트 필터 | pytest 통과, 추천 게시물 제외 확인 |
| M2 | 선별·요약 + dry-run(`--dry-run`이면 `out/`에 md 출력) | 수동 실행 결과 md를 읽고 품질 합격 |
| M3 | 메일 발송 | 메인 메일 수신 확인 |
| M4 | 실제 IMAP 수집 연결 + 중복 제거 + state 커밋 | 2회 연속 실행 시 중복 0건 |
| M5 | cron 활성화 + ntfy 푸시 + 실패 알림 | 3일 연속 07:30 이전 수신 |

## 13. 미정 사항
- [ ] P3 관찰 결과에 따라 파서 전략 확정 (개별 메일 / 다이제스트)
- [ ] 워치리스트 최종 목록
- [ ] 좋은 예/나쁜 예 게시물 선정
