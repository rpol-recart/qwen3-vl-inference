"""Main FastAPI application."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router, set_engine
from app.core.inference_engine import Qwen3VLInferenceEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.

    Initializes the inference engine on startup and cleans up on shutdown.
    """
    # Startup
    logger.info("Starting Qwen3-VL Inference Server...")
    logger.info(f"Model path: {settings.model_path}")

    try:
        # Initialize inference engine
        engine = Qwen3VLInferenceEngine(
            model_path=settings.model_path,
            gpu_memory_utilization=settings.gpu_memory_utilization,
            tensor_parallel_size=settings.tensor_parallel_size,
            trust_remote_code=settings.trust_remote_code,
            enforce_eager=settings.enforce_eager,
            max_model_len=settings.max_model_len,
        )

        # Set global engine instance
        set_engine(engine)

        logger.info("Inference engine initialized successfully")
        logger.info(f"Server ready at http://{settings.host}:{settings.port}")

    except Exception as e:
        logger.error(f"Failed to initialize inference engine: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Qwen3-VL Inference Server...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Qwen3-VL Inference Server provides a comprehensive API for multimodal vision-language tasks.

    ## Features

    - **2D Grounding**: Detect and localize objects in images
    - **Spatial Understanding**: Answer spatial reasoning questions
    - **Video Understanding**: Analyze videos and temporal events
    - **Image Description**: Generate detailed image captions
    - **Document Parsing**: Convert documents to structured formats
    - **OCR**: Extract text from documents and natural images

    ## Model

    Powered by Qwen3-VL with vLLM inference engine for high-performance inference.
    """,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)

# Include API router
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/api/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
