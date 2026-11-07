"""
Test that validator detects manifest path substitution attacks.

A substitution attack replaces a valid hash+path with a different valid hash
pointing to a path outside the vendor tree, while keeping the file count correct.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestManifestPathSubstitution:
    """Test production validator detects path substitution."""

    @pytest.fixture
    def workspace_root(self) -> Path:
        """Return the actual workspace root."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def validator_script(self, workspace_root: Path) -> Path:
        """Return path to the production validator script."""
        script = workspace_root / "scripts" / "verify-pstack-integration.sh"
        assert script.exists(), "Validator script must exist"
        return script

    def run_validator(self, validator_script: Path, target_dir: Path) -> tuple[int, str]:
        """Run the production validator."""
        result = subprocess.run(
            ["bash", str(validator_script), str(target_dir)],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout + result.stderr

    def test_validator_detects_substituted_path(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should detect when manifest has valid hash but substituted external path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Create external file
            external_file = tmp_path / "outside.txt"
            external_file.write_text("external content")

            # Get hash of external file
            import hashlib

            external_hash = hashlib.sha256(b"external content").hexdigest()

            # Replace logo.png entry with external path but keep file count same
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest) as f:
                    lines = f.readlines()

                with open(manifest, "w") as f:
                    for line in lines:
                        # Replace logo.png entry with external path
                        if "./assets/logo.png" in line:
                            f.write(f"{external_hash}  ./../../../outside.txt\n")
                        else:
                            f.write(line)

            returncode, output = self.run_validator(validator_script, tmp_path)
            assert returncode != 0, f"Should detect path substitution, but got: {output}"
            assert "do not match" in output.lower() or "mismatch" in output.lower(), (
                f"Expected path set mismatch error: {output}"
            )
