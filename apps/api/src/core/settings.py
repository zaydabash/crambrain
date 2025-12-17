# apps/api/src/core/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Server
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    cors_origins: str = Field("*", alias="CORS_ORIGINS")
    api_key: str | None = Field(None, alias="API_KEY")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, alias="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, alias="RATE_LIMIT_WINDOW")

    # LLM
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")

    # OCR
    enable_tesseract: bool = Field(False, alias="ENABLE_TESSERACT")
    tesseract_cmd: str | None = Field(None, alias="TESSERACT_CMD")

    # S3 (Backblaze B2 S3-compatible)
    s3_endpoint_url: str = Field(..., alias="S3_ENDPOINT_URL")
    s3_region: str = Field(..., alias="S3_REGION")
    s3_bucket: str = Field(..., alias="S3_BUCKET")
    s3_access_key: str = Field(..., alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(..., alias="S3_SECRET_KEY")
    # None or "private" if you don't serve public previews
    s3_public_base_url: str | None = Field(None, alias="S3_PUBLIC_BASE_URL")

    # Vector DB
    chroma_persist_dir: str = Field("/data/chroma", alias="CHROMA_PERSIST_DIR")
    chroma_collection: str = Field("crambrain", alias="CHROMA_COLLECTION")

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        """Return CORS origins as a list; treat '*' as wildcard."""
        if not self.cors_origins or self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

def get_settings() -> "Settings":
    return Settings()  # type: ignore