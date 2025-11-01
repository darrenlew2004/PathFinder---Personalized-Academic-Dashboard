from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "PathFinder Academic Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Cassandra
    CASSANDRA_HOST: str = "sunway.hep88.com"
    CASSANDRA_PORT: int = 9042
    CASSANDRA_KEYSPACE: str = "subjectplanning"
    CASSANDRA_DATACENTER: str = "datacenter1"
    CASSANDRA_USERNAME: str = ""
    CASSANDRA_PASSWORD: str = ""
    
    # JWT
    JWT_SECRET_KEY: str = "your-256-bit-secret-change-this-in-production-make-it-long"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
