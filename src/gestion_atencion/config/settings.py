import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "gestion_atencion"
    db_user: str = "postgres"
    db_password: str = "postgres"

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "gestion_atencion"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", "postgres"),
        )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
