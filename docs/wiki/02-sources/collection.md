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

## 변경 이력
- SPEC v2(PR #6): Google Alerts를 LinkedIn 대체 경로로 채택.

관련: [목표와 범위](../01-overview/goals-and-scope.md), [중복 제거·선별](../03-pipeline/dedupe-and-selection.md)
