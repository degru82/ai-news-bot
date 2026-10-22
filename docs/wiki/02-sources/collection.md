# 소스 수집

## 결정
HF Daily Papers, arXiv RSS, AINews RSS, Google Alerts RSS, Hacker News(Algolia) 5개. 모두 `Item` 리스트를 반환하는 같은 인터페이스(`sources/` 모듈당 1소스).

## 배경·이유
| 소스 | 채택 이유 / 주의 |
|------|------------------|
| HF Daily Papers | 커뮤니티가 걸러 준 논문 신호(upvote). 응답 필드는 M1에서 실응답으로 확정 |
| arXiv RSS | 논문 원천. 하루 수백 건이라 키워드 사전 필터 필수, 주말 0건은 실패가 아님 |
| AINews | 하루 1건 요약본. 원문 전재 금지, 핵심만 재요약+링크 |
| Google Alerts | 로그인 없이 LinkedIn 등 소셜 신호를 얻는 경로. 리다이렉트 URL 해제 필요, 1~3일 지연 가능 |
| Hacker News | 커뮤니티 반응. 제목·링크·점수만 사용(본문 스크래핑 금지) |

- 인터페이스 통일: 이후 단계(정규화·중복 제거)가 소스를 몰라도 되도록.
- 소스별 예외 격리: 한 소스 실패로 07:00 발행이 막히지 않도록 실패를 결과 객체에 기록하고 페이지에 "수집 실패 소스"로 표기.
- 타임아웃 30초·재시도 2회·식별 가능한 User-Agent·호출 간격 준수: 공개 서비스에 차단당하지 않기 위한 최소 예의.

## M1 구현 결정
- **수집기 계약**: `sources/<소스>.py`마다 `NAME`, `EXT`, `collect(client, config, now) -> list[Item]`. `collect_all`이 소스별로 예외를 잡아 `FetchResult.error`에 기록한다. 이후 단계는 결과 객체만 보면 된다.
- **HTTP는 인터페이스 뒤에**: `HttpClient.get(url, params) -> str`. 실제(`HttpxClient`: 타임아웃 30초, 5xx·429·네트워크 오류만 2회 재시도, 소스별 호출 간격 1초, 식별 User-Agent), 녹화(`RecordingClient`), 재생(`FixtureClient`) 3종. 테스트는 네트워크 없이 fixture만 쓴다.
- **fixture 저장**: `--save-fixtures DIR`로 실제 응답을 `<NAME><확장자>`로 저장, `--fixtures DIR`로 재생. 수집기 로직을 실응답 기준으로 다듬는 루프를 네트워크 없이 돌리기 위함.
- **RSS는 표준 라이브러리로 파싱**(`feeds.py`, RSS 2.0·Atom 공통): SPEC 10장은 `feedparser`를 예시했으나, 필요한 필드가 제목·링크·요약·날짜뿐이라 의존성 추가(및 lock 갱신)를 피했다. 엔티티 선언이 있는 피드는 거부한다. 추정: 필요가 커지면 `feedparser`로 교체해도 `FeedEntry` 인터페이스는 유지된다.
- **논문 canonical_id**: arXiv URL이면 `arxiv:<버전 제거 ID>`로 통일(HF·arXiv·HN이 같은 논문이면 M2에서 병합 가능). HN은 arXiv 링크일 때만 이 규칙을 따르고 `kind`는 `community`로 둔다.
- **HN 키워드 필터를 M1에 포함**: Algolia는 여러 키워드 OR 검색이 없어 점수·기간은 서버에서, 키워드(단어 경계, 대소문자 무시)는 코드에서 거른다. HF의 upvote 기준도 수집 단계에서 적용한다. arXiv 키워드 필터와 상한 150건은 M2(사전 필터)에서.
- **Google Alerts**: 오류 메시지에는 피드 이름만 쓴다(피드 URL에 계정 식별 정보가 있고 Actions 로그는 공개될 수 있음). 피드 일부만 실패하면 로그 경고 후 나머지로 진행하고, 전부 실패할 때만 소스 실패로 기록한다.
- **미설정 소스 처리 정책**: 설정되지 않은 소스(예: `google_alerts: []`)는 `FetchResult.skipped=True`로 표시하고 종료 코드 판정에서 제외한다. 종료 코드 1은 설정된 모든 소스가 실패했을 때만 반환한다. 이유: 미설정 Alerts 소스가 성공(0건)으로 카운트되면, 나머지 소스 전체의 장애가 가려져 운영자가 알림을 받지 못할 수 있다.
- **실응답 확인 완료(#13, #14, #15)**: 2026-10-16/20 네트워크 연결 환경에서 실응답 수집 및 확정.
  - **HF Daily Papers API (#14)**: `https://huggingface.co/api/daily_papers?date=YYYY-MM-DD`. 응답은 논문 배열, 각 항목에 최상위 필드(`publishedAt`, `title`, `numComments`)와 중첩 `paper` 객체(`id`, `upvotes`, `githubRepo`, `githubStars`) 포함. 수집기는 `paper.githubRepo` → `signals["github_repo"]`로 정규화. 필드 매핑 정상 동작 확인.
  - **AINews RSS URL (#15)**: `https://news.smol.ai/rss.xml` (초기 추측이 정확함). RSS 2.0 포맷, 정상 수집 확인 (파서는 최신 1건만 사용).
  - **실제 fixture 교체 (#13)**: `tests/fixtures/`의 HF, arXiv, AINews, HN을 실제 API/RSS 응답으로 교체. HF 3건 (2026-10-16), arXiv 7건 (2026-10-20, 757 items in feed, HTTP 200: 3 new + 2 cross + 2 replace, 파서는 new/cross 5건만 수집), AINews 1건 (2026-10-16, 파서는 최신 1건만 사용), HN 6건 (2026-10-16). Google Alerts는 샘플 유지 (피드 URL에 계정 정보 포함, 현재 미설정). 테스트는 실응답 기준으로 수정됨. `uv run pytest` 전체 통과.

## 변경 이력
- SPEC v2(PR #6): Google Alerts를 LinkedIn 대체 경로로 채택.
- 2026-09-29 (M1, 이슈 #9): 수집기 5종·`Item`·fixture 저장/재생 구현. 위 "M1 구현 결정" 참고.

관련: [목표와 범위](../01-overview/goals-and-scope.md), [중복 제거·선별](../03-pipeline/dedupe-and-selection.md)
