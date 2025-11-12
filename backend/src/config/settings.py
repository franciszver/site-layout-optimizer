from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # AWS Configuration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_geospatial: str = "site-layout-optimizer-geospatial"
    s3_bucket_processed: str = "site-layout-optimizer-processed"
    s3_bucket_exports: str = "site-layout-optimizer-exports"
    s3_bucket_terrain_cache: str = "site-layout-optimizer-terrain-cache"
    
    # Database Configuration
    database_url: Optional[str] = None
    postgres_user: str = "postgres"
    postgres_password: str = ""  # Set via environment variable
    postgres_db: str = "site_layout_optimizer"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # OpenAI/OpenRouter Configuration
    openrouter_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    
    # Application Configuration
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

