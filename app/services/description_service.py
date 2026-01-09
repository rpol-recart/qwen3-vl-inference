"""Service for image description tasks."""
import logging
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import build_image_message, get_image_from_request
from app.schemas import ImageDescriptionRequest, InferenceResponse

logger = logging.getLogger(__name__)


class ImageDescriptionService:
    """Service for detailed image description."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize image description service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    def _build_description_prompt(self, detail_level: str, custom_prompt: str = None) -> str:
        """Build prompt based on detail level."""
        if custom_prompt:
            return custom_prompt

        prompts = {
            "basic": "Provide a brief description of the image.",
            "detailed": "Provide a detailed description of the image, including objects, people, actions, and context.",
            "comprehensive": (
                "Provide a comprehensive and thorough description of the image. "
                "Include details about: objects and their attributes, people and their actions, "
                "spatial relationships, colors, textures, background elements, mood, and any text visible in the image."
            ),
        }
        return prompts.get(detail_level, prompts["detailed"])

    async def perform_image_description(
        self, request: ImageDescriptionRequest
    ) -> InferenceResponse:
        """
        Perform image description task.

        Args:
            request: Image description request

        Returns:
            Inference response
        """
        try:
            # Get image input
            image_input = get_image_from_request(request.image_url, request.image_base64)

            # Build prompt
            prompt = self._build_description_prompt(
                detail_level=request.detail_level,
                custom_prompt=request.prompt if request.prompt else None
            )

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

            return InferenceResponse(
                success=True,
                result=result,
                metadata={
                    "task": "image_description",
                    "detail_level": request.detail_level,
                }
            )

        except Exception as e:
            logger.error(f"Image description failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )
