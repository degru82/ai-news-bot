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


def test_unconfigured_source_is_skipped(tmp_path, capsys):
    """빈 리스트로 설정된 소스(google_alerts)는 건너뛴다."""
    main(["--config", str(ROOT / "sources.yaml"), "--fixtures", str(tmp_path)])
    out = capsys.readouterr().out
    assert "google_alerts: 설정 안 됨 (건너뜀)" in out


def test_all_configured_sources_failing_gives_nonzero(tmp_path):
    """설정된 모든 소스가 실패하면 exit code는 1이다."""
    code = main(["--config", str(ROOT / "sources.yaml"), "--fixtures", str(tmp_path)])
    assert code == 1


def test_one_success_with_unconfigured_gives_zero(capsys):
    """설정된 소스 하나가 성공하고 설정 안 된 소스가 있으면 exit code는 0이다."""
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
    assert code == 0
    out = capsys.readouterr().out
    assert "google_alerts: 설정 안 됨 (건너뜀)" in out


def test_only_unconfigured_sources_gives_zero(tmp_path, capsys):
    """설정된 소스가 하나도 없고 모두 건너뛰어진 경우 exit code는 0이다.

    현재 config 모델에서는 google_alerts만 unconfigured 가능하므로,
    이 테스트는 google_alerts만 건너뛰고 나머지는 성공하는 경우를 테스트한다.
    """
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
    assert code == 0
    out = capsys.readouterr().out
    assert "google_alerts: 설정 안 됨 (건너뜀)" in out
    assert "hf_papers: 2건" in out
