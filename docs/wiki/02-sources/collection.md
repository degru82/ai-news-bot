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
- **미확정(SPEC 13장)**: HF 응답 필드명과 AINews RSS URL은 네트워크가 막힌 환경에서 구현해 실응답으로 확인하지 못했다. `tests/fixtures/`는 손으로 쓴 샘플이며, 운영자가 `--save-fixtures`로 교체한 뒤 필드를 확정해야 M1이 완료된다.

## 변경 이력
- SPEC v2(PR #6): Google Alerts를 LinkedIn 대체 경로로 채택.
- 2026-09-29 (M1, 이슈 #9): 수집기 5종·`Item`·fixture 저장/재생 구현. 위 "M1 구현 결정" 참고.

관련: [목표와 범위](../01-overview/goals-and-scope.md), [중복 제거·선별](../03-pipeline/dedupe-and-selection.md)
