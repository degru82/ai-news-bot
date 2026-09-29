"""Google Alerts RSS(Atom) 수집기. 최근 `lookback_hours` 이내 항목만 남긴다.

피드 URL에는 계정 식별 정보가 들어 있으므로 오류 메시지에는 피드 이름만 쓴다.
"""

import logging
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from briefing.config import Config
from briefing.feeds import parse_feed
from briefing.http import HttpClient
from briefing.models import Item
from briefing.normalize import (
    canonical_id_for_url,
    clean_url,
    strip_html,
    truncate,
    unwrap_google_url,
)

NAME = "google_alerts"
EXT = ".xml"
log = logging.getLogger(__name__)


def collect(client: HttpClient, config: Config, now: datetime) -> list[Item]:
    cutoff = now - timedelta(hours=config.lookback_hours)
    items: list[Item] = []
    failed: list[str] = []
    for alert in config.google_alerts:
        try:
            entries = parse_feed(client.get(alert.feed))
        except Exception as exc:
            failed.append(alert.name)
            log.warning("google_alerts feed %r failed: %s", alert.name, type(exc).__name__)
            continue
        for entry in entries:
            if not entry.link or (entry.published and entry.published < cutoff):
                continue
            url = clean_url(unwrap_google_url(entry.link))
            host = urlsplit(url).netloc
            items.append(
                Item(
                    source=NAME,
                    kind="linkedin" if host.endswith("linkedin.com") else "news",
                    title=strip_html(entry.title),
                    url=url,
                    canonical_id=canonical_id_for_url(url),
                    published_at=entry.published,
                    snippet=truncate(strip_html(entry.summary)),
                    signals={"alert": alert.name},
                )
            )
    if failed and len(failed) == len(config.google_alerts):
        raise RuntimeError("all alert feeds failed: " + ", ".join(failed))
    return items
