# 목표와 범위

## 결정
매일 07:00(KST)까지 **공개 소스만으로** 지난 24시간의 AI 동향·논문을 선별·요약해 웹(+RSS)·메일·푸시로 전달한다.

## 배경·이유
- 개인 계정 자격증명 없이 돌아야 동료가 구독하거나 그대로 복제해 쓸 수 있다. 그래서 로그인 수집·스크래핑·유료 API를 금지한다.
- 저장소는 public: 무료 GitHub Pages 사용 + 동료가 `sources.yaml`에 키워드·피드를 PR로 기여.
- 사용자: 운영자(관리), 구독자(읽기), 기여자(키워드·피드 PR).

## 검토한 대안
- X/Threads 등 소셜 직접 수집 — 계정 정지·약관 위반 위험과 "복제 가능" 목표와 충돌해 1단계 제외. 2단계에서 유료 API(xAI X Search)로 재검토 ([미정 사항](../06-decisions/milestones-and-open-questions.md)).
- 논문 PDF 본문 분석 — 비용·복잡도 때문에 초록만 사용.

## 변경 이력
- SPEC v2(PR #6): 공개 소스 중심 1단계로 재정의.

관련: [소스 수집](../02-sources/collection.md), [운영·보안](../05-operations/operations-and-security.md)
