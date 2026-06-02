from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Secret pepper used for hashing passkeys deterministically
    SECRET_PEPPER: str = os.getenv("SECRET_PEPPER", "default-dev-secret-pepper-change-in-prod")
    
    # CORS allowed origins (comma separated or JSON list, but let's just keep it simple: split by comma)
    # E.g. "http://localhost:8000,https://myproductiondomain.com"
    ALLOWED_ORIGINS_STR: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        if self.ALLOWED_ORIGINS_STR == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS_STR.split(",")]

settings = Settings()
