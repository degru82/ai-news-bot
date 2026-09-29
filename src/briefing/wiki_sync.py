"""docs/wiki/<섹션>/<문서>.md 를 GitHub Wiki(평면 구조)용 파일로 변환한다.

- `docs/wiki/03-pipeline/briefing.md` -> `03-pipeline-briefing.md` (위키 페이지 이름)
- 문서 사이의 상대 링크(`../02-sources/collection.md`)는 위키 링크(`02-sources-collection`)로 바꾼다.
- `docs/wiki/Home.md`는 그대로 `Home.md`, `_Sidebar.md`는 섹션 구조에서 생성한다.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)\s]+?\.md)(#[^)\s]*)?\)")


def page_name(rel: Path) -> str:
    """docs/wiki 기준 상대 경로를 위키 페이지 이름으로 바꾼다."""
    if len(rel.parts) == 1:
        return rel.stem
    return "-".join([*rel.parts[:-1], rel.stem])


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def rewrite_links(text: str, src: Path, root: Path) -> str:
    """`src`(root 기준 문서) 안의 상대 .md 링크를 위키 링크로 바꾼다."""

    def repl(m: re.Match[str]) -> str:
        label, target, anchor = m.group(1), m.group(2), m.group(3) or ""
        if "://" in target:
            return m.group(0)
        resolved = (src.parent / target).resolve()
        try:
            rel = resolved.relative_to(root.resolve())
        except ValueError:
            return m.group(0)
        return f"[{label}]({page_name(rel)}{anchor})"

    return _LINK.sub(repl, text)


def collect(root: Path) -> list[Path]:
    """Home.md 와 `<섹션>/*.md` 문서를 정렬해 반환한다."""
    pages = [p for p in root.glob("*/*.md")]
    home = root / "Home.md"
    if home.exists():
        pages.append(home)
    return sorted(pages)


def build_sidebar(root: Path, pages: list[Path]) -> str:
    lines = ["**[[Home]]**", ""]
    section = None
    for p in pages:
        rel = p.relative_to(root)
        if len(rel.parts) == 1:
            continue
        if rel.parts[0] != section:
            section = rel.parts[0]
            lines += ["", f"**{section}**"]
        title = _title(p.read_text(encoding="utf-8"), rel.stem)
        lines.append(f"- [{title}]({page_name(rel)})")
    return "\n".join(lines) + "\n"


def sync(root: Path, out: Path) -> list[str]:
    """변환 결과를 `out`에 쓴다. out의 기존 *.md는 지우고(.git은 유지) 다시 채운다."""
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.md"):
        old.unlink()
    pages = collect(root)
    written = []
    for p in pages:
        rel = p.relative_to(root)
        text = rewrite_links(p.read_text(encoding="utf-8"), p, root)
        name = page_name(rel)
        (out / f"{name}.md").write_text(text, encoding="utf-8")
        written.append(name)
    (out / "_Sidebar.md").write_text(build_sidebar(root, pages), encoding="utf-8")
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", type=Path, default=Path("docs/wiki"))
    ap.add_argument("--out", type=Path, required=True, help="체크아웃한 <repo>.wiki 디렉터리")
    args = ap.parse_args()
    if not args.src.is_dir():
        raise SystemExit(f"소스 디렉터리가 없습니다: {args.src}")
    names = sync(args.src, args.out)
    print(f"{len(names)}개 페이지 동기화: {', '.join(names)}")


if __name__ == "__main__":
    main()
