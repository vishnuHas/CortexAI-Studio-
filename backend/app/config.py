import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "CortexAI Studio - Multi-Tier Engineering Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # NVIDIA NIM Configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    DEFAULT_CHAT_MODEL: str = os.getenv("DEFAULT_CHAT_MODEL", "meta/llama-3.2-11b-vision-instruct")
    DEFAULT_FAST_MODEL: str = os.getenv("DEFAULT_FAST_MODEL", "meta/llama-3.2-11b-vision-instruct")
    DEFAULT_EMBED_MODEL: str = os.getenv("DEFAULT_EMBED_MODEL", "nvidia/nv-embedqa-e5-v5")

    # Document & RAG Defaults
    DEFAULT_CHUNK_SIZE: int = 400
    DEFAULT_CHUNK_OVERLAP: int = 50
    DEFAULT_TOP_K: int = 4

settings = Settings()
