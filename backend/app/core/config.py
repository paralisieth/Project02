from typing import List
from pydantic import BaseSettings, AnyHttpUrl

class Settings(BaseSettings):
    # API Settings
    PROJECT_NAME: str = "Cyber Training Platform"
    API_V1_STR: str = "/api/v1"
    
    # Security Settings
    SECRET_KEY: str = "your-super-secret-key-change-in-production"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS Settings
    CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:3001"   # Alternative port
    ]
    
    # VM Settings
    DEFAULT_VM_MEMORY: int = 4096  # MB
    DEFAULT_VM_CPU_COUNT: int = 2
    MAX_VMS_PER_USER: int = 5
    
    # Guacamole Settings
    GUACAMOLE_HOST: str = "localhost"
    GUACAMOLE_PORT: int = 4822
    
    # VPN Settings
    VPN_SERVER_HOST: str = "localhost"
    VPN_SERVER_PORT: int = 1194
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
