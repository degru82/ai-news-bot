from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest

from briefing.config import AlertFeed, load_config
from briefing.http import FixtureClient
from briefing.models import Item
from briefing.sources import SOURCES, ainews, alerts, arxiv, collect_all, hf, hn

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 9, 29, 7, 0, tzinfo=UTC)


@pytest.fixture
def config():
    cfg = load_config(Path(__file__).parent.parent / "sources.yaml")
    cfg.google_alerts = [AlertFeed(name="sample", feed="https://example.com/alerts.xml")]
    return cfg


def fixture_for(module: ModuleType) -> FixtureClient:
    return FixtureClient(FIXTURES, module.NAME, module.EXT)


def test_hf_filters_by_upvotes_and_normalizes(config):
    items = hf.collect(fixture_for(hf), config, NOW)
    assert [i.canonical_id for i in items] == ["arxiv:2609.11111", "arxiv:2609.22222"]
    first = items[0]
    assert first.kind == "paper"
    assert first.url == "https://huggingface.co/papers/2609.11111"
    assert first.signals == {
        "upvotes": 45,
        "github_repo": "https://github.com/example/paper-a",
        "github_stars": 120,
        "comments": 3,
    }
    assert first.published_at is not None


def test_arxiv_keeps_only_new_and_cross(config):
    items = arxiv.collect(fixture_for(arxiv), config, NOW)
    assert [i.canonical_id for i in items] == ["arxiv:2609.11111", "arxiv:2609.44444"]
    assert [i.signals["announce_type"] for i in items] == ["new", "cross"]
    assert items[0].url == "https://arxiv.org/abs/2609.11111"
    assert items[0].snippet.startswith("Sample abstract")


def test_arxiv_empty_feed_is_not_a_failure(config):
    class Empty:
        def get(self, url, params=None):
            return '<rss version="2.0"><channel><title>x</title></channel></rss>'

    assert arxiv.collect(Empty(), config, NOW) == []


def test_ainews_returns_only_latest_issue(config):
    items = ainews.collect(fixture_for(ainews), config, NOW)
    assert len(items) == 1
    assert items[0].title == "[AINews] Sample latest issue"
    assert items[0].kind == "news"
    assert items[0].snippet == "Latest sample issue summary with markup ."


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
    assert [i.title for i in items] == [
        "Show HN: A sample LLM inference server",
        "Sample paper discussion: agent benchmarks",
        "Ask HN: Sample question about Claude usage",
    ]
    assert items[0].canonical_id == "https://example.com/llm-server"
    assert items[1].canonical_id == "arxiv:2609.11111"
    assert items[2].url == "https://news.ycombinator.com/item?id=45000003"
    assert items[0].signals["points"] == 250
    assert all(i.kind == "community" for i in items)


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
    for result in results:
        assert result.items
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
