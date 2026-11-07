"""
Test pstack integration verification with negative tests.

These tests verify the PRODUCTION validator (scripts/verify-pstack-integration.sh)
correctly detects missing or corrupted files by running it against mutated fixture roots.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


class TestPstackIntegrationValidator:
    """Test the production pstack integration validator."""

    @pytest.fixture
    def workspace_root(self) -> Path:
        """Return the actual workspace root."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def validator_script(self, workspace_root: Path) -> Path:
        """Return path to the production validator script."""
        script = workspace_root / "scripts" / "verify-pstack-integration.sh"
        assert script.exists(), "Validator script must exist"
        assert script.stat().st_mode & 0o111, "Validator must be executable"
        return script

    def run_validator_in_dir(self, validator_script: Path, target_dir: Path) -> tuple[int, str]:
        """Run the production validator in a specific directory."""
        result = subprocess.run(
            ["bash", str(validator_script), str(target_dir)],
            capture_output=True,
            text=True,
        )
        return result.returncode, result.stdout + result.stderr

    def test_validator_passes_on_actual_workspace(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should pass on the actual complete workspace."""
        returncode, output = self.run_validator_in_dir(validator_script, workspace_root)
        assert returncode == 0, f"Validator should pass on complete bundle:\n{output}"
        assert "All checks passed" in output

    def test_validator_fails_without_pstack_directory(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when pstack/ directory is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy workspace structure but omit pstack
            for item in ["CLAUDE.md", "README.md", "scripts"]:
                src = workspace_root / item
                if src.exists():
                    if src.is_dir():
                        shutil.copytree(src, tmp_path / item, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, tmp_path / item)

            # Create .cursor/skills but no pstack
            (tmp_path / ".cursor" / "skills").mkdir(parents=True, exist_ok=True)

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail without pstack directory"
            assert "pstack directory exists" in output

    def test_validator_fails_without_manifest(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when MANIFEST.sha256 is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Delete manifest
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                manifest.unlink()

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail without manifest"
            assert "MANIFEST.sha256 missing" in output or "check(s) failed" in output

    def test_validator_fails_with_corrupted_file(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when a file is corrupted (hash mismatch)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Corrupt a key file
            poteto = (
                tmp_path / ".cursor" / "skills" / "pstack" / "skills" / "poteto-mode" / "SKILL.md"
            )
            if poteto.exists():
                with open(poteto, "a") as f:
                    f.write("\n# CORRUPTED FILE\n")

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with corrupted file"
            # Either integrity check fails or file count mismatch
            assert "failed" in output.lower()

    def test_validator_fails_without_poteto_mode(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when poteto-mode entry point is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Delete poteto-mode
            poteto_dir = tmp_path / ".cursor" / "skills" / "pstack" / "skills" / "poteto-mode"
            if poteto_dir.exists():
                shutil.rmtree(poteto_dir)

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail without poteto-mode"
            assert "poteto-mode exists" in output or "Integrity check failed" in output

    def test_validator_fails_without_playbooks(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when playbooks are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Delete playbooks
            playbooks_dir = (
                tmp_path / ".cursor" / "skills" / "pstack" / "skills" / "poteto-mode" / "playbooks"
            )
            if playbooks_dir.exists():
                shutil.rmtree(playbooks_dir)

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail without playbooks"
            # Will fail on "playbooks directory exists" or "Has playbooks" or integrity check
            assert "failed" in output.lower()

    def test_validator_fails_with_missing_dependencies(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when referenced skill dependencies are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Delete a key referenced skill
            how_skill = tmp_path / ".cursor" / "skills" / "pstack" / "skills" / "how"
            if how_skill.exists():
                shutil.rmtree(how_skill)

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with missing dependencies"
            assert "skills/how/SKILL.md" in output or "Integrity check failed" in output

    def test_validator_fails_without_router_skill(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when router skill is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Delete router
            router = tmp_path / ".cursor" / "skills" / "use-pstack-workflows"
            if router.exists():
                shutil.rmtree(router)

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail without router"
            assert "Router exists" in output

    def test_validator_detects_stale_readme_references(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should detect stale README references to deleted files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Add stale reference to README
            readme = tmp_path / "README.md"
            if readme.exists():
                with open(readme, "a") as f:
                    f.write("\n\nSee `.cursor/rules/pstack-coding.mdc` for details.\n")

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with stale README references"
            assert "No deleted .mdc references" in output

    def test_validator_detects_malformed_manifest_hash(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when manifest has malformed hash (not 64-char hex)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Corrupt manifest with malformed hash
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest) as f:
                    lines = f.readlines()
                with open(manifest, "w") as f:
                    # First line malformed
                    f.write("XXXX0123456789abcdef  ./LICENSE\n")
                    f.writelines(lines[1:])

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with malformed manifest hash"
            assert "malformed" in output.lower() or "valid SHA256" in output

    def test_validator_detects_duplicate_manifest_paths(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when manifest has duplicate paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Add duplicate entry to manifest
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest, "a") as f:
                    # Duplicate the LICENSE entry
                    hash_val = "bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e"
                    f.write(f"{hash_val}  ./LICENSE\n")

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with duplicate manifest paths"
            assert "duplicate" in output.lower()

    def test_validator_detects_wrong_file_count(
        self, workspace_root: Path, validator_script: Path
    ) -> None:
        """Validator should fail when file count doesn't match manifest count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Copy everything
            shutil.copytree(workspace_root, tmp_path, dirs_exist_ok=True, symlinks=True)

            # Remove last line from manifest
            manifest = tmp_path / ".cursor" / "skills" / "pstack" / "MANIFEST.sha256"
            if manifest.exists():
                with open(manifest) as f:
                    lines = f.readlines()
                with open(manifest, "w") as f:
                    f.writelines(lines[:-1])

            returncode, output = self.run_validator_in_dir(validator_script, tmp_path)
            assert returncode != 0, "Should fail with wrong file count"
            assert "count" in output.lower() or "mismatch" in output.lower(), (
                f"Expected file count error, got: {output}"
            )
