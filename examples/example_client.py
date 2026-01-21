"""Example client for Qwen3-VL Inference Server."""
import requests
import json
from typing import Dict, Any


class Qwen3VLClient:
    """Client for Qwen3-VL Inference Server."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize client.

        Args:
            base_url: Base URL of the inference server
        """
        self.base_url = base_url.rstrip("/")

    def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        response = requests.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    def grounding_2d(
        self,
        image_url: str = None,
        image_base64: str = None,
        categories: list = None,
        prompt: str = None,
        include_attributes: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform 2D object grounding.

        Args:
            image_url: URL to image
            image_base64: Base64 encoded image
            categories: List of object categories
            prompt: Custom prompt
            include_attributes: Include additional attributes
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "categories": categories,
            "prompt": prompt or "",
            "include_attributes": include_attributes,
            **kwargs
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/grounding/2d", json=data)
        response.raise_for_status()
        return response.json()

    def spatial_understanding(
        self,
        image_url: str = None,
        image_base64: str = None,
        query: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform spatial understanding.

        Args:
            image_url: URL to image
            image_base64: Base64 encoded image
            query: Spatial reasoning query
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "query": query,
            "prompt": query,  # Use query as prompt
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/spatial/understanding", json=data)
        response.raise_for_status()
        return response.json()

    def video_understanding(
        self,
        video_url: str = None,
        video_base64: str = None,
        frame_urls: list = None,
        frame_base64_list: list = None,
        prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform video understanding.

        Args:
            video_url: URL to video file
            video_base64: Base64 encoded video
            frame_urls: List of frame URLs
            frame_base64_list: List of base64 encoded frames
            prompt: Question about the video
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "video_url": video_url,
            "video_base64": video_base64,
            "frame_urls": frame_urls,
            "frame_base64_list": frame_base64_list,
            "prompt": prompt or "",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/video/understanding", json=data)
        response.raise_for_status()
        return response.json()

    def video_understanding_upload(
        self,
        video_path: str,
        prompt: str,
        max_frames: int = 128,
        sample_fps: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform video understanding with file upload.

        Args:
            video_path: Path to local video file
            prompt: Question about the video
            max_frames: Maximum frames to process
            sample_fps: Sampling FPS
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        import os

        with open(video_path, "rb") as f:
            files = {"file": (os.path.basename(video_path), f, "video/mp4")}
            data = {
                "prompt": prompt,
                "max_frames": max_frames,
                "sample_fps": sample_fps,
                **kwargs
            }

            response = requests.post(
                f"{self.base_url}/api/v1/video/understanding/upload",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()

    def image_description(
        self,
        image_url: str = None,
        image_base64: str = None,
        detail_level: str = "detailed",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image description.

        Args:
            image_url: URL to image
            image_base64: Base64 encoded image
            detail_level: Level of detail (basic, detailed, comprehensive)
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "detail_level": detail_level,
            "prompt": "",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/image/description", json=data)
        response.raise_for_status()
        return response.json()

    def document_parsing(
        self,
        image_url: str = None,
        image_base64: str = None,
        output_format: str = "qwenvl_html",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Parse document.

        Args:
            image_url: URL to document image
            image_base64: Base64 encoded image
            output_format: Output format (html, markdown, qwenvl_html, qwenvl_markdown)
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "output_format": output_format,
            "prompt": "",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/document/parsing", json=data)
        response.raise_for_status()
        return response.json()

    def document_ocr(
        self,
        image_url: str = None,
        image_base64: str = None,
        granularity: str = "line",
        include_bbox: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform document OCR.

        Args:
            image_url: URL to document image
            image_base64: Base64 encoded image
            granularity: OCR granularity (word, line, paragraph)
            include_bbox: Include bounding boxes
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "granularity": granularity,
            "include_bbox": include_bbox,
            "prompt": "",
            "output_format": "text",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/ocr/document", json=data)
        response.raise_for_status()
        return response.json()

    def wild_ocr(
        self,
        image_url: str = None,
        image_base64: str = None,
        include_bbox: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform wild/natural image OCR.

        Args:
            image_url: URL to image
            image_base64: Base64 encoded image
            include_bbox: Include bounding boxes
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_url": image_url,
            "image_base64": image_base64,
            "include_bbox": include_bbox,
            "prompt": "",
            "output_format": "text",
            "granularity": "line",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/ocr/wild", json=data)
        response.raise_for_status()
        return response.json()

    def image_comparison(
        self,
        image_urls: list = None,
        image_base64_list: list = None,
        comparison_type: str = "differences",
        output_format: str = "json",
        prompt: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Compare multiple images (2-4) and detect differences, changes, or similarities.

        Args:
            image_urls: List of image URLs (2-4 images)
            image_base64_list: List of base64 encoded images (2-4 images)
            comparison_type: Type of comparison (differences, changes, similarities)
            output_format: Output format (json, text)
            prompt: Custom prompt for comparison
            **kwargs: Additional parameters

        Returns:
            Response dictionary
        """
        data = {
            "image_urls": image_urls,
            "image_base64_list": image_base64_list,
            "comparison_type": comparison_type,
            "output_format": output_format,
            "prompt": prompt or "",
            **kwargs
        }
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.base_url}/api/v1/image/comparison", json=data)
        response.raise_for_status()
        return response.json()


def main():
    """Example usage."""
    client = Qwen3VLClient("http://localhost:8000")

    # Check health
    print("=== Health Check ===")
    health = client.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))

    # Example 1: 2D Grounding
    print("\n=== 2D Grounding ===")
    result = client.grounding_2d(
        image_url="https://example.com/image.jpg",
        categories=["person", "car"],
        include_attributes=True
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example 2: Image Description
    print("\n=== Image Description ===")
    result = client.image_description(
        image_url="https://example.com/image.jpg",
        detail_level="comprehensive"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example 3: Document OCR
    print("\n=== Document OCR ===")
    result = client.document_ocr(
        image_url="https://example.com/document.jpg",
        include_bbox=True,
        granularity="line"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example 4: Image Comparison
    print("\n=== Image Comparison ===")
    result = client.image_comparison(
        image_urls=[
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ],
        comparison_type="differences",
        output_format="json"
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
