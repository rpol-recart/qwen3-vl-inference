"""Service for OCR tasks."""
import logging
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import build_image_message, parse_json_response, get_image_from_request
from app.schemas import OCRRequest, InferenceResponse, OutputFormat

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR (Optical Character Recognition)."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize OCR service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    def _build_ocr_prompt(
        self,
        granularity: str,
        include_bbox: bool,
        output_format: OutputFormat,
        is_wild: bool = False,
    ) -> str:
        """Build prompt based on OCR requirements."""
        if is_wild:
            # For wild/natural images
            base_prompt = "Read and extract all visible text from the image, including text on signs, labels, and any other surfaces. "
        else:
            # For documents
            base_prompt = "Read all the text in the image. "

        if include_bbox:
            if granularity == "word":
                base_prompt += (
                    "Spotting all the text in the image with word-level, and output in JSON format as "
                    "[{'bbox_2d': [x1, y1, x2, y2], 'text_content': 'text'}, ...]."
                )
            elif granularity == "line":
                base_prompt += (
                    "Spotting all the text in the image with line-level, and output in JSON format as "
                    "[{'bbox_2d': [x1, y1, x2, y2], 'text_content': 'text'}, ...]."
                )
            else:  # paragraph
                base_prompt += (
                    "Spotting all the text in the image with paragraph-level, and output in JSON format as "
                    "[{'bbox_2d': [x1, y1, x2, y2], 'text_content': 'text'}, ...]."
                )
        else:
            if output_format == OutputFormat.JSON:
                base_prompt += "Output the text content in JSON format."
            else:
                base_prompt += "Please output only the text content from the image without any additional descriptions or formatting."

        return base_prompt

    async def perform_ocr(self, request: OCRRequest, is_wild: bool = False) -> InferenceResponse:
        """
        Perform OCR task.

        Args:
            request: OCR request
            is_wild: Whether this is wild/natural image OCR

        Returns:
            Inference response
        """
        try:
            # Get image input
            image_input = get_image_from_request(request.image_url, request.image_base64)

            # Build prompt
            if request.prompt:
                prompt = request.prompt
            else:
                prompt = self._build_ocr_prompt(
                    granularity=request.granularity,
                    include_bbox=request.include_bbox,
                    output_format=request.output_format,
                    is_wild=is_wild,
                )

            # Build messages
            messages = build_image_message(
                image_input=image_input,
                prompt=prompt,
                min_pixels=request.min_pixels or 512 * 32 * 32,
                max_pixels=request.max_pixels or 2048 * 32 * 32,
            )

            # Generate response
            result = self.engine.generate(
                messages=messages,
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature or 0.0,
                top_p=request.top_p or 1.0,
                seed=request.seed,
            )

            # Parse JSON if needed
            if request.include_bbox or request.output_format == OutputFormat.JSON:
                result = parse_json_response(result)

            task_type = "wild_ocr" if is_wild else "document_ocr"

            return InferenceResponse(
                success=True,
                result=result,
                metadata={
                    "task": task_type,
                    "granularity": request.granularity,
                    "include_bbox": request.include_bbox,
                    "output_format": request.output_format.value,
                }
            )

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )

    async def perform_document_ocr(self, request: OCRRequest) -> InferenceResponse:
        """Perform document OCR."""
        return await self.perform_ocr(request, is_wild=False)

    async def perform_wild_ocr(self, request: OCRRequest) -> InferenceResponse:
        """Perform wild/natural image OCR."""
        return await self.perform_ocr(request, is_wild=True)
