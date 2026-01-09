"""API routes for Qwen3-VL inference server."""
import logging
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional
from app.schemas import (
    Grounding2DRequest,
    SpatialUnderstandingRequest,
    VideoUnderstandingRequest,
    ImageDescriptionRequest,
    DocumentParsingRequest,
    OCRRequest,
    InferenceResponse,
    HealthResponse,
)
from app.services.grounding_service import GroundingService
from app.services.spatial_service import SpatialUnderstandingService
from app.services.video_service import VideoUnderstandingService
from app.services.description_service import ImageDescriptionService
from app.services.document_service import DocumentParsingService
from app.services.ocr_service import OCRService
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import encode_video_to_base64

logger = logging.getLogger(__name__)

router = APIRouter()

# Global engine instance (will be initialized on startup)
_engine: Qwen3VLInferenceEngine = None


def get_engine() -> Qwen3VLInferenceEngine:
    """Get the global inference engine instance."""
    if _engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inference engine not initialized"
        )
    return _engine


def set_engine(engine: Qwen3VLInferenceEngine):
    """Set the global inference engine instance."""
    global _engine
    _engine = engine


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        engine = get_engine()
        return HealthResponse(
            status="healthy",
            model_loaded=engine.is_ready(),
            version="1.0.0",
        )
    except HTTPException:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            version="1.0.0",
        )


@router.post("/v1/grounding/2d", response_model=InferenceResponse)
async def grounding_2d(
    request: Grounding2DRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform 2D object grounding and detection.

    This endpoint detects and localizes objects in images, returning bounding boxes
    in relative coordinates (0-1000).
    """
    service = GroundingService(engine)
    return await service.perform_grounding(request)


@router.post("/v1/spatial/understanding", response_model=InferenceResponse)
async def spatial_understanding(
    request: SpatialUnderstandingRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform spatial understanding and reasoning.

    This endpoint answers spatial questions about images, such as object relationships,
    positions, and affordances.
    """
    service = SpatialUnderstandingService(engine)
    return await service.perform_spatial_understanding(request)


@router.post("/v1/video/understanding", response_model=InferenceResponse)
async def video_understanding(
    request: VideoUnderstandingRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform video understanding and analysis.

    This endpoint analyzes videos and answers questions about content, actions,
    events, and temporal relationships.

    Supports multiple input formats:
    - video_url: URL to video file
    - video_base64: Base64 encoded video
    - frame_urls: List of frame URLs
    - frame_base64_list: List of base64 encoded frames
    """
    service = VideoUnderstandingService(engine)
    return await service.perform_video_understanding(request)


@router.post("/v1/video/understanding/upload", response_model=InferenceResponse)
async def video_understanding_upload(
    file: UploadFile = File(..., description="Video file to analyze"),
    prompt: str = Form(..., description="Question or instruction about the video"),
    max_tokens: Optional[int] = Form(2048, description="Maximum tokens to generate"),
    temperature: Optional[float] = Form(0.0, description="Sampling temperature"),
    top_p: Optional[float] = Form(1.0, description="Top-p sampling"),
    max_frames: Optional[int] = Form(2048, description="Maximum frames to process"),
    sample_fps: Optional[float] = Form(2.0, description="Sampling FPS"),
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform video understanding with file upload.

    This endpoint accepts a video file directly via multipart/form-data upload.
    Useful for analyzing local video files without needing to host them.

    Example using curl:
    ```
    curl -X POST "http://localhost:8000/api/v1/video/understanding/upload" \
      -F "file=@video.mp4" \
      -F "prompt=Describe what happens in this video"
    ```
    """
    try:
        # Save uploaded file to temporary location
        temp_dir = "/tmp/qwen_vl_uploads"
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}_{file.filename}")

        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"Video uploaded and saved to {temp_file_path}")

        # Convert to base64 for processing
        video_base64 = encode_video_to_base64(temp_file_path)

        # Create request object
        request = VideoUnderstandingRequest(
            video_base64=video_base64,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            max_frames=max_frames,
            sample_fps=sample_fps,
        )

        # Process video
        service = VideoUnderstandingService(engine)
        result = await service.perform_video_understanding(request)

        # Clean up temporary file
        try:
            os.remove(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {temp_file_path}: {e}")

        return result

    except Exception as e:
        logger.error(f"Video upload processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded video: {str(e)}"
        )


@router.post("/v1/image/description", response_model=InferenceResponse)
async def image_description(
    request: ImageDescriptionRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Generate detailed image descriptions.

    This endpoint provides comprehensive descriptions of images with varying
    levels of detail.
    """
    service = ImageDescriptionService(engine)
    return await service.perform_image_description(request)


@router.post("/v1/document/parsing", response_model=InferenceResponse)
async def document_parsing(
    request: DocumentParsingRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Parse documents and extract structured content.

    This endpoint converts document images to various formats (HTML, Markdown, JSON)
    with optional positional information.
    """
    service = DocumentParsingService(engine)
    return await service.perform_document_parsing(request)


@router.post("/v1/ocr/document", response_model=InferenceResponse)
async def document_ocr(
    request: OCRRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform OCR on document images.

    This endpoint extracts text from structured documents with optional
    bounding box information.
    """
    service = OCRService(engine)
    return await service.perform_document_ocr(request)


@router.post("/v1/ocr/wild", response_model=InferenceResponse)
async def wild_ocr(
    request: OCRRequest,
    engine: Qwen3VLInferenceEngine = Depends(get_engine),
):
    """
    Perform OCR on natural/wild images.

    This endpoint extracts text from images in natural scenes (signs, labels, etc.)
    with optional bounding box information.
    """
    service = OCRService(engine)
    return await service.perform_wild_ocr(request)
