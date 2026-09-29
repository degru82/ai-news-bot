from pathlib import Path

from briefing.wiki_sync import page_name, rewrite_links, sync


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_page_name():
    assert page_name(Path("Home.md")) == "Home"
    assert page_name(Path("03-pipeline/briefing.md")) == "03-pipeline-briefing"


def test_rewrite_links_keeps_external_and_anchor(tmp_path):
    root = tmp_path / "wiki"
    src = root / "01-a" / "x.md"
    _write(src, "")
    text = "[y](../02-b/y.md#sec) [ext](https://e.com/a.md) [img](i.png)"
    out = rewrite_links(text, src, root)
    assert out == "[y](02-b-y#sec) [ext](https://e.com/a.md) [img](i.png)"


def test_sync_flattens_and_builds_sidebar(tmp_path):
    root = tmp_path / "wiki"
    _write(root / "Home.md", "# Home\n[x](01-a/x.md)\n")
    _write(root / "01-a" / "x.md", "# 문서 X\n[y](../02-b/y.md)\n")
    _write(root / "02-b" / "y.md", "# 문서 Y\n")
    out = tmp_path / "out"
    _write(out / "stale.md", "old")

    names = sync(root, out)

    assert sorted(names) == ["01-a-x", "02-b-y", "Home"]
    assert not (out / "stale.md").exists()
    assert "[y](02-b-y)" in (out / "01-a-x.md").read_text(encoding="utf-8")
    sidebar = (out / "_Sidebar.md").read_text(encoding="utf-8")
    assert "[문서 X](01-a-x)" in sidebar and "[문서 Y](02-b-y)" in sidebar
