"""Integration test for cloning and extracting a small public repository."""

import shutil

from repo_processor import clone_repository, extract_code


def test_clone_repository_and_extract_source_files():
    repo_path = clone_repository("https://github.com/kennethreitz/samplemod.git")
    try:
        assert repo_path
        code_files = extract_code(repo_path)

        assert code_files, "Expected to find at least one supported source file"
        assert any(item["filename"].endswith(".py") for item in code_files)
        assert all(isinstance(item["content"], str) for item in code_files)
        assert any(item["content"].strip() for item in code_files)
    finally:
        shutil.rmtree(repo_path, ignore_errors=True)
