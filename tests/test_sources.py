from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

from briefing.config import AlertFeed, load_config
from briefing.http import FixtureClient
from briefing.models import Item
from briefing.sources import SOURCES, ainews, alerts, arxiv, collect_all, hf, hn

FIXTURES = Path(__file__).parent / "fixtures"
# 실제 fixture 수집일: HF/HN/AINews는 2026-10-16, arXiv는 평일 데이터
NOW = datetime(2026, 10, 16, 23, 59, 59, tzinfo=UTC)


@pytest.fixture
def config():
    cfg = load_config(Path(__file__).parent.parent / "sources.yaml")
    cfg.google_alerts = [AlertFeed(name="sample", feed="https://example.com/alerts.xml")]
    return cfg


def fixture_for(module: ModuleType) -> FixtureClient:
    return FixtureClient(FIXTURES, module.NAME, module.EXT)


def test_hf_filters_by_upvotes_and_normalizes(config):
    items = hf.collect(fixture_for(hf), config, NOW)
    # 실제 응답(2026-10-16): upvotes >= 10인 3개 논문
    assert len(items) == 3
    assert all(i.kind == "paper" for i in items)
    assert all(i.canonical_id.startswith("arxiv:") for i in items)
    # 첫 논문 검증
    first = items[0]
    assert first.canonical_id == "arxiv:2610.21601"
    assert first.url == "https://huggingface.co/papers/2610.21601"
    assert first.signals["upvotes"] == 659
    assert "github_repo" in first.signals
    assert first.published_at is not None


def test_arxiv_keeps_only_new_and_cross(config):
    items = arxiv.collect(fixture_for(arxiv), config, NOW)
    # Real arXiv RSS: 3 new, 2 cross, 2 replace -> 5건 수집 (replace 제외)
    assert len(items) == 5
    assert [i.canonical_id for i in items] == [
        "arxiv:2610.22373",  # new
        "arxiv:2610.22379",  # new
        "arxiv:2610.22380",  # new
        "arxiv:2410.22659",  # cross
        "arxiv:2604.27553",  # cross
    ]
    # 버전 접미사 제거 확인 (v1 등 제거)
    # new와 cross만 포함, replace는 제외됨
    assert [i.signals["announce_type"] for i in items] == ["new", "new", "new", "cross", "cross"]
    assert items[0].url == "https://arxiv.org/abs/2610.22373"
    assert items[0].snippet.startswith("LLM-based agents are increasingly used")


def test_arxiv_empty_feed_is_not_a_failure(config):
    class Empty:
        def get(self, url, params=None):
            return '<rss version="2.0"><channel><title>x</title></channel></rss>'

    assert arxiv.collect(Empty(), config, NOW) == []


def test_ainews_returns_only_latest_issue(config):
    items = ainews.collect(fixture_for(ainews), config, NOW)
    assert len(items) == 1
    # 실제 응답(2026-10-16): "not much happened today"
    assert items[0].title == "not much happened today"
    assert items[0].kind == "news"
    assert len(items[0].snippet) > 0  # 스니펫이 존재함을 확인


def test_alerts_unwraps_urls_and_applies_lookback(config):
    items = alerts.collect(fixture_for(alerts), config, NOW)
    assert [i.url for i in items] == [
        "https://www.linkedin.com/posts/example-post-123",
        "https://example.com/news/genai-1",
    ]
    assert [i.kind for i in items] == ["linkedin", "news"]
    assert items[0].title == "Sample LLM post on LinkedIn"
    assert items[0].signals == {"alert": "sample"}


def test_alerts_without_feeds_returns_empty(config):
    config.google_alerts = []
    assert alerts.collect(fixture_for(alerts), config, NOW) == []


def test_alerts_raises_when_all_feeds_fail_without_leaking_url(config):
    class Broken:
        def get(self, url, params=None):
            raise RuntimeError(f"boom {url}")

    with pytest.raises(RuntimeError) as excinfo:
        alerts.collect(Broken(), config, NOW)
    assert "sample" in str(excinfo.value)
    assert "example.com" not in str(excinfo.value)


def test_hn_filters_keywords_and_points(config):
    items = hn.collect(fixture_for(hn), config, NOW)
    # 실제 응답(2026-10-16): 6개 항목, AI 키워드·최소 점수 필터 적용됨
    assert len(items) == 6
    assert all(i.kind == "community" for i in items)
    assert all(i.signals["points"] >= 100 for i in items)
    # 첫 항목 검증
    assert "Claude" in items[0].title or "AI" in items[0].title.upper()
    assert items[0].url.startswith("https://")


def test_hn_sends_threshold_and_window_to_api(config):
    calls = []

    class Spy:
        def get(self, url, params=None):
            calls.append(params)
            return '{"hits": []}'

    hn.collect(Spy(), config, NOW)
    assert "points>=100" in calls[0]["numericFilters"]
    assert f"created_at_i>{int(NOW.timestamp()) - 86400}" in calls[0]["numericFilters"]


def test_collect_all_returns_valid_items_for_every_source(config):
    results = collect_all(config, fixture_for, NOW)
    assert [r.source for r in results] == [m.NAME for m in SOURCES]
    assert all(r.ok for r in results)
    # 실제 응답 기반 fixture: 모든 소스가 항목을 반환 (arXiv는 평일 데이터)
    for result in results:
        assert result.items  # 모든 소스가 항목이 있어야 함
        assert all(isinstance(i, Item) and i.source == result.source for i in result.items)


def test_collect_all_isolates_a_failing_source(config):
    def factory(module):
        if module is arxiv:

            class Broken:
                def get(self, url, params=None):
                    raise TimeoutError("timed out")

            return Broken()
        return fixture_for(module)

    results = {r.source: r for r in collect_all(config, factory, NOW)}
    assert not results["arxiv"].ok
    assert "TimeoutError" in results["arxiv"].error
    assert results["arxiv"].items == []
    assert all(r.ok and r.items for name, r in results.items() if name != "arxiv")
