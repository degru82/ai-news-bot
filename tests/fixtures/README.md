# Test Fixtures

각 소스별 API/RSS 응답 샘플 (네트워크 없이 테스트하기 위해).

## 수집 내역
- **hf_papers.json**: 2026-10-16 실제 API 응답 (3개 논문, upvotes >= 10)
- **arxiv.xml**: **SYNTHETIC** - 실제 응답이 아닌 테스트용 샘플
  - 실제 arXiv RSS 피드가 비어있었음 (2026-10-16 금요일 밤, 2026-10-19 월요일 새벽 확인 시 모두 빈 피드)
  - arXiv는 일반적으로 일요일 밤 ~20:00 UTC에 월요일 논문을 게시하므로, 그 이전에는 빈 피드 반환
  - 파서 테스트를 위해 arXiv RSS 형식을 따르는 합성 샘플 사용 (5개 항목: 2 new, 2 cross, 1 replace)
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
- **arXiv는 합성 샘플**: 실제 피드가 비어있어 파서 로직 테스트용 샘플 사용. 파일 상단 주석 참고.
- arXiv는 주말(토/일)과 게시 전 시간에 빈 피드를 반환.
- 실제 Google Alerts 피드에는 계정 식별 정보가 있으므로 커밋 전에 제거.
