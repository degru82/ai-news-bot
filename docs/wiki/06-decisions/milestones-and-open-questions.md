# 마일스톤과 미정 사항

## 마일스톤
| # | 내용 |
|---|------|
| M1 | 5개 소스 수집기 + fixture + `Item` 정규화 → [소스 수집](../02-sources/collection.md) |
| M2 | 중복 제거 + 사전 필터 → [중복 제거·선별](../03-pipeline/dedupe-and-selection.md) |
| M3 | LLM 선별·요약 + dry-run → [브리핑 생성](../03-pipeline/briefing.md) |
| M4 | HTML·RSS + Pages 게시 → [게시·전달](../04-delivery/publishing-and-delivery.md) |
| M5 | 구독자 메일 + 운영자 푸시 → 같은 문서 |
| M6 | cron + 실패 처리 + 비용 로그 → [운영·보안](../05-operations/operations-and-security.md) |

완료 조건은 SPEC.md 12장. 마일스톤을 구현하는 PR은 해당 문서의 "변경 이력"에 결정·이유를 남긴다.

## 미정 사항
- AINews RSS URL, HF 응답 필드: M1에서 실응답으로 확정.
- 동료 회사 메일로 외부 발송이 수신되는지: 안 되면 RSS·개인 메일 안내.
- upvote·points 기준치: 1주 운영 후 조정.
- 2단계(유료 API로 X 신호 도입): 1단계 4주 운영 후 결정 — [목표와 범위](../01-overview/goals-and-scope.md)의 "공개 소스만" 결정을 재검토하는 시점.

관련: [목표와 범위](../01-overview/goals-and-scope.md)
