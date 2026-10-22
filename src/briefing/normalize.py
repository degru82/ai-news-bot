"""URL·ID·텍스트 정규화 도구 (SPEC 4장)."""

import html
import re
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit, urlunsplit

_TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
_BARE_ARXIV_ID = r"(?:[a-z\-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})"
_ARXIV_URL_RE = re.compile(
    rf"arxiv\.org/(?:abs|pdf|html)/({_BARE_ARXIV_ID})(?:v\d+)?", re.IGNORECASE
)
_VERSION_RE = re.compile(r"v\d+$")
_TAG_RE = re.compile(r"<[^>]+>")


def strip_version(arxiv_id: str) -> str:
    return _VERSION_RE.sub("", arxiv_id.strip())


def extract_arxiv_id(url: str) -> str | None:
    """arXiv URL에서 버전 접미사를 뗀 ID를 꺼낸다. arXiv URL이 아니면 None."""
    match = _ARXIV_URL_RE.search(url)
    return match.group(1) if match else None


def clean_url(url: str) -> str:
    """추적 파라미터·프래그먼트·끝 슬래시를 제거한 URL."""
    parts = urlsplit(url.strip())
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.lower().startswith("utm_") and key.lower() not in _TRACKING_PARAMS
    ]
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), "")
    )


def unwrap_google_url(url: str) -> str:
    """`google.com/url?...&url=<실제 URL>` 리다이렉트 링크에서 실제 URL을 꺼낸다."""
    parts = urlsplit(url)
    host = parts.netloc.lower()
    if (host == "google.com" or host.endswith(".google.com")) and parts.path == "/url":
        query = parse_qs(parts.query)
        for key in ("url", "q"):
            if query.get(key):
                return query[key][0]
    return url


def canonical_id_for_url(url: str) -> str:
    """논문 URL이면 `arxiv:<id>`, 그 외에는 정리된 URL."""
    arxiv_id = extract_arxiv_id(url)
    return f"arxiv:{arxiv_id}" if arxiv_id else clean_url(url)


def strip_html(text: str) -> str:
    return " ".join(html.unescape(_TAG_RE.sub(" ", text)).split())


def truncate(text: str, limit: int = 500) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
