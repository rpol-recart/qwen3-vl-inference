"""Service for spatial understanding tasks."""
import logging
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import build_image_message, parse_json_response, get_image_from_request
from app.schemas import SpatialUnderstandingRequest, InferenceResponse

logger = logging.getLogger(__name__)


class SpatialUnderstandingService:
    """Service for spatial understanding and reasoning."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize spatial understanding service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    async def perform_spatial_understanding(
        self, request: SpatialUnderstandingRequest
    ) -> InferenceResponse:
        """
        Perform spatial understanding task.

        Args:
            request: Spatial understanding request

        Returns:
            Inference response
        """
        try:
            # Get image input
            image_input = get_image_from_request(request.image_url, request.image_base64)

            # Use the query as prompt
            prompt = request.query

            # Build messages
            messages = build_image_message(
                image_input=image_input,
                prompt=prompt,
                min_pixels=request.min_pixels or 64 * 32 * 32,
                max_pixels=request.max_pixels or 2048 * 32 * 32,
            )

            # Generate response
            result = self.engine.generate(
                messages=messages,
                max_tokens=request.max_tokens or 2048,
                temperature=request.temperature or 0.0,
                top_p=request.top_p or 1.0,
                seed=request.seed,
            )

            # Parse JSON if needed
            if request.output_format.value == "json":
                result = parse_json_response(result)

            return InferenceResponse(
                success=True,
                result=result,
                metadata={
                    "task": "spatial_understanding",
                    "query": request.query,
                    "output_format": request.output_format.value,
                }
            )

        except Exception as e:
            logger.error(f"Spatial understanding failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )
