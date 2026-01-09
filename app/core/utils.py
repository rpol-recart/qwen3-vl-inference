"""Utility functions for image and video processing."""
import base64
import io
import os
import hashlib
import requests
from typing import Optional, List, Tuple, Union
from PIL import Image
import numpy as np
import logging

logger = logging.getLogger(__name__)


def decode_base64_image(base64_str: str) -> Image.Image:
    """
    Decode base64 string to PIL Image.

    Args:
        base64_str: Base64 encoded image string

    Returns:
        PIL Image object
    """
    # Remove data URL prefix if present
    if 'base64,' in base64_str:
        base64_str = base64_str.split('base64,')[1]

    image_data = base64.b64decode(base64_str)
    image = Image.open(io.BytesIO(image_data))
    return image


def encode_image_to_base64(image: Union[Image.Image, str]) -> str:
    """
    Encode PIL Image or image path to base64 string.

    Args:
        image: PIL Image or path to image file

    Returns:
        Base64 encoded string
    """
    if isinstance(image, str):
        with open(image, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    buffered = io.BytesIO()
    image.save(buffered, format=image.format or 'PNG')
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def download_image(url: str) -> Image.Image:
    """
    Download image from URL.

    Args:
        url: Image URL

    Returns:
        PIL Image object
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        return image
    except Exception as e:
        logger.error(f"Failed to download image from {url}: {e}")
        raise


def get_image_from_request(
    image_url: Optional[str] = None,
    image_base64: Optional[str] = None,
) -> str:
    """
    Get image path or URL from request parameters.

    Args:
        image_url: URL to image
        image_base64: Base64 encoded image

    Returns:
        Image URL or local path
    """
    if image_url:
        return image_url
    elif image_base64:
        # For base64, we return a data URL
        if not image_base64.startswith('data:'):
            # Assume it's a JPEG if no format specified
            image_base64 = f"data:image/jpeg;base64,{image_base64}"
        return image_base64
    else:
        raise ValueError("Either image_url or image_base64 must be provided")


def decode_base64_video(base64_str: str, output_path: str) -> str:
    """
    Decode base64 string to video file.

    Args:
        base64_str: Base64 encoded video string
        output_path: Path where to save the video file

    Returns:
        Path to the saved video file
    """
    try:
        # Remove data URL prefix if present
        if 'base64,' in base64_str:
            base64_str = base64_str.split('base64,')[1]

        video_data = base64.b64decode(base64_str)

        with open(output_path, 'wb') as f:
            f.write(video_data)

        logger.info(f"Video decoded and saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Failed to decode base64 video: {e}")
        raise


def encode_video_to_base64(video_path: str) -> str:
    """
    Encode video file to base64 string.

    Args:
        video_path: Path to video file

    Returns:
        Base64 encoded string
    """
    try:
        with open(video_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encode video to base64: {e}")
        raise


def download_video(url: str, dest_path: str) -> None:
    """
    Download video from URL to destination path.

    Args:
        url: Video URL
        dest_path: Destination file path
    """
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Video downloaded to {dest_path}")
    except Exception as e:
        logger.error(f"Failed to download video from {url}: {e}")
        raise


def get_video_from_request(
    video_url: Optional[str] = None,
    video_base64: Optional[str] = None,
    temp_dir: str = "/tmp"
) -> str:
    """
    Get video path from request parameters.

    Args:
        video_url: URL to video
        video_base64: Base64 encoded video
        temp_dir: Temporary directory for saving base64 videos

    Returns:
        Video file path or URL
    """
    if video_url:
        return video_url
    elif video_base64:
        # Save base64 video to temporary file
        import uuid

        os.makedirs(temp_dir, exist_ok=True)
        temp_file = os.path.join(temp_dir, f"video_{uuid.uuid4().hex}.mp4")
        decode_base64_video(video_base64, temp_file)
        return temp_file
    else:
        raise ValueError("Either video_url or video_base64 must be provided")


def get_frames_from_request(
    frame_urls: Optional[List[str]] = None,
    frame_base64_list: Optional[List[str]] = None,
) -> List[str]:
    """
    Get frame URLs or data URLs from request parameters.

    Args:
        frame_urls: List of frame URLs
        frame_base64_list: List of base64 encoded frames

    Returns:
        List of frame URLs or data URLs
    """
    if frame_urls:
        return frame_urls
    elif frame_base64_list:
        # Convert base64 frames to data URLs
        data_urls = []
        for i, base64_str in enumerate(frame_base64_list):
            if not base64_str.startswith('data:'):
                # Assume JPEG format
                base64_str = f"data:image/jpeg;base64,{base64_str}"
            data_urls.append(base64_str)
        return data_urls
    else:
        raise ValueError("Either frame_urls or frame_base64_list must be provided")


def build_image_message(
    image_input: str,
    prompt: str,
    min_pixels: int = 64 * 32 * 32,
    max_pixels: int = 2048 * 32 * 32,
) -> List[dict]:
    """
    Build message format for image inference.

    Args:
        image_input: Image URL or data URL
        prompt: Text prompt
        min_pixels: Minimum pixels for image processing
        max_pixels: Maximum pixels for image processing

    Returns:
        List of message dictionaries
    """
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image_input,
                    "min_pixels": min_pixels,
                    "max_pixels": max_pixels,
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }
    ]
    return messages


def build_video_message(
    video_input: Union[str, List[str]],
    prompt: str,
    total_pixels: int = 20480 * 32 * 32,
    min_pixels: int = 64 * 32 * 32,
    max_frames: int = 2048,
    sample_fps: float = 2.0,
) -> List[dict]:
    """
    Build message format for video inference.

    Args:
        video_input: Video URL or list of frame URLs
        prompt: Text prompt
        total_pixels: Total pixels budget
        min_pixels: Minimum pixels per frame
        max_frames: Maximum number of frames
        sample_fps: Sampling FPS

    Returns:
        List of message dictionaries
    """
    if isinstance(video_input, str):
        # Single video file
        content = [
            {
                "type": "video",
                "video": video_input,
                "total_pixels": total_pixels,
                "min_pixels": min_pixels,
                "max_frames": max_frames,
                "sample_fps": sample_fps,
            },
            {
                "type": "text",
                "text": prompt,
            },
        ]
    else:
        # List of frames
        content = [
            {
                "type": "video",
                "video": video_input,
                "total_pixels": total_pixels,
                "min_pixels": min_pixels,
                "max_frames": max_frames,
                "sample_fps": sample_fps,
            },
            {
                "type": "text",
                "text": prompt,
            },
        ]

    messages = [
        {
            "role": "user",
            "content": content,
        }
    ]
    return messages


def parse_json_response(response: str) -> str:
    """
    Parse JSON from model response (removes markdown fencing).

    Args:
        response: Model response text

    Returns:
        Cleaned JSON string
    """
    lines = response.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "```json":
            response = "\n".join(lines[i + 1:])
            response = response.split("```")[0]
            break
    return response.strip()


def build_grounding_prompt(
    categories: Optional[List[str]] = None,
    include_attributes: bool = False,
    output_format: str = "json",
) -> str:
    """
    Build prompt for 2D grounding task.

    Args:
        categories: List of object categories to detect
        include_attributes: Whether to include additional attributes
        output_format: Output format (json, xml, etc.)

    Returns:
        Formatted prompt string
    """
    if categories:
        category_str = ", ".join(f'"{cat}"' for cat in categories)
        base_prompt = f'Locate every instance that belongs to the following categories: {category_str}. '
    else:
        base_prompt = 'Detect all objects in the image. '

    if include_attributes:
        base_prompt += (
            'For each object, report bbox coordinates, label, and any relevant attributes '
            '(such as color, type, etc.) in JSON format like: '
            '{"bbox_2d": [x1, y1, x2, y2], "label": "object_name", "attributes": {...}}.'
        )
    else:
        base_prompt += 'Report bbox coordinates in JSON format.'

    return base_prompt
