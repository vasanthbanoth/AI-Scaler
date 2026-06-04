import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _repo_root() -> Path:
    env = os.getenv("REPO_ROOT")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent
    for base in (here.parent.parent, here.parents[2], here.parents[3]):
        if (base / "data" / "resume.md").exists():
            return base
    return here.parents[3]


ROOT = _repo_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(ROOT / ".env", ROOT / ".env.local"),
        extra="ignore",
    )

    openai_api_key: str = ""
    api_base_url: str = "http://localhost:8000"

    calcom_api_key: str = ""
    calcom_event_type_id: str = ""
    calcom_username: str = "vasanthbanoth"

    vapi_server_secret: str = "dev-secret"
    run_ingest_on_start: bool = False

    github_username: str = "vasanthbanoth"
    github_token: str = ""

    chunks_path: Path = ROOT / "data" / "chunks.json"
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()
