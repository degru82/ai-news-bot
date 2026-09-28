# AI 모닝 브리핑 — SPEC v2 (1단계: 무료 공개 소스)

## 0. 목표
매일 07:00(KST)까지 **공개 소스만으로** 지난 24시간의 AI 기술·트렌드와 주목할 논문을 선별·요약하여,
웹 페이지(+RSS)로 게시하고 구독자에게 메일로, 운영자에게 푸시로 전달한다.
개인 계정 자격증명 없이 동작해 **동료가 구독하거나 그대로 복제해 쓸 수 있어야** 한다.

## 1. 범위
**포함**
- 5개 소스 수집: HF Daily Papers, arXiv RSS, AINews RSS, Google Alerts RSS, Hacker News
- 정규화 → 중복 제거 → 사전 필터 → LLM 선별 → LLM 요약
- GitHub Pages 게시(날짜별 페이지, 아카이브, `feed.xml`), 구독자 메일, 운영자 ntfy 푸시
- 날짜 지정 재실행(backfill), dry-run

**제외**
- X/Threads 직접 수집, 로그인·스크래핑, 유료 수집 API
- 개인별 맞춤 브리핑, 웹 구독 신청 폼, 댓글·추천 기능
- 논문 PDF 본문 분석 (초록만 사용)

## 2. 사용자
| 역할 | 하는 일 |
|------|---------|
| 운영자(본인) | 소스·키워드 관리, 품질 점검, 실패 대응 |
| 구독자(동료) | 메일 또는 RSS로 읽기 |
| 기여자(동료) | `sources.yaml`에 키워드·Alerts 피드 추가 PR |

## 3. 소스별 수집 요구사항
| 소스 | 방식 | 수집 기준 | 주의 |
|------|------|-----------|------|
| **HF Daily Papers** | `GET https://huggingface.co/api/daily_papers?date=YYYY-MM-DD` | 실행 시점 UTC 날짜 목록, upvote 기준치 이상 | 응답 필드명(upvote, GitHub 링크 등)은 M1에서 실제 응답으로 확정 |
| **arXiv RSS** | `https://rss.arxiv.org/rss/cs.CL+cs.AI+cs.LG` | 신규(new)·교차(cross) 항목만, 개정(replace) 제외 | 하루 수백 건이라 키워드 사전 필터 필수. 주말에는 신규 공지 없음 |
| **AINews** | news.smol.ai RSS | 최근 1회차 | 하루 1건의 긴 요약본. 원문 전재 금지, 핵심 항목만 재요약하고 원문 링크 |
| **Google Alerts** | 운영자가 만든 Alerts의 RSS URL | 최근 26시간 | 링크가 `google.com/url?...&url=` 형태이므로 실제 URL 추출. 색인 지연으로 1~3일 늦을 수 있음 |
| **Hacker News** | Algolia API `search_by_date` | 최근 24시간, 점수 기준치 이상, AI 키워드 | 기사 본문은 가져오지 않고 제목·링크·점수만 사용 |

**Google Alerts 초기 쿼리 예시** (운영자가 생성, 전달 방식 = RSS 피드)
- `site:linkedin.com/posts ("LLM" OR "AI agent" OR "생성형 AI")`
- `site:linkedin.com/pulse (RAG OR "LLM evaluation")`
- `("금융" OR "카드사") ("생성형 AI" OR LLM)`

**공통**
- 소스별 타임아웃 30초, 재시도 2회
- **한 소스가 실패해도 나머지로 발행**하고, 페이지 하단에 "수집 실패 소스" 표기
- 모든 요청에 식별 가능한 User-Agent 설정, 소스별 호출 간격 준수

## 4. 정규화·중복 제거
- 공통 스키마 `Item`: `source`, `kind(paper|news|community|linkedin)`, `title`, `url`, `canonical_id`, `published_at`, `snippet`, `signals{upvotes, points, ...}`
- `canonical_id` 규칙
  - 논문: arXiv ID (버전 접미사 `v2` 등 제거). HF, arXiv, HN, AINews에 같은 논문이 있으면 하나로 병합하고 신호값을 함께 표시
  - 그 외: 추적 파라미터(`utm_*` 등)를 제거한 URL
- 이전 발행분 재등장 방지: `state/published.json` (30일 보관)

## 5. 선별 규칙
**사전 필터 (코드)**
- arXiv: `sources.yaml`의 키워드가 제목·초록에 포함된 것만
- HF: upvote ≥ 기준치, HN: points ≥ 기준치
- 선별 단계 입력은 최대 150건

**LLM 선별** — `claude-haiku-4-5-20251001`, 20건 단위 배치
- 항목별 1~5점 + 한 줄 근거, JSON 스키마 검증
- 가점: 신규 모델·아키텍처, RAG/에이전트/평가 방법론, 추론 효율화, 엔터프라이즈 적용 사례, 규제·거버넌스, 금융 도메인
- 감점·제외: 홍보성 글, 채용, 근거 없는 전망, 중복 보도
- 섹션별 상위 항목 채택 (6장)

## 6. 브리핑 구성
- 모델: `claude-sonnet-5`
- 한국어, 전문 용어 원문 병기, 모든 항목에 원문 링크
- 요약은 **자체 문장으로 작성**하고 원문 문장을 옮기지 않음

| 섹션 | 개수 | 항목 형식 |
|------|------|-----------|
| 오늘의 헤드라인 | 2~3줄 | 섹션 전체를 관통하는 흐름 |
| 주목할 논문 | 최대 5 | 제목(한/영), 한 줄 핵심, 3줄 요약, 실무 시사점, 링크(arXiv, HF) |
| 업계·기술 동향 | 최대 5 | 제목, 3줄 요약, 왜 중요한가, 출처 |
| LinkedIn 화제 | 최대 3 | 작성자(있으면), 요약, 링크 — 항목이 없으면 섹션 생략 |
| 수집 통계 | 1줄 | 소스별 수집/선별 건수, 실패 소스 |

## 7. 게시·전달
**웹 (GitHub Pages)**
- `site/YYYY-MM-DD.html`, `site/index.html`(최근 30일 목록), `site/feed.xml`(RSS 2.0)
- 정적 HTML만 생성 (프레임워크 없음), 모바일 가독성 우선, 라이트/다크 대응
- 같은 날짜 재실행 시 해당 날짜 페이지만 덮어씀

**메일**
- **발송 전용 Gmail** SMTP, 구독자는 BCC
- 구독자 목록은 저장소가 아니라 GitHub Secrets `SUBSCRIBERS`(쉼표 구분)에 보관
- 제목: `[AI 브리핑] 2026-09-29 — 헤드라인 앞부분`
- 본문: 헤드라인, 섹션별 제목과 한 줄 요약, 웹 페이지 링크

**푸시 (운영자 전용)**
- ntfy: 헤드라인 + 페이지 링크, 실패 시 실패 알림

## 8. 스케줄·운영
- cron `0 21 * * *` (KST 06:00), `workflow_dispatch`에 `date`, `dry_run` 입력
- 전체 실행 10분 이내
- 전체 실패 시: 푸시로 실패 알림 + Actions 로그 링크, 메일 미발송
- 로그: 소스별 수집 건수, 필터 후 건수, 선별 건수, 토큰 사용량과 추정 비용

## 9. 비용·보안·정책
- 월 API 비용 목표 $10 이하, 실행마다 추정 비용 기록
- Secrets: `ANTHROPIC_API_KEY`, `SMTP_USER`, `SMTP_APP_PASSWORD`, `SUBSCRIBERS`, `NTFY_TOPIC`
- 수집 텍스트는 신뢰할 수 없는 입력으로 취급: 프롬프트에서 데이터 영역을 태그로 격리하고, 출력은 스키마 검증 후 HTML 이스케이프
- **공개 게시 전제**: GitHub Pages는 공개 사이트이므로 회사 내부 정보와 구독자 정보는 페이지와 저장소에 넣지 않음
- 저장소는 public 권장 (무료 Pages 사용 + 동료 PR 기여)

## 10. 기술 스택·구조
- Python 3.12, uv, pytest, ruff
- 라이브러리: `anthropic`, `httpx`, `feedparser`, `pydantic`, `jinja2`, `pyyaml`

```
.
├── CLAUDE.md, SPEC.md, sources.yaml
├── prompts/        (select.md, summarize.md)
├── templates/      (day.html.j2, index.html.j2, feed.xml.j2, email.html.j2)
├── src/briefing/
│   ├── sources/    (hf.py, arxiv.py, ainews.py, alerts.py, hn.py)
│   ├── models.py, normalize.py, dedupe.py, prefilter.py
│   └── select.py, summarize.py, render.py, publish.py, notify.py, main.py
├── state/published.json
├── site/           (Pages 게시 대상)
├── tests/fixtures/ (소스별 실제 응답 샘플)
└── .github/workflows/ (daily.yml, ci.yml)
```

## 11. sources.yaml 예시
```yaml
timezone: Asia/Seoul
lookback_hours: 26
hf_papers:
  min_upvotes: 10
arxiv:
  categories: [cs.CL, cs.AI, cs.LG]
  keywords: [RAG, retrieval, agent, evaluation, benchmark, reasoning,
             quantization, inference, financial, fraud]
ainews:
  feed: "<M1에서 확인한 RSS URL>"
google_alerts:
  - name: "LinkedIn - LLM/Agent"
    feed: "https://www.google.com/alerts/feeds/..."
hackernews:
  min_points: 100
  keywords: [LLM, GPT, Claude, Gemini, agent, AI]
limits:
  prefilter_max: 150
  papers: 5
  news: 5
  linkedin: 3
```

## 12. 마일스톤
| # | 내용 | 완료 조건 |
|---|------|-----------|
| M1 | 5개 소스 수집기 + fixture 저장 + `Item` 정규화 | 수동 실행으로 소스별 fixture 저장, pytest 통과 |
| M2 | 중복 제거(arXiv ID 병합 포함) + 사전 필터 | 같은 논문이 여러 소스에 있을 때 1건으로 병합되는 테스트 통과 |
| M3 | LLM 선별·요약 + dry-run(md 출력) | dry-run 결과를 운영자가 읽고 품질 합격 |
| M4 | HTML·RSS 렌더링 + GitHub Pages 게시 | 휴대폰에서 페이지 확인, RSS 리더 구독 성공 |
| M5 | 구독자 메일 + 운영자 푸시 | 본인 포함 2명 수신 확인 |
| M6 | cron 활성화 + 실패 처리 + 비용 로그 | 5일 연속 07:00 이전 발행, 소스 1개 강제 실패 시 부분 발행 확인 |

## 13. 미정 사항
- [ ] AINews RSS URL, HF 응답 필드 확정 (M1)
- [ ] 동료 회사 메일로 외부 발송 메일이 수신되는지 확인 (안 되면 RSS·개인 메일로 안내)
- [ ] upvote·points 기준치는 1주 운영 후 조정
- [ ] 2단계(xAI X Search) 도입 여부는 1단계 4주 운영 후 결정
