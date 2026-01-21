"""Pydantic schemas for request and response models."""
from typing import Optional, Union, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class TaskType(str, Enum):
    """Supported task types."""
    GROUNDING_2D = "2d_grounding"
    SPATIAL_UNDERSTANDING = "spatial_understanding"
    VIDEO_UNDERSTANDING = "video_understanding"
    IMAGE_DESCRIPTION = "image_description"
    DOCUMENT_PARSING = "document_parsing"
    DOCUMENT_OCR = "document_ocr"
    WILD_OCR = "wild_ocr"
    IMAGE_COMPARISON = "image_comparison"


class OutputFormat(str, Enum):
    """Output format options."""
    JSON = "json"
    TEXT = "text"
    HTML = "html"
    MARKDOWN = "markdown"
    LATEX = "latex"
    QWENVL_HTML = "qwenvl_html"
    QWENVL_MARKDOWN = "qwenvl_markdown"


class BBox2D(BaseModel):
    """2D bounding box in relative coordinates (0-1000)."""
    x1: float = Field(..., ge=0, le=1000, description="Top-left x coordinate")
    y1: float = Field(..., ge=0, le=1000, description="Top-left y coordinate")
    x2: float = Field(..., ge=0, le=1000, description="Bottom-right x coordinate")
    y2: float = Field(..., ge=0, le=1000, description="Bottom-right y coordinate")


class Point2D(BaseModel):
    """2D point in relative coordinates (0-1000)."""
    x: float = Field(..., ge=0, le=1000, description="X coordinate")
    y: float = Field(..., ge=0, le=1000, description="Y coordinate")


class InferenceRequest(BaseModel):
    """Base inference request."""
    prompt: str = Field(..., description="Text prompt for the model")
    max_tokens: Optional[int] = Field(2048, ge=1, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.0, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class ImageInferenceRequest(InferenceRequest):
    """Image-based inference request."""
    image_url: Optional[str] = Field(None, description="URL to the image")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    min_pixels: Optional[int] = Field(64 * 32 * 32, description="Minimum pixels for image processing")
    max_pixels: Optional[int] = Field(2048 * 32 * 32, description="Maximum pixels for image processing")


class VideoInferenceRequest(InferenceRequest):
    """Video-based inference request."""
    video_url: Optional[str] = Field(None, description="URL to the video file")
    video_base64: Optional[str] = Field(None, description="Base64 encoded video file")
    frame_urls: Optional[List[str]] = Field(None, description="List of frame URLs")
    frame_base64_list: Optional[List[str]] = Field(None, description="List of base64 encoded frames")
    max_frames: Optional[int] = Field(2048, description="Maximum number of frames")
    sample_fps: Optional[float] = Field(2.0, description="Sampling FPS")
    total_pixels: Optional[int] = Field(20480 * 32 * 32, description="Total pixels budget")
    min_pixels: Optional[int] = Field(64 * 32 * 32, description="Minimum pixels per frame")


class Grounding2DRequest(ImageInferenceRequest):
    """2D grounding request."""
    categories: Optional[List[str]] = Field(None, description="Object categories to detect")
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")
    include_attributes: bool = Field(False, description="Include additional attributes")


class SpatialUnderstandingRequest(ImageInferenceRequest):
    """Spatial understanding request."""
    query: str = Field(..., description="Spatial reasoning query")
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")


class VideoUnderstandingRequest(VideoInferenceRequest):
    """Video understanding request."""
    task: str = Field("description", description="Video understanding task type")


class ImageDescriptionRequest(ImageInferenceRequest):
    """Image description request."""
    detail_level: str = Field("detailed", description="Level of detail: basic, detailed, comprehensive")


class DocumentParsingRequest(ImageInferenceRequest):
    """Document parsing request."""
    output_format: OutputFormat = Field(
        OutputFormat.QWENVL_HTML,
        description="Output format: html, markdown, qwenvl_html, qwenvl_markdown"
    )


class OCRRequest(ImageInferenceRequest):
    """OCR request."""
    output_format: OutputFormat = Field(OutputFormat.TEXT, description="Output format")
    granularity: str = Field("line", description="OCR granularity: word, line, paragraph")
    include_bbox: bool = Field(False, description="Include bounding boxes")


class ImageComparisonRequest(InferenceRequest):
    """Image comparison request for detecting differences between 2-4 images."""
    image_urls: Optional[List[str]] = Field(None, description="List of image URLs (2-4 images)")
    image_base64_list: Optional[List[str]] = Field(None, description="List of base64 encoded images (2-4 images)")
    comparison_type: str = Field("differences", description="Type of comparison: differences, changes, similarities")
    output_format: OutputFormat = Field(OutputFormat.JSON, description="Output format")
    min_pixels: Optional[int] = Field(64 * 32 * 32, description="Minimum pixels for image processing")
    max_pixels: Optional[int] = Field(2048 * 32 * 32, description="Maximum pixels for image processing")


class InferenceResponse(BaseModel):
    """Base inference response."""
    success: bool = Field(..., description="Whether the request was successful")
    result: Any = Field(..., description="Inference result")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")
