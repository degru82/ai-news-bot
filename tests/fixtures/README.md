# Test Fixtures

각 소스별 실제 API/RSS 응답 샘플 (네트워크 없이 테스트하기 위해).

## 수집 내역
- **hf_papers.json**: 2026-10-16 수집 (3개 논문, upvotes >= 10)
- **arxiv.xml**: 평일 데이터 (5개 항목: 2 new, 2 cross, 1 replace)
- **ainews.xml**: 2026-10-16 수집 (최근 2건으로 trimmed)
- **hackernews.json**: 2026-10-16 수집 (6건, AI 키워드·100점 이상)
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
- arXiv는 주말(토/일)에 빈 피드를 반환하므로 평일 데이터를 유지.
- 실제 Google Alerts 피드에는 계정 식별 정보가 있으므로 커밋 전에 제거.
