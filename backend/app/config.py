from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    lab_mode: str = "baseline"
    database_url: str = f"sqlite:///{(BACKEND_ROOT / 'data' / 'lab.db').as_posix()}"
    doubao_api_key: str = ""
    doubao_endpoint_id: str = ""
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    use_mock_llm: bool = False
    lab_admin_token: str = "dev-lab-token-change-me"

    @property
    def llm_configured(self) -> bool:
        return bool(self.doubao_api_key and self.doubao_endpoint_id)


@lru_cache
def get_settings() -> Settings:
    return Settings()
