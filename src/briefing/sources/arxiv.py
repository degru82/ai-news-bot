"""arXiv RSS 수집기. 신규(new)·교차(cross) 공지만 남기고 개정(replace)은 제외한다.

주말에는 신규 공지가 없어 빈 목록이 나오며, 이는 실패가 아니다.
"""

import re
from datetime import datetime

from briefing.config import Config
from briefing.feeds import parse_feed
from briefing.http import HttpClient
from briefing.models import Item
from briefing.normalize import extract_arxiv_id, strip_html, truncate

NAME = "arxiv"
EXT = ".xml"
FEED_URL = "https://rss.arxiv.org/rss/"
_ANNOUNCE_RE = re.compile(r"Announce Type:\s*([\w-]+)")
_ABSTRACT_RE = re.compile(r"Abstract:\s*(.*)", re.DOTALL)
_KEPT_TYPES = {"new", "cross"}


def collect(client: HttpClient, config: Config, now: datetime) -> list[Item]:
    text = client.get(FEED_URL + "+".join(config.arxiv.categories))
    items = []
    for entry in parse_feed(text):
        announce = _ANNOUNCE_RE.search(entry.summary)
        if not announce or announce.group(1) not in _KEPT_TYPES:
            continue
        arxiv_id = extract_arxiv_id(entry.link)
        if not arxiv_id:
            continue
        abstract = _ABSTRACT_RE.search(entry.summary)
        items.append(
            Item(
                source=NAME,
                kind="paper",
                title=strip_html(entry.title),
                url=f"https://arxiv.org/abs/{arxiv_id}",
                canonical_id=f"arxiv:{arxiv_id}",
                published_at=entry.published,
                snippet=truncate(strip_html(abstract.group(1) if abstract else "")),
                signals={"announce_type": announce.group(1)},
            )
        )
    return items
