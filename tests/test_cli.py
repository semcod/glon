"""
Tests for CLI functionality.
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from glon.cli import (
    _extract_git_url_from_text,
    clone_repository,
    create_directory_structure,
    detect_github_repo_from_cwd,
    parse_git_url,
    publish_repository,
)


class TestParseGitUrl:
    """Test cases for URL parsing function."""

    def test_parse_ssh_url(self) -> None:
        """Test parsing SSH git URL."""
        url = "git@github.com:tom-sapletta-com/glon.git"
        result = parse_git_url(url)

        assert result == ("tom-sapletta-com", "glon")

    def test_parse_https_url_with_git(self) -> None:
        """Test parsing HTTPS git URL with .git extension."""
        url = "https://github.com/tom-sapletta-com/glon.git"
        result = parse_git_url(url)

        assert result == ("tom-sapletta-com", "glon")

    def test_parse_https_url_without_git(self) -> None:
        """Test parsing HTTPS git URL without .git extension."""
        url = "https://github.com/tom-sapletta-com/glon"
        result = parse_git_url(url)

        assert result == ("tom-sapletta-com", "glon")

    def test_parse_invalid_url(self) -> None:
        """Test parsing invalid URL."""
        url = "invalid-url"
        result = parse_git_url(url)

        assert result is None

    def test_parse_different_domain_ssh(self) -> None:
        """Test parsing SSH URL with different domain."""
        url = "git@gitlab.com:user/project.git"
        result = parse_git_url(url)

        assert result == ("user", "project")

    def test_parse_different_domain_https(self) -> None:
        """Test parsing HTTPS URL with different domain."""
        url = "https://gitlab.com/user/project.git"
        result = parse_git_url(url)

        assert result == ("user", "project")

    def test_extract_embedded_url(self) -> None:
        """Extract a URL surrounded by prose."""
        text = "Clone https://github.com/owner/repo.git before continuing."

        assert _extract_git_url_from_text(text) == ("https://github.com/owner/repo.git")


class TestCreateDirectoryStructure:
    """Test cases for directory structure creation."""

    def test_create_directory_default_path(self) -> None:
        """Test creating directory with default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock expanduser to use temp directory
            with patch("os.path.expanduser", return_value=temp_dir):
                target_dir = create_directory_structure("owner", "repo")

                expected_path = Path(temp_dir) / "owner" / "repo"
                assert target_dir == expected_path
                assert target_dir.exists()
                assert target_dir.is_dir()

    def test_create_directory_custom_path(self) -> None:
        """Test creating directory with custom base path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "custom"
            target_dir = create_directory_structure("owner", "repo", str(base_path))

            expected_path = base_path / "owner" / "repo"
            assert target_dir == expected_path
            assert target_dir.exists()
            assert target_dir.is_dir()

    def test_create_directory_existing(self) -> None:
        """Test creating directory when it already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir) / "custom"
            target_dir = create_directory_structure("owner", "repo", str(base_path))

            # Create again - should not raise error
            target_dir2 = create_directory_structure("owner", "repo", str(base_path))

            assert target_dir == target_dir2
            assert target_dir.exists()


class TestCloneRepository:
    """Test cases for repository cloning."""

    @patch("subprocess.run")
    def test_clone_success(self, mock_run) -> None:
        """Test successful repository cloning."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Cloning into 'target'...", stderr=""
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target"
            target_dir.mkdir()

            url = "https://github.com/owner/repo.git"
            result = clone_repository(url, target_dir)

            assert result is True
            mock_run.assert_called_once_with(
                ["git", "clone", url, str(target_dir)],
                capture_output=True,
                text=True,
                check=True,
            )

    @patch("subprocess.run")
    def test_clone_git_error(self, mock_run) -> None:
        """Test repository cloning with git error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="Repository not found"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target"
            target_dir.mkdir()

            url = "https://github.com/owner/repo.git"
            result = clone_repository(url, target_dir)

            assert result is False

    @patch("subprocess.run")
    def test_clone_git_not_found(self, mock_run) -> None:
        """Test repository cloning when git is not found."""
        mock_run.side_effect = FileNotFoundError()

        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target"
            target_dir.mkdir()

            url = "https://github.com/owner/repo.git"
            result = clone_repository(url, target_dir)

            assert result is False

    def test_clone_non_empty_directory(self) -> None:
        """Test cloning to non-empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "target"
            target_dir.mkdir()

            # Create a file in the directory
            (target_dir / "existing_file.txt").write_text("content")

            url = "https://github.com/owner/repo.git"
            result = clone_repository(url, target_dir)

            assert result is False


class TestGrabFromClipboard:
    """Test cases for grab from clipboard functionality."""

    @patch("glon.cli._read_clipboard_text")
    @patch("glon.cli.parse_git_url")
    def test_grab_git_url_from_clipboard(self, mock_parse, mock_clipboard) -> None:
        """Test grabbing git URL from clipboard."""
        mock_clipboard.return_value = "git@github.com:owner/repo.git"
        mock_parse.return_value = ("owner", "repo")

        with patch("glon.cli.clone_repository", return_value=True) as mock_clone:
            with patch("glon.cli.create_directory_structure") as mock_create:
                mock_create.return_value = Path("/tmp/github/owner/repo")

                from glon.cli import grab_from_clipboard

                result = grab_from_clipboard()

                assert result is True
                mock_parse.assert_called_once_with("git@github.com:owner/repo.git")
                mock_create.assert_called_once()
                mock_clone.assert_called_once()

    @patch("glon.cli._read_clipboard_text")
    def test_grab_empty_clipboard(self, mock_clipboard) -> None:
        """Test grabbing from empty clipboard."""
        mock_clipboard.return_value = None

        from glon.cli import grab_from_clipboard

        result = grab_from_clipboard()

        assert result is False

    @patch("glon.cli._read_clipboard_text")
    def test_grab_whitespace_clipboard(self, mock_clipboard) -> None:
        """Test grabbing from clipboard with only whitespace."""
        mock_clipboard.return_value = "   \n\t  "

        from glon.cli import grab_from_clipboard

        result = grab_from_clipboard()

        assert result is False

    @patch("glon.cli._read_clipboard_text")
    def test_grab_invalid_path(self, mock_clipboard) -> None:
        """Test grabbing invalid path from clipboard."""
        mock_clipboard.return_value = "/nonexistent/path/12345"

        from glon.cli import grab_from_clipboard

        result = grab_from_clipboard()

        assert result is False

    @patch("glon.cli._read_clipboard_text")
    @patch("glon.cli.parse_git_url")
    def test_grab_dry_run(self, mock_parse, mock_clipboard) -> None:
        """Test grab with dry run."""
        mock_clipboard.return_value = "git@github.com:owner/repo.git"
        mock_parse.return_value = ("owner", "repo")

        from glon.cli import grab_from_clipboard

        result = grab_from_clipboard(dry_run=True)

        assert result is True

    @patch("glon.cli._read_clipboard_text")
    def test_grab_local_directory(self, mock_clipboard) -> None:
        """Test grabbing local directory from clipboard."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            mock_clipboard.return_value = temp_dir

            from glon.cli import grab_from_clipboard

            with patch("os.path.expanduser", return_value=temp_dir):
                result = grab_from_clipboard(base_path=temp_dir)

                # Should succeed (creates symlink)
                assert result is True or result is False  # Depends on permissions

    @patch("glon.cli._read_clipboard_text")
    @patch("glon.cli.parse_git_url")
    def test_grab_verbose_mode(self, mock_parse, mock_clipboard) -> None:
        """Test grab with verbose output."""
        mock_clipboard.return_value = "git@github.com:owner/repo.git"
        mock_parse.return_value = ("owner", "repo")

        with patch("glon.cli.clone_repository", return_value=True):
            with patch("glon.cli.create_directory_structure") as mock_create:
                mock_create.return_value = Path("/tmp/github/owner/repo")

                from glon.cli import grab_from_clipboard

                result = grab_from_clipboard(verbose=True)

                assert result is True


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    @patch("glon.cli.clone_repository")
    @patch("glon.cli.create_directory_structure")
    @patch("glon.cli.parse_git_url")
    def test_main_successful_clone(self, mock_parse, mock_create, mock_clone) -> None:
        """Test main function with successful clone."""
        mock_parse.return_value = ("owner", "repo")
        mock_create.return_value = Path("/tmp/github/owner/repo")
        mock_clone.return_value = True

        with patch("sys.argv", ["glon", "https://github.com/owner/repo.git"]):
            with patch("builtins.print") as mock_print:
                from glon.cli import main

                main()

                mock_parse.assert_called_once_with("https://github.com/owner/repo.git")
                mock_create.assert_called_once_with("owner", "repo", None)
                mock_clone.assert_called_once()

                # Check success message
                mock_print.assert_any_call(
                    "Repository ready at: /tmp/github/owner/repo"
                )

    @patch("glon.cli.parse_git_url")
    def test_main_invalid_url(self, mock_parse) -> None:
        """Test main function with invalid URL."""
        mock_parse.return_value = None

        with patch("sys.argv", ["glon", "invalid-url"]):
            with patch("sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    from glon.cli import main

                    main()

                    mock_exit.assert_not_called()
                    mock_print.assert_any_call(
                        "Error: Invalid git URL format: invalid-url"
                    )

    @patch("glon.cli.clone_repository")
    @patch("glon.cli.create_directory_structure")
    @patch("glon.cli.parse_git_url")
    def test_main_clone_failure(self, mock_parse, mock_create, mock_clone) -> None:
        """Test main function with clone failure."""
        mock_parse.return_value = ("owner", "repo")
        mock_create.return_value = Path("/tmp/github/owner/repo")
        mock_clone.return_value = False

        with patch("sys.argv", ["glon", "https://github.com/owner/repo.git"]):
            with patch("builtins.print") as mock_print:
                from glon.cli import main

                main()

                # Should not print success message on failure
                assert not any(
                    "Repository ready at" in str(call)
                    for call in mock_print.call_args_list
                )

    @patch("glon.cli.clone_repository")
    @patch("glon.cli.create_directory_structure")
    @patch("glon.cli.parse_git_url")
    def test_main_dry_run(self, mock_parse, mock_create, mock_clone) -> None:
        """Test main function with dry run."""
        mock_parse.return_value = ("owner", "repo")
        mock_create.return_value = Path("/tmp/github/owner/repo")

        with patch(
            "sys.argv", ["glon", "--dry-run", "https://github.com/owner/repo.git"]
        ):
            with patch("builtins.print") as mock_print:
                from glon.cli import main

                main()

                mock_clone.assert_not_called()
                mock_print.assert_any_call(
                    "Would clone https://github.com/owner/repo.git to "
                    "/tmp/github/owner/repo"
                )

    @patch("glon.cli.clone_repository")
    @patch("glon.cli.create_directory_structure")
    @patch("glon.cli.parse_git_url")
    def test_main_clone_subcommand(self, mock_parse, mock_create, mock_clone) -> None:
        """Accept the explicit clone subcommand without parser errors."""
        mock_parse.return_value = ("owner", "repo")
        mock_create.return_value = Path("/tmp/github/owner/repo")
        mock_clone.return_value = True

        with patch(
            "sys.argv",
            ["glon", "clone", "https://github.com/owner/repo.git"],
        ):
            from glon.cli import main

            main()

        mock_parse.assert_called_once_with("https://github.com/owner/repo.git")
        mock_clone.assert_called_once()


class TestDetectGithubRepo:
    """Test cases for detecting github/<owner>/<repo> from cwd."""

    def test_detect_repo_under_base_path(self) -> None:
        """Detect owner/repo when cwd is directly under base_path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "kvmouse" / "pi2w"
            repo_dir.mkdir(parents=True)

            result = detect_github_repo_from_cwd(cwd=repo_dir, base_path=temp_dir)

            assert result == ("kvmouse", "pi2w", repo_dir.resolve())

    def test_detect_repo_from_nested_subdir(self) -> None:
        """Detect owner/repo root even when cwd is a subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "kvmouse" / "pi2w"
            nested_dir = repo_dir / "docs" / "guides"
            nested_dir.mkdir(parents=True)

            result = detect_github_repo_from_cwd(cwd=nested_dir, base_path=temp_dir)

            assert result == ("kvmouse", "pi2w", repo_dir.resolve())

    def test_detect_repo_under_generic_github_dir(self) -> None:
        """Detect owner/repo under any .../github/<owner>/<repo> path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "github" / "semcod" / "glon"
            repo_dir.mkdir(parents=True)

            with patch("os.path.expanduser", return_value="/nonexistent/github"):
                result = detect_github_repo_from_cwd(cwd=repo_dir)

            assert result == ("semcod", "glon", repo_dir.resolve())

    def test_detect_returns_none_outside_repo_level(self) -> None:
        """Return None at owner level or outside github directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            owner_dir = Path(temp_dir) / "kvmouse"
            owner_dir.mkdir(parents=True)

            assert detect_github_repo_from_cwd(cwd=owner_dir, base_path=temp_dir) is None
            assert (
                detect_github_repo_from_cwd(cwd=Path(temp_dir), base_path=temp_dir)
                is None
            )


class TestPublishRepository:
    """Test cases for publishing github/*/* repos via gh and goal -a."""

    @patch("subprocess.run")
    def test_publish_new_repo_private_default(self, mock_run) -> None:
        """Initialize git, create private GitHub repo via gh, and run goal -a."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "github" / "kvmouse" / "pi2w"
            repo_dir.mkdir(parents=True)

            def fake_run(cmd, **kwargs):
                if cmd[:3] == ["git", "rev-parse", "--verify"]:
                    return MagicMock(returncode=1, stdout="", stderr="")
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = fake_run

            result = publish_repository(repo_dir, "kvmouse", "pi2w")

            assert result is True
            commands = [call.args[0] for call in mock_run.call_args_list]
            assert ["git", "init"] in commands
            assert ["git", "add", "-A"] in commands
            assert ["git", "commit", "--allow-empty", "-m", "Initial commit"] in commands
            assert [
                "gh",
                "repo",
                "create",
                "kvmouse/pi2w",
                "--private",
                "--source=.",
                "--remote=origin",
                "--push",
            ] in commands
            assert ["goal", "-a"] in commands

    @patch("subprocess.run")
    def test_publish_existing_origin_public(self, mock_run) -> None:
        """Update visibility to public, push origin, and run goal -a."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "github" / "semcod" / "glon"
            (repo_dir / ".git").mkdir(parents=True)

            def fake_run(cmd, **kwargs):
                if cmd[:3] == ["git", "remote", "get-url"]:
                    return MagicMock(
                        returncode=0,
                        stdout="https://github.com/semcod/glon.git\n",
                        stderr="",
                    )
                return MagicMock(returncode=0, stdout="", stderr="")

            mock_run.side_effect = fake_run

            result = publish_repository(repo_dir, "semcod", "glon", visibility="public")

            assert result is True
            commands = [call.args[0] for call in mock_run.call_args_list]
            assert [
                "gh",
                "repo",
                "edit",
                "semcod/glon",
                "--visibility",
                "public",
            ] in commands
            assert ["git", "push", "-u", "origin", "HEAD"] in commands
            assert ["goal", "-a"] in commands

    @patch("subprocess.run")
    def test_publish_dry_run_skips_mutating_commands(self, mock_run) -> None:
        """Dry run prints planned commands without executing gh or goal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "github" / "kvmouse" / "pi2w"
            repo_dir.mkdir(parents=True)

            result = publish_repository(
                repo_dir, "kvmouse", "pi2w", visibility="private", dry_run=True
            )

            assert result is True
            mock_run.assert_not_called()

    @patch("glon.cli.publish_repository", return_value=True)
    @patch("glon.cli.detect_github_repo_from_cwd")
    def test_main_no_args_in_github_folder_publishes_private(
        self, mock_detect, mock_publish
    ) -> None:
        """Running `glon` inside github/*/* publishes privately by default."""
        repo_path = Path("/tmp/github/kvmouse/pi2w")
        mock_detect.return_value = ("kvmouse", "pi2w", repo_path)

        with patch("sys.argv", ["glon"]):
            from glon.cli import main

            main()

        mock_publish.assert_called_once_with(
            repo_path,
            "kvmouse",
            "pi2w",
            visibility="private",
            dry_run=False,
            verbose=False,
        )

    @patch("glon.cli.publish_repository", return_value=True)
    @patch("glon.cli.detect_github_repo_from_cwd")
    def test_main_public_subcommand_publishes_public(
        self, mock_detect, mock_publish
    ) -> None:
        """Running `glon public` publishes with public visibility."""
        repo_path = Path("/tmp/github/kvmouse/pi2w")
        mock_detect.return_value = ("kvmouse", "pi2w", repo_path)

        with patch("sys.argv", ["glon", "public"]):
            from glon.cli import main

            main()

        mock_publish.assert_called_once_with(
            repo_path,
            "kvmouse",
            "pi2w",
            visibility="public",
            dry_run=False,
            verbose=False,
        )

    @patch("glon.cli.publish_repository", return_value=True)
    @patch("glon.cli.detect_github_repo_from_cwd")
    def test_main_private_subcommand_publishes_private(
        self, mock_detect, mock_publish
    ) -> None:
        """Running `glon private` publishes with private visibility."""
        repo_path = Path("/tmp/github/kvmouse/pi2w")
        mock_detect.return_value = ("kvmouse", "pi2w", repo_path)

        with patch("sys.argv", ["glon", "private"]):
            from glon.cli import main

            main()

        mock_publish.assert_called_once_with(
            repo_path,
            "kvmouse",
            "pi2w",
            visibility="private",
            dry_run=False,
            verbose=False,
        )

    @patch("glon.cli.detect_github_repo_from_cwd", return_value=None)
    def test_main_private_outside_github_folder_prints_error(
        self, mock_detect
    ) -> None:
        """Running `glon private` outside github/*/* prints a clear error."""
        with patch("sys.argv", ["glon", "private"]):
            with patch("builtins.print") as mock_print:
                from glon.cli import main

                main()

        mock_print.assert_any_call(
            "Error: Current directory is not inside a github/<owner>/<repo> folder."
        )
