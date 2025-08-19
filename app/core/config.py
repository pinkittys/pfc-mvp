from pydantic import BaseModel
from functools import lru_cache
import os

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")

@lru_cache()
def get_settings():
    return Settings()
