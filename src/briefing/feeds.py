"""RSS 2.0 / Atom 피드를 표준 라이브러리로 파싱한다."""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime


@dataclass(frozen=True)
class FeedEntry:
    title: str
    link: str
    summary: str
    published: datetime | None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_feed(text: str) -> list[FeedEntry]:
    if "<!ENTITY" in text:
        raise ValueError("feed contains entity declarations")
    root = ET.fromstring(text)
    entries = []
    for node in root.iter():
        if _local(node.tag) not in ("item", "entry"):
            continue
        fields: dict[str, str] = {}
        link = ""
        for child in node:
            name = _local(child.tag)
            if name == "link":
                href = child.get("href")
                if href and child.get("rel", "alternate") == "alternate":
                    link = link or href
                elif not href and child.text:
                    link = link or child.text.strip()
            elif child.text and child.text.strip():
                fields.setdefault(name, child.text.strip())
        summary = fields.get("description") or fields.get("summary") or fields.get("content", "")
        published = (
            fields.get("pubDate")
            or fields.get("published")
            or fields.get("updated")
            or fields.get("date")
        )
        entries.append(
            FeedEntry(
                title=fields.get("title", ""),
                link=link,
                summary=summary,
                published=parse_datetime(published),
            )
        )
    return entries
