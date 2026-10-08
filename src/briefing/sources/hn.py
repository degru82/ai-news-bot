"""Hacker News(Algolia) 수집기. 제목·링크·점수만 쓰고 기사 본문은 가져오지 않는다."""

import json
import re
from datetime import datetime, timedelta

from briefing.config import Config
from briefing.feeds import parse_datetime
from briefing.http import HttpClient
from briefing.models import Item
from briefing.normalize import canonical_id_for_url, strip_html

NAME = "hackernews"
EXT = ".json"
API_URL = "https://hn.algolia.com/api/v1/search_by_date"
ITEM_URL = "https://news.ycombinator.com/item?id="


def _keyword_pattern(keywords: list[str]) -> re.Pattern[str] | None:
    if not keywords:
        return None
    alternatives = "|".join(re.escape(k) for k in keywords)
    return re.compile(rf"(?<!\w)(?:{alternatives})(?!\w)", re.IGNORECASE)


def collect(client: HttpClient, config: Config, now: datetime) -> list[Item]:
    cfg = config.hackernews
    since = int((now - timedelta(hours=24)).timestamp())
    params = {
        "tags": "story",
        "numericFilters": f"created_at_i>{since},points>={cfg.min_points}",
        "hitsPerPage": 1000,
    }
    pattern = _keyword_pattern(cfg.keywords)
    items = []
    for hit in json.loads(client.get(API_URL, params)).get("hits", []):
        title = hit.get("title")
        points = int(hit.get("points") or 0)
        if not title or points < cfg.min_points:
            continue
        if pattern and not pattern.search(title):
            continue
        discussion = ITEM_URL + str(hit["objectID"])
        url = hit.get("url") or discussion
        items.append(
            Item(
                source=NAME,
                kind="community",
                title=strip_html(title),
                url=url,
                canonical_id=canonical_id_for_url(url),
                published_at=parse_datetime(hit.get("created_at")),
                signals={
                    "points": points,
                    "comments": int(hit.get("num_comments") or 0),
                    "discussion_url": discussion,
                },
            )
        )
    return items
