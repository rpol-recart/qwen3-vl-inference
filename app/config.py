"""Configuration module for Qwen3-VL Inference Server."""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server settings
    app_name: str = "Qwen3-VL Inference Server"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Model settings
    model_path: str = os.getenv(
        "MODEL_PATH",
        "Qwen/Qwen3-VL-235B-A22B-Instruct"
    )

    # vLLM settings
    gpu_memory_utilization: float = 0.70
    tensor_parallel_size: Optional[int] = None
    max_model_len: Optional[int] = None
    trust_remote_code: bool = True
    enforce_eager: bool = False

    # Inference settings
    default_max_tokens: int = 2048
    default_temperature: float = 0.0
    default_top_p: float = 1.0

    # Image processing settings
    default_min_pixels: int = 64 * 32 * 32
    default_max_pixels: int = 2048 * 32 * 32

    # Video processing settings
    default_max_frames: int = 2048
    default_sample_fps: float = 2.0
    default_total_pixels: int = 20480 * 32 * 32

    # CORS settings
    allow_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
