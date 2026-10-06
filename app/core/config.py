import os
from dataclasses import dataclass, field


def _list(v: str) -> list[str]:
    return [x.strip() for x in v.split(",") if x.strip()]


@dataclass
class Settings:
    admin_token: str = field(default_factory=lambda: os.getenv("ADMIN_TOKEN", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    allowed_origins: list[str] = field(default_factory=lambda: _list(os.getenv("ALLOWED_ORIGINS", "http://localhost:8000")))
    rate_limit_per_min: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MIN", "20")))
    database_path: str = field(default_factory=lambda: os.getenv("DATABASE_PATH", "data/ajanta.db"))
    knowledge_dir: str = field(default_factory=lambda: os.getenv("KNOWLEDGE_DIR", "knowledge"))
    contact_email: str = field(default_factory=lambda: os.getenv("CONTACT_EMAIL", ""))
    relevance_threshold: float = 0.34
    top_k: int = 4


def get_settings() -> Settings:
    return Settings()
