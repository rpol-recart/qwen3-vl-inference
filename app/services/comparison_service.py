"""Service for image comparison tasks."""
import logging
from typing import List, Optional
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import get_image_from_request, parse_json_response
from app.schemas import ImageComparisonRequest, InferenceResponse

logger = logging.getLogger(__name__)


class ImageComparisonService:
    """Service for comparing multiple images and detecting differences."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize image comparison service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    def _build_comparison_prompt(
        self,
        comparison_type: str,
        output_format: str,
        num_images: int,
    ) -> str:
        """
        Build prompt for image comparison task.

        Args:
            comparison_type: Type of comparison (differences, changes, similarities)
            output_format: Output format (json, text)
            num_images: Number of images to compare

        Returns:
            Formatted prompt string
        """
        if comparison_type == "differences":
            base_prompt = f"Compare these {num_images} images and identify all differences between them. "
            base_prompt += "Focus on changes in objects, positions, colors, text, or any visual elements. "
        elif comparison_type == "changes":
            base_prompt = f"Analyze these {num_images} images in sequence and describe what has changed from one image to the next. "
            base_prompt += "Focus on temporal changes, movements, additions, or removals. "
        elif comparison_type == "similarities":
            base_prompt = f"Compare these {num_images} images and identify common elements and similarities. "
            base_prompt += "Focus on shared objects, patterns, themes, or visual characteristics. "
        else:
            # Default to differences
            base_prompt = f"Compare these {num_images} images and identify all differences between them. "

        if output_format == "json":
            base_prompt += (
                "Provide a detailed analysis in JSON format with the following structure: "
                '{"summary": "brief overview", "differences": [{"description": "...", "location": "...", '
                '"images_affected": [1, 2]}], "common_elements": ["..."]}'
            )
        else:
            base_prompt += "Provide a detailed textual analysis of the comparison."

        return base_prompt

    def _build_multi_image_message(
        self,
        image_inputs: List[str],
        prompt: str,
        min_pixels: int,
        max_pixels: int,
    ) -> List[dict]:
        """
        Build message format for multi-image comparison.

        Args:
            image_inputs: List of image URLs or data URLs
            prompt: Text prompt
            min_pixels: Minimum pixels for image processing
            max_pixels: Maximum pixels for image processing

        Returns:
            List of message dictionaries
        """
        content = []

        # Add all images first
        for i, image_input in enumerate(image_inputs):
            content.append({
                "type": "image",
                "image": image_input,
                "min_pixels": min_pixels,
                "max_pixels": max_pixels,
            })

        # Add the text prompt at the end
        content.append({
            "type": "text",
            "text": prompt,
        })

        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
        return messages

    async def perform_comparison(self, request: ImageComparisonRequest) -> InferenceResponse:
        """
        Perform image comparison task.

        Args:
            request: Image comparison request

        Returns:
            Inference response with comparison results
        """
        try:
            # Get image inputs
            image_inputs = []

            if request.image_urls:
                if len(request.image_urls) < 2 or len(request.image_urls) > 4:
                    return InferenceResponse(
                        success=False,
                        result=None,
                        error="Number of images must be between 2 and 4",
                    )
                image_inputs = request.image_urls
            elif request.image_base64_list:
                if len(request.image_base64_list) < 2 or len(request.image_base64_list) > 4:
                    return InferenceResponse(
                        success=False,
                        result=None,
                        error="Number of images must be between 2 and 4",
                    )
                # Convert base64 to data URLs
                for base64_str in request.image_base64_list:
                    image_input = get_image_from_request(image_base64=base64_str)
                    image_inputs.append(image_input)
            else:
                return InferenceResponse(
                    success=False,
                    result=None,
                    error="Either image_urls or image_base64_list must be provided",
                )

            # Build prompt
            if not request.prompt or request.prompt.strip() == "":
                prompt = self._build_comparison_prompt(
                    comparison_type=request.comparison_type,
                    output_format=request.output_format.value,
                    num_images=len(image_inputs),
                )
            else:
                prompt = request.prompt

            # Build messages with multiple images
            messages = self._build_multi_image_message(
                image_inputs=image_inputs,
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
                    "task": "image_comparison",
                    "num_images": len(image_inputs),
                    "comparison_type": request.comparison_type,
                    "output_format": request.output_format.value,
                }
            )

        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )
