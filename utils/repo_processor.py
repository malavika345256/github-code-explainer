"""Clone public GitHub repositories and collect supported source files."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".html",
    ".css",
    ".sql",
    ".json",
}
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}
CLONE_TIMEOUT_SECONDS = 60


def _is_github_repository_url(repo_url):
    """Return whether repo_url points to a standard HTTPS GitHub repository."""
    if not isinstance(repo_url, str):
        return False

    parsed = urlparse(repo_url.strip())
    if parsed.scheme != "https" or parsed.hostname not in {"github.com", "www.github.com"}:
        return False

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) != 2:
        return False

    repository = parts[1][:-4] if parts[1].endswith(".git") else parts[1]
    return bool(parts[0] and repository)


def clone_repository(repo_url):
    """Clone a public GitHub repository and return its temporary checkout path.

    The temporary directory is intentionally retained for the caller to use.
    Remove it with shutil.rmtree when it is no longer needed.
    """
    if not _is_github_repository_url(repo_url):
        raise ValueError("repo_url must be an HTTPS URL for a GitHub owner/repository.")

    destination = tempfile.mkdtemp(prefix="github-code-explainer-")
    try:
        # A full-history clone of a large repository can otherwise leave the
        # API request waiting indefinitely. A shallow clone is sufficient for
        # source inspection and puts a hard limit on the time spent here.
        subprocess.run(
            ["git", "clone", "--depth=1", repo_url.strip(), destination],
            check=True,
            capture_output=True,
            text=True,
            timeout=CLONE_TIMEOUT_SECONDS,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        shutil.rmtree(destination, ignore_errors=True)
        raise RuntimeError(f"Could not clone GitHub repository: {exc}") from exc
    return destination


def extract_code(repo_path):
    """Return supported source files beneath repo_path as filename/path/content rows."""
    root = Path(repo_path)
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo_path}")

    files = []
    for current_dir, directory_names, file_names in os.walk(root):
        directory_names[:] = [
            name for name in directory_names if name not in IGNORED_DIRECTORIES
        ]
        for name in file_names:
            file_path = Path(current_dir) / name
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue
            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                # Unreadable or non-UTF-8 files should not prevent processing
                # the rest of the repository.
                continue
            files.append(
                {
                    "filename": name,
                    "relative_path": file_path.relative_to(root).as_posix(),
                    "content": content,
                }
            )
    return files
