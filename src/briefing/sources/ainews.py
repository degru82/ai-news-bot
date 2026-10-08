"""AINews(news.smol.ai) RSS 수집기. 가장 최근 1회차만 가져온다.

하루 1건의 긴 요약본이므로 스니펫만 남기고, 원문 전재는 하지 않는다.
"""

from datetime import UTC, datetime

from briefing.config import Config
from briefing.feeds import parse_feed
from briefing.http import HttpClient
from briefing.models import Item
from briefing.normalize import clean_url, strip_html, truncate

NAME = "ainews"
EXT = ".xml"


def collect(client: HttpClient, config: Config, now: datetime) -> list[Item]:
    entries = [e for e in parse_feed(client.get(config.ainews.feed)) if e.link]
    if not entries:
        return []
    latest = max(entries, key=lambda e: e.published or datetime.min.replace(tzinfo=UTC))
    return [
        Item(
            source=NAME,
            kind="news",
            title=strip_html(latest.title),
            url=latest.link,
            canonical_id=clean_url(latest.link),
            published_at=latest.published,
            snippet=truncate(strip_html(latest.summary)),
        )
    ]
