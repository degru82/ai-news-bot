from pathlib import Path

from briefing.config import load_config
from briefing.main import main

ROOT = Path(__file__).parent.parent


def test_sources_yaml_loads():
    config = load_config(ROOT / "sources.yaml")
    assert config.arxiv.categories == ["cs.CL", "cs.AI", "cs.LG"]
    assert config.hackernews.min_points == 100


def test_dry_run_with_fixtures(capsys):
    code = main(
        [
            "--dry-run",
            "--date",
            "2026-09-29",
            "--config",
            str(ROOT / "sources.yaml"),
            "--fixtures",
            str(ROOT / "tests" / "fixtures"),
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "hf_papers: 2건" in out
    assert "arxiv: 2건" in out
    assert "ainews: 1건" in out
    assert "hackernews: 3건" in out


def test_failure_of_every_source_returns_nonzero(tmp_path, capsys):
    code = main(["--config", str(ROOT / "sources.yaml"), "--fixtures", str(tmp_path)])
    assert code == 1
    assert "수집 실패" in capsys.readouterr().out
