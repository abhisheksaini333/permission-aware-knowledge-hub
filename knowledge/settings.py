from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///data/knowledge.db"
    issuer: str = "http://localhost:8183/realms/knowledge"
    audience: str = "knowledge-api"
    max_document_bytes: int = 2000000
    chunk_size: int = 700
    chunk_overlap: int = 100
    max_query_chars: int = 1000

    def __post_init__(self):
        if (
            any(type(v) is not int or v < 1 for v in (self.chunk_size, self.max_document_bytes, self.max_query_chars))
            or type(self.chunk_overlap) is not int
            or not 0 <= self.chunk_overlap < self.chunk_size
            or self.max_document_bytes <= 0
        ):
            raise ValueError("Invalid document or chunk limits")

    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            issuer=os.getenv("OIDC_ISSUER", cls.issuer),
            audience=os.getenv("OIDC_AUDIENCE", cls.audience),
        )
