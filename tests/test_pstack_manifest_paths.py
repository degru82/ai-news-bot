"""
Test manifest path validation using production validator.

Verifies that the production validator rejects manifests with:
- Path traversal attempts (../)
- Absolute paths
- Paths outside vendor root
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestManifestPathValidation:
    """Test production validator rejects malformed manifest paths."""

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

    def test_validator_rejects_path_traversal(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should reject manifest with ../ path traversal."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Inject path traversal in manifest
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest) as f:
                    lines = f.readlines()
                with open(manifest, "w") as f:
                    # Replace first line with traversal
                    hash_val = "a" * 64
                    f.write(f"{hash_val}  ./../etc/passwd\n")
                    f.writelines(lines[1:])

            returncode, output = self.run_validator(validator_script, tmp_path)
            assert returncode != 0, "Should reject path traversal"
            assert "malformed" in output.lower() or "valid SHA256" in output, (
                f"Expected path validation error: {output}"
            )

    def test_validator_rejects_absolute_paths(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should reject manifest with absolute paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Inject absolute path in manifest
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest) as f:
                    lines = f.readlines()
                with open(manifest, "w") as f:
                    hash_val = "b" * 64
                    f.write(f"{hash_val}  /etc/passwd\n")
                    f.writelines(lines[1:])

            returncode, output = self.run_validator(validator_script, tmp_path)
            assert returncode != 0, "Should reject absolute path"
            assert "malformed" in output.lower() or "valid SHA256" in output, (
                f"Expected path validation error: {output}"
            )

    def test_validator_accepts_valid_relative_paths(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should accept properly formatted relative paths."""
        returncode, output = self.run_validator(validator_script, workspace_root)
        assert returncode == 0, f"Valid manifest should pass: {output}"
