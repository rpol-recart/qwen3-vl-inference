# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Qwen3-VL Inference Server** - a production-ready FastAPI server for multimodal vision-language tasks using the Qwen3-VL model with vLLM backend. The server provides 8 core capabilities: 2D Grounding, Spatial Understanding, Video Understanding, Image Description, Document Parsing, Document OCR, Wild Image OCR, and Image Comparison.

The codebase is in **Russian** (comments and documentation), though code follows standard Python conventions.

## Common Commands

### Local Development

```bash
# Setup and installation
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env  # Edit .env with your configuration

# Run server locally
python main.py
# Or with uvicorn directly:
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run with reload (development)
uvicorn app.main:app --reload --log-level debug
```

### Docker Development

```bash
# Using Makefile (recommended)
make setup              # Create .env from template
make deploy-dev         # Full dev deployment (setup + build + up + health check)
make deploy-prod        # Full prod deployment
make logs               # View logs in follow mode
make health             # Check service health
make dev                # Start in dev mode with hot reload
make shell              # Open bash shell in container
make gpu                # Check GPU usage inside container

# Using docker-compose directly
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose logs -f
docker-compose ps
```

### Testing

```bash
# API health check
curl http://localhost:8000/api/health

# Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**Note**: There are no automated tests in this codebase currently. Testing is done manually via API calls or the example client.

## Architecture

### High-Level Design

The project follows **SOLID principles** with a clean **layered architecture**:

```
HTTP Request → API Layer (routes.py) → Service Layer (services/) → Core Layer (inference_engine.py) → vLLM Model
```

**Key architectural patterns:**

1. **Dependency Injection**: Engine is injected via FastAPI `Depends()` to all endpoints
2. **Singleton Pattern**: Single `Qwen3VLInferenceEngine` instance shared across all requests (set in lifespan)
3. **Service Layer Pattern**: Each capability (grounding, spatial, video, etc.) has its own service class
4. **Factory Pattern**: Services are instantiated per-request in route handlers

### Critical Components

#### 1. Lifespan Management ([app/main.py](app/main.py))

The inference engine is initialized in FastAPI's lifespan context manager (startup) and stored as a global singleton. This is **critical** - the engine must be initialized before any requests are processed:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = Qwen3VLInferenceEngine(...)
    set_engine(engine)  # Stores in global _engine variable
    yield
    # Shutdown cleanup
```

#### 2. Inference Engine ([app/core/inference_engine.py](app/core/inference_engine.py))

Wrapper around vLLM that handles:
- Model initialization with tensor parallelism support
- Image/video input preprocessing via `process_vision_info`
- Prompt formatting via processor's chat template
- Generation with configurable sampling parameters

**Important**: The engine uses `AutoProcessor` to format messages and `process_vision_info` from `qwen_vl_utils` to handle multimodal inputs.

#### 3. Service Layer ([app/services/](app/services/))

Each service class follows the same pattern:
- Takes `Qwen3VLInferenceEngine` in constructor
- Has a main method (e.g., `perform_grounding`, `generate_description`)
- Builds task-specific prompts
- Calls engine.generate()
- Returns `InferenceResponse` with structured results

**Key Services:**
- `GroundingService`: 2D object detection with bounding boxes
- `SpatialUnderstandingService`: Spatial reasoning queries
- `VideoUnderstandingService`: Video analysis with frame sampling
- `DescriptionService`: Image captioning with detail levels
- `DocumentService`: Document parsing to HTML/Markdown/JSON
- `OCRService`: Text extraction from documents and natural images
- `ImageComparisonService`: Multi-image (2-4) comparison for detecting differences, changes, or similarities

#### 4. Request/Response Schemas ([app/schemas.py](app/schemas.py))

Pydantic models provide:
- Automatic validation
- API documentation generation
- Type safety

**Key schemas:**
- `InferenceRequest` (base class)
- `ImageInferenceRequest` (for image tasks)
- `VideoInferenceRequest` (for video tasks)
- Task-specific requests extend these base classes
- All responses use `InferenceResponse` with `success`, `result`, and `error` fields

#### 5. Configuration ([app/config.py](app/config.py))

Uses `pydantic_settings.BaseSettings` for environment-based config:
- Model path and vLLM settings (GPU memory, tensor parallelism)
- Inference defaults (max_tokens, temperature, top_p)
- Image/video processing defaults (min/max pixels, fps, max frames)
- CORS settings

### Data Flow for Typical Request

1. Request hits API endpoint in [app/api/routes.py](app/api/routes.py)
2. Pydantic validates request against schema
3. Route handler creates appropriate service instance with injected engine
4. Service builds task-specific prompt using [app/core/utils.py](app/core/utils.py) helpers
5. Service calls `engine.prepare_image_inputs()` then `engine.generate()`
6. Engine formats prompt via processor, processes vision inputs, runs vLLM inference
7. Service parses/formats result and returns `InferenceResponse`
8. FastAPI serializes response to JSON

### Important Utilities ([app/core/utils.py](app/core/utils.py))

- `get_image_from_request()`: Handles both URLs and base64 images
- `get_video_from_request()`: Handles video URLs and base64
- `build_image_message()`: Creates message dict for processor
- `build_video_message()`: Creates video message dict with kwargs
- `parse_json_response()`: Extracts and validates JSON from model output

### GPU and Performance Considerations

- **Tensor Parallelism**: Set `TENSOR_PARALLEL_SIZE` env var to distribute model across multiple GPUs
- **GPU Memory**: Adjust `GPU_MEMORY_UTILIZATION` (default 0.7) based on available VRAM
- **Model Size**: Qwen3-VL-235B requires minimum 24GB VRAM, more for larger contexts
- **vLLM Optimizations**: Uses PagedAttention for efficient memory management
- **Image Processing**: `min_pixels` and `max_pixels` control resolution vs speed tradeoff

## Key Files

- [app/main.py](app/main.py): FastAPI app initialization, lifespan management, CORS
- [app/api/routes.py](app/api/routes.py): All API endpoints, dependency injection setup
- [app/core/inference_engine.py](app/core/inference_engine.py): vLLM wrapper, core inference logic
- [app/core/utils.py](app/core/utils.py): Shared utilities for image/video processing, message building
- [app/config.py](app/config.py): Environment-based configuration
- [app/schemas.py](app/schemas.py): Pydantic request/response models
- [Makefile](Makefile): Convenient commands for common operations
- [ARCHITECTURE.md](ARCHITECTURE.md): Detailed architecture documentation (in Russian)
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md): Comprehensive Docker deployment guide

## Environment Variables

Critical environment variables (set in `.env` file):

```bash
MODEL_PATH=Qwen/Qwen3-VL-235B-A22B-Instruct  # HuggingFace model ID or local path
HF_TOKEN=hf_xxxxx  # Required for gated models
GPU_MEMORY_UTILIZATION=0.70  # 0.0-1.0, lower if OOM errors
TENSOR_PARALLEL_SIZE=1  # Number of GPUs to use (auto-detected if not set)
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

See [.env.example](.env.example) or [.env.docker](.env.docker) for full list.

## Adding New Capabilities

To add a new vision-language task:

1. Create service class in [app/services/](app/services/)
2. Define request schema in [app/schemas.py](app/schemas.py) extending `ImageInferenceRequest` or `VideoInferenceRequest`
3. Add endpoint in [app/api/routes.py](app/api/routes.py)
4. Follow existing service pattern: constructor takes engine, main method builds prompt and calls `engine.generate()`

## Common Issues

**OOM Errors**: Reduce `GPU_MEMORY_UTILIZATION` or use smaller `max_pixels` values
**Slow Startup**: Model loading takes 1-2 minutes, increase `healthcheck.start_period` in docker-compose
**Model Not Found**: Ensure `MODEL_PATH` is correct and `HF_TOKEN` is set for gated models
**CUDA Errors**: Ensure nvidia-docker is installed and GPUs are accessible via `docker run --gpus all`

## Docker Context

- **Base Image**: Uses CUDA-enabled PyTorch base image
- **Multi-stage Build**: Separates dependencies from runtime (see [Dockerfile](Dockerfile))
- **Volume Mounts**: Model cache in named volume `model-cache`
- **GPU Access**: Requires nvidia-docker runtime with `--gpus all`
- **Healthcheck**: Polls `/api/health` endpoint every 30s after 120s startup period
- **Dev vs Prod**: Dev mode mounts source code for hot reload, prod mode runs optimized

## Documentation References

- Full API docs: Run server and visit `/docs` (Swagger) or `/redoc`
- Architecture deep-dive: See [ARCHITECTURE.md](ARCHITECTURE.md) (in Russian)
- Docker deployment: See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) (in Russian)
- Quick start guide: See [QUICKSTART.md](QUICKSTART.md) (in Russian)
- Video API specifics: See [VIDEO_API_GUIDE.md](VIDEO_API_GUIDE.md) (if present)
