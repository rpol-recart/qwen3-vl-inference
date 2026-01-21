"""Example of using Image Comparison endpoint."""
import requests
import json


def compare_images_url():
    """Example: Compare images using URLs."""
    url = "http://localhost:8000/api/v1/image/comparison"

    # Example 1: Find differences between two images
    print("=== Example 1: Comparing 2 Images (Differences) ===")
    data = {
        "image_urls": [
            "https://example.com/before.jpg",
            "https://example.com/after.jpg"
        ],
        "comparison_type": "differences",
        "output_format": "json",
        "prompt": ""
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example 2: Analyze changes across 3 images (temporal sequence)
    print("\n=== Example 2: Comparing 3 Images (Changes) ===")
    data = {
        "image_urls": [
            "https://example.com/frame1.jpg",
            "https://example.com/frame2.jpg",
            "https://example.com/frame3.jpg"
        ],
        "comparison_type": "changes",
        "output_format": "json",
        "prompt": ""
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Example 3: Find similarities across 4 images
    print("\n=== Example 3: Comparing 4 Images (Similarities) ===")
    data = {
        "image_urls": [
            "https://example.com/product1.jpg",
            "https://example.com/product2.jpg",
            "https://example.com/product3.jpg",
            "https://example.com/product4.jpg"
        ],
        "comparison_type": "similarities",
        "output_format": "json",
        "prompt": ""
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))


def compare_images_base64():
    """Example: Compare images using base64."""
    import base64

    url = "http://localhost:8000/api/v1/image/comparison"

    # Read and encode images
    image_paths = ["image1.jpg", "image2.jpg"]
    image_base64_list = []

    for path in image_paths:
        try:
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
                image_base64_list.append(image_data)
        except FileNotFoundError:
            print(f"Warning: {path} not found, skipping...")
            continue

    if len(image_base64_list) >= 2:
        print("=== Comparing Images from Base64 ===")
        data = {
            "image_base64_list": image_base64_list,
            "comparison_type": "differences",
            "output_format": "json",
            "prompt": ""
        }

        response = requests.post(url, json=data)
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Not enough images found for comparison")


def compare_with_custom_prompt():
    """Example: Compare images with custom prompt."""
    url = "http://localhost:8000/api/v1/image/comparison"

    print("=== Custom Prompt Comparison ===")
    data = {
        "image_urls": [
            "https://example.com/room_before.jpg",
            "https://example.com/room_after.jpg"
        ],
        "comparison_type": "differences",
        "output_format": "json",
        "prompt": "Compare these two images of the same room and identify all furniture and decoration changes. Pay special attention to color changes, new or removed items, and repositioned objects."
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))


def compare_with_parameters():
    """Example: Compare images with additional parameters."""
    url = "http://localhost:8000/api/v1/image/comparison"

    print("=== Comparison with Custom Parameters ===")
    data = {
        "image_urls": [
            "https://example.com/scene1.jpg",
            "https://example.com/scene2.jpg",
            "https://example.com/scene3.jpg"
        ],
        "comparison_type": "differences",
        "output_format": "json",
        "prompt": "",
        "max_tokens": 3072,
        "temperature": 0.1,
        "top_p": 0.9,
        "min_pixels": 32768,
        "max_pixels": 1048576
    }

    response = requests.post(url, json=data)
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """Run all examples."""
    print("=" * 80)
    print("Image Comparison Examples for Qwen3-VL Inference Server")
    print("=" * 80)

    # Run examples
    try:
        compare_images_url()
    except Exception as e:
        print(f"Error in compare_images_url: {e}")

    print("\n" + "=" * 80 + "\n")

    try:
        compare_images_base64()
    except Exception as e:
        print(f"Error in compare_images_base64: {e}")

    print("\n" + "=" * 80 + "\n")

    try:
        compare_with_custom_prompt()
    except Exception as e:
        print(f"Error in compare_with_custom_prompt: {e}")

    print("\n" + "=" * 80 + "\n")

    try:
        compare_with_parameters()
    except Exception as e:
        print(f"Error in compare_with_parameters: {e}")


if __name__ == "__main__":
    main()
