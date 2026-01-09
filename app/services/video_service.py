"""Service for video understanding tasks."""
import logging
from typing import Optional, Union, List
from app.core.inference_engine import Qwen3VLInferenceEngine
from app.core.utils import build_video_message, get_video_from_request, get_frames_from_request
from app.schemas import VideoUnderstandingRequest, InferenceResponse

logger = logging.getLogger(__name__)


class VideoUnderstandingService:
    """Service for video understanding and analysis."""

    def __init__(self, engine: Qwen3VLInferenceEngine):
        """
        Initialize video understanding service.

        Args:
            engine: Inference engine instance
        """
        self.engine = engine

    def _get_video_input(self, request: VideoUnderstandingRequest) -> Union[str, List[str]]:
        """Get video input from request."""
        # Priority: video_url -> video_base64 -> frame_urls -> frame_base64_list
        if request.video_url or request.video_base64:
            return get_video_from_request(
                video_url=request.video_url,
                video_base64=request.video_base64
            )
        elif request.frame_urls or request.frame_base64_list:
            return get_frames_from_request(
                frame_urls=request.frame_urls,
                frame_base64_list=request.frame_base64_list
            )
        else:
            raise ValueError(
                "One of video_url, video_base64, frame_urls, or frame_base64_list must be provided"
            )

    async def perform_video_understanding(
        self, request: VideoUnderstandingRequest
    ) -> InferenceResponse:
        """
        Perform video understanding task.

        Args:
            request: Video understanding request

        Returns:
            Inference response
        """
        try:
            # Get video input
            video_input = self._get_video_input(request)

            # Use prompt from request
            prompt = request.prompt

            # Build messages
            messages = build_video_message(
                video_input=video_input,
                prompt=prompt,
                total_pixels=request.total_pixels or 20480 * 32 * 32,
                min_pixels=request.min_pixels or 64 * 32 * 32,
                max_frames=request.max_frames or 2048,
                sample_fps=request.sample_fps or 2.0,
            )

            # Generate response
            result = self.engine.generate(
                messages=messages,
                max_tokens=request.max_tokens or 2048,
                temperature=request.temperature or 0.0,
                top_p=request.top_p or 1.0,
                seed=request.seed,
            )

            # Determine video type for metadata
            video_type = "unknown"
            if request.video_url:
                video_type = "url"
            elif request.video_base64:
                video_type = "base64"
            elif request.frame_urls:
                video_type = "frame_urls"
            elif request.frame_base64_list:
                video_type = "frame_base64_list"

            return InferenceResponse(
                success=True,
                result=result,
                metadata={
                    "task": "video_understanding",
                    "video_type": video_type,
                }
            )

        except Exception as e:
            logger.error(f"Video understanding failed: {e}")
            return InferenceResponse(
                success=False,
                result=None,
                error=str(e),
            )
