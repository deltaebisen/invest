import os
from dataclasses import dataclass


@dataclass
class Config:
    # PostgreSQL設定
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "stocks")
    postgres_user: str = os.getenv("POSTGRES_USER", "stockuser")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "stockpass")

    # アプリケーション設定
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    download_batch_size: int = int(os.getenv("DOWNLOAD_BATCH_SIZE", "50"))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


config = Config()
