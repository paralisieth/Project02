from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Cyber Training Platform"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "cyber_platform"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Lab settings
    LAB_NETWORK_NAME: str = "lab-network"
    LAB_VPN_SUBNET: str = "172.16.0.0/16"
    LAB_VPN_HOST: str = "vpn.labs.local"
    MAX_LABS_PER_USER: int = 3
    MAX_VMS_PER_LAB: int = 5

    # Monitoring settings
    MONITOR_CHECK_INTERVAL: int = 60  # seconds
    MONITOR_CPU_THRESHOLD: float = 80.0  # percent
    MONITOR_MEMORY_THRESHOLD: float = 80.0  # percent
    MONITOR_DISK_THRESHOLD: float = 90.0  # percent

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
