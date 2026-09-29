"""HF Daily Papers 수집기.

응답 필드명(`paper.id`, `paper.upvotes`, `paper.githubRepo` 등)은 알려진 형태를 가정한 것이며,
실제 응답으로 `--save-fixtures` 를 돌려 확정해야 한다 (SPEC 13장).
"""

import json
from datetime import UTC, datetime

from briefing.config import Config
from briefing.feeds import parse_datetime
from briefing.http import HttpClient
from briefing.models import Item
from briefing.normalize import strip_html, strip_version, truncate

NAME = "hf_papers"
EXT = ".json"
API_URL = "https://huggingface.co/api/daily_papers"


def collect(client: HttpClient, config: Config, now: datetime) -> list[Item]:
    date = now.astimezone(UTC).date().isoformat()
    entries = json.loads(client.get(API_URL, {"date": date}))
    items = []
    for entry in entries:
        paper = entry.get("paper") or entry
        paper_id = paper.get("id")
        title = paper.get("title") or entry.get("title")
        if not paper_id or not title:
            continue
        upvotes = int(paper.get("upvotes", entry.get("upvotes", 0)) or 0)
        if upvotes < config.hf_papers.min_upvotes:
            continue
        signals: dict[str, int | str] = {"upvotes": upvotes}
        if paper.get("githubRepo"):
            signals["github_repo"] = paper["githubRepo"]
        if paper.get("githubStars") is not None:
            signals["github_stars"] = int(paper["githubStars"])
        if entry.get("numComments") is not None:
            signals["comments"] = int(entry["numComments"])
        arxiv_id = strip_version(paper_id)
        items.append(
            Item(
                source=NAME,
                kind="paper",
                title=strip_html(title),
                url=f"https://huggingface.co/papers/{arxiv_id}",
                canonical_id=f"arxiv:{arxiv_id}",
                published_at=parse_datetime(paper.get("publishedAt") or entry.get("publishedAt")),
                snippet=truncate(strip_html(paper.get("summary") or entry.get("summary") or "")),
                signals=signals,
            )
        )
    return items
