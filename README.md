# ai-news-bot
매일 07:00(KST)까지 **공개 소스만으로** 지난 24시간의 AI 기술·트렌드와 주목할 논문을 선별·요약해,
웹 페이지(+RSS)로 게시하고 구독자에게 메일로, 운영자에게 푸시로 전달하는 일일 배치입니다.
개인 계정 자격증명 없이 동작하므로 동료가 구독하거나 그대로 복제해 쓸 수 있습니다.

## 수집 소스
- HF Daily Papers
- arXiv RSS (cs.CL, cs.AI, cs.LG)
- AINews RSS
- Google Alerts RSS (LinkedIn 게시물 포함)
- Hacker News (Algolia API)

로그인이 필요한 수집, 스크래핑, 유료 수집 API는 사용하지 않습니다.

## 받아 보기
- **웹/RSS**: GitHub Pages의 날짜별 페이지와 `feed.xml` (M4 이후 제공)
- **메일**: 운영자에게 구독 요청 (M5 이후 제공)

## 개발
```bash
uv sync                                               # 설치
uv run pytest                                         # 테스트
uv run ruff check . && uv run ruff format --check .   # 린트
```

요구사항과 마일스톤은 [SPEC.md](SPEC.md), 작업 규칙은 [CLAUDE.md](CLAUDE.md)를 참고하세요.
키워드나 Google Alerts 피드는 `sources.yaml`에 추가하는 PR로 기여할 수 있습니다.
