# Test Fixtures

각 소스별 API/RSS 응답 샘플 (네트워크 없이 테스트하기 위해).

## 수집 내역
- **hf_papers.json**: 2026-10-16 실제 API 응답 (3개 논문, upvotes >= 10)
- **arxiv.xml**: 2026-10-20 실제 RSS 응답 (7개 항목: 3 new, 2 cross, 2 replace)
  - HTTP 200, 757 items in feed
  - 파서는 new와 cross만 수집(5건), replace는 제외
- **ainews.xml**: 2026-10-16 실제 RSS 응답 (최근 2건으로 trimmed)
- **hackernews.json**: 2026-10-16 실제 API 응답 (6건, AI 키워드·100점 이상)
- **google_alerts.xml**: 샘플 데이터 (lookback 날짜는 2026-10-16 기준)

## 재수집
실제 응답을 다시 수집하려면:
```bash
uv run python -m briefing.main --save-fixtures tests/fixtures-new --date YYYY-MM-DD
```

파일명은 `<소스 NAME><확장자>` (`hf_papers.json`, `arxiv.xml`, `ainews.xml`,
`google_alerts.xml`, `hackernews.json`). Google Alerts 피드가 여러 개면 `google_alerts-2.xml`처럼
순번이 붙는다.

## 주의
- JSON과 XML을 직접 편집하면 파서가 예상과 다르게 동작할 수 있음.
- arXiv는 주말(토/일)과 게시 전 시간(일요일 밤 ~20:00 UTC 이전)에 빈 피드를 반환.
- 실제 Google Alerts 피드에는 계정 식별 정보가 있으므로 커밋 전에 제거.
