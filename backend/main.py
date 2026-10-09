
"""HTTP API for explaining public GitHub repositories with local Ollama."""

import shutil
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, field_validator

from utils.llm_explainer import explain_code
from utils.repo_processor import clone_repository, extract_code

MAX_CODE_CHARS = 50_000


class RepositoryRequest(BaseModel):
    """Request body containing the HTTPS URL of a GitHub repository."""

    model_config = ConfigDict(str_strip_whitespace=True)

    repo_url: str

    @field_validator("repo_url")
    @classmethod
    def validate_github_repository_url(cls, value: str) -> str:
        parsed = urlparse(value)
        path_parts = [
            part for part in parsed.path.strip("/").split("/") if part
        ]

        if (
            parsed.scheme != "https"
            or parsed.hostname not in {"github.com", "www.github.com"}
            or parsed.port is not None
            or parsed.username is not None
            or parsed.password is not None
            or len(path_parts) != 2
            or path_parts[1].removesuffix(".git") == ""
        ):
            raise ValueError(
                "repo_url must be an HTTPS GitHub repository URL, "
                "such as https://github.com/owner/repository."
            )

        return value


app = FastAPI(
    title="Local GitHub Repository Code Explainer",
    description=(
        "Explains public GitHub repositories using Qwen "
        "running locally in Ollama."
    ),
    version="1.0.0",
)

# Allow the local frontend to communicate with the FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    """Check whether the API is running."""
    return {
        "status": "ok",
        "message": "GitHub Code Explainer API is running.",
    }


@app.post("/explain", tags=["Repository"])
def explain_repository(
    request: RepositoryRequest,
) -> dict[str, object]:
    """Clone a repository, collect source code, and explain it with Ollama."""

    repo_path: str | None = None

    try:
        try:
            repo_path = clone_repository(request.repo_url)
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Repository cloning failed: {exc}",
            ) from exc

        try:
            files = extract_code(repo_path)
        except (OSError, ValueError) as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Could not read repository source files: {exc}",
            ) from exc

        if not files:
            raise HTTPException(
                status_code=422,
                detail=(
                    "No supported source files were found "
                    "in this repository."
                ),
            )

        code_parts = []
        remaining_chars = MAX_CODE_CHARS
        files_in_prompt = 0

        for item in files:
            if remaining_chars <= 0:
                break

            file_section = (
                f"===== {item['relative_path']} =====\n"
                f"{item['content']}\n\n"
            )

            part = file_section[:remaining_chars]
            code_parts.append(part)
            remaining_chars -= len(part)
            files_in_prompt += 1

        combined_code = "".join(code_parts)

        try:
            explanation = explain_code(combined_code)
        except (RuntimeError, ValueError) as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Local Ollama explanation failed: {exc}",
            ) from exc

        return {
            "success": True,
            "files_analyzed": files_in_prompt,
            "explanation": explanation,
        }

    finally:
        if repo_path:
            shutil.rmtree(Path(repo_path), ignore_errors=True)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
