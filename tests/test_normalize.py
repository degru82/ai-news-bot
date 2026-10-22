from briefing.normalize import (
    canonical_id_for_url,
    clean_url,
    extract_arxiv_id,
    strip_html,
    strip_version,
    truncate,
    unwrap_google_url,
)


def test_strip_version():
    assert strip_version("2609.11111v2") == "2609.11111"
    assert strip_version("2609.11111") == "2609.11111"


def test_extract_arxiv_id_drops_version_and_handles_pdf():
    assert extract_arxiv_id("https://arxiv.org/abs/2609.11111v3") == "2609.11111"
    assert extract_arxiv_id("https://arxiv.org/pdf/2609.11111v1.pdf") == "2609.11111"
    assert extract_arxiv_id("https://arxiv.org/abs/hep-th/9901001") == "hep-th/9901001"
    assert extract_arxiv_id("https://example.com/2609.11111") is None


def test_clean_url_removes_tracking_and_fragment():
    url = "HTTPS://Example.com/a/b/?utm_source=x&id=7&fbclid=z#top"
    assert clean_url(url) == "https://example.com/a/b?id=7"


def test_unwrap_google_url():
    wrapped = "https://www.google.com/url?rct=j&url=https://example.com/a%3Fx%3D1&ct=ga"
    assert unwrap_google_url(wrapped) == "https://example.com/a?x=1"
    not_google = "https://example.com/url?url=other"
    assert unwrap_google_url(not_google) == not_google


def test_canonical_id_for_url():
    assert canonical_id_for_url("https://arxiv.org/abs/2609.11111v2") == "arxiv:2609.11111"
    assert canonical_id_for_url("https://example.com/p/?utm_medium=a") == "https://example.com/p"


def test_strip_html_and_truncate():
    assert strip_html("a &lt;b&gt;bold&lt;/b&gt; <i>x</i>  &amp; y") == "a <b>bold</b> x & y"
    assert truncate("abcdef", 4) == "abc…"
    assert truncate("abc", 4) == "abc"
