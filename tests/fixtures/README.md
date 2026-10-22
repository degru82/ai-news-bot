# fixtures

현재 파일은 **손으로 작성한 샘플**이며 실제 응답이 아니다 (네트워크가 막힌 환경에서 작성).
운영자가 실제 응답으로 교체한다.

```
uv run python -m briefing.main --save-fixtures tests/fixtures
```

파일명은 `<소스 NAME><확장자>` (`hf_papers.json`, `arxiv.xml`, `ainews.xml`,
`google_alerts.xml`, `hackernews.json`). Google Alerts 피드가 여러 개면 `google_alerts-2.xml`처럼
순번이 붙는다. 실제 Alerts 피드에는 계정 식별 정보가 있으므로 커밋 전에 지운다.
