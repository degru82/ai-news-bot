# ai-news-bot 설계 위키

최종 요구사항은 저장소의 [SPEC.md](https://github.com/degru82/ai-news-bot/blob/main/SPEC.md)가 기준이고,
이 위키는 **왜 그렇게 정했는지(배경·검토·이유)** 를 남긴다. 원본은 저장소의 `docs/wiki/`이며
main에 머지되면 자동으로 이 위키에 동기화된다. 위키에서 직접 수정하지 않는다.

## 읽는 순서
1. [목표와 범위](01-overview/goals-and-scope.md) — 무엇을, 왜 만드는가
2. [소스 수집](02-sources/collection.md) — 5개 소스와 선택 이유
3. [중복 제거·선별](03-pipeline/dedupe-and-selection.md) → [브리핑 생성](03-pipeline/briefing.md)
4. [게시·전달](04-delivery/publishing-and-delivery.md)
5. [운영·보안](05-operations/operations-and-security.md)
6. [마일스톤과 미정 사항](06-decisions/milestones-and-open-questions.md)

## 위키 작성 규칙
[작성 가이드](00-guide/how-to-write.md) 참고. 매 PR마다 결정·변경의 배경을 이 위키에 남긴다.
