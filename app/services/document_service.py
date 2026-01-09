"""Service for document parsing tasks."""
import logging
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import build_image_message, get_image_from_request
from app.schemas import DocumentParsingRequest, InferenceResponse, OutputFormat

logger = logging.getLogger(__name__)


class DocumentParsingService:
    """Service for document parsing and extraction."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize document parsing service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    def _build_parsing_prompt(self, output_format: OutputFormat) -> str:
        """Build prompt based on output format."""
        format_prompts = {
            OutputFormat.HTML: "Convert the document to HTML format.",
            OutputFormat.MARKDOWN: "Convert the document to Markdown format.",
            OutputFormat.QWENVL_HTML: "qwenvl html",
            OutputFormat.QWENVL_MARKDOWN: "qwenvl markdown",
            OutputFormat.JSON: "Parse the document and output structured information in JSON format.",
        }
        return format_prompts.get(output_format, format_prompts[OutputFormat.QWENVL_HTML])

    async def perform_document_parsing(
        self, request: DocumentParsingRequest
    ) -> InferenceResponse:
        """
        Perform document parsing task.

        Args:
            request: Document parsing request

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
                prompt = self._build_parsing_prompt(request.output_format)

            # Build messages
            messages = build_image_message(
                image_input=image_input,
                prompt=prompt,
                min_pixels=request.min_pixels or 512 * 32 * 32,
                max_pixels=request.max_pixels or 4608 * 32 * 32,
            )

            # Generate response
            result = self.engine.generate(
                messages=messages,
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature or 0.0,
                top_p=request.top_p or 1.0,
                seed=request.seed,
            )

            return InferenceResponse(
                success=True,
                result=result,
                metadata={
                    "task": "document_parsing",
                    "output_format": request.output_format.value,
                }
            )

        except Exception as e:
            logger.error(f"Document parsing failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )
