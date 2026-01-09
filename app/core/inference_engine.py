"""vLLM-based inference engine for Qwen3-VL model."""
import os
import logging
from typing import Optional, Union, List, Dict, Any
import torch
from vllm import LLM, SamplingParams
from transformers import AutoProcessor
from qwen_vl_utils import process_vision_info

logger = logging.getLogger(__name__)


class Qwen3VLInferenceEngine:
    """vLLM-based inference engine for Qwen3-VL."""

    def __init__(
        self,
        model_path: str,
        gpu_memory_utilization: float = 0.70,
        tensor_parallel_size: Optional[int] = None,
        trust_remote_code: bool = True,
        enforce_eager: bool = False,
        max_model_len: Optional[int] = None,
    ):
        """
        Initialize the inference engine.

        Args:
            model_path: Path to the model weights
            gpu_memory_utilization: GPU memory utilization ratio
            tensor_parallel_size: Number of GPUs for tensor parallelism
            trust_remote_code: Whether to trust remote code
            enforce_eager: Whether to enforce eager execution
            max_model_len: Maximum model length
        """
        self.model_path = model_path
        self.model: Optional[LLM] = None
        self.processor: Optional[AutoProcessor] = None

        # Set environment variable for vLLM
        os.environ['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'

        # Determine tensor parallel size
        if tensor_parallel_size is None:
            tensor_parallel_size = torch.cuda.device_count() if torch.cuda.is_available() else 1

        logger.info(f"Initializing Qwen3-VL Inference Engine with model: {model_path}")
        logger.info(f"Tensor parallel size: {tensor_parallel_size}")
        logger.info(f"GPU memory utilization: {gpu_memory_utilization}")

        try:
            # Initialize vLLM engine
            self.model = LLM(
                model=model_path,
                trust_remote_code=trust_remote_code,
                gpu_memory_utilization=gpu_memory_utilization,
                enforce_eager=enforce_eager,
                tensor_parallel_size=tensor_parallel_size,
                seed=0,
                max_model_len=max_model_len,
            )

            # Load processor
            self.processor = AutoProcessor.from_pretrained(model_path)

            logger.info("Inference engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize inference engine: {e}")
            raise

    def prepare_image_inputs(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Prepare inputs for image-based inference.

        Args:
            messages: List of message dictionaries

        Returns:
            Dictionary with prompt and multimodal data
        """
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        image_inputs, video_inputs, video_kwargs = process_vision_info(
            messages,
            image_patch_size=self.processor.image_processor.patch_size,
            return_video_kwargs=True,
            return_video_metadata=True
        )

        mm_data = {}
        if image_inputs is not None:
            mm_data['image'] = image_inputs
        if video_inputs is not None:
            mm_data['video'] = video_inputs

        return {
            'prompt': text,
            'multi_modal_data': mm_data,
            'mm_processor_kwargs': video_kwargs
        }

    def prepare_video_inputs(
        self,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Prepare inputs for video-based inference.

        Args:
            messages: List of message dictionaries

        Returns:
            Dictionary with prompt and multimodal data
        """
        # Video processing uses the same preparation as image
        return self.prepare_image_inputs(messages)

    def generate(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048,
        temperature: float = 0.0,
        top_p: float = 1.0,
        seed: Optional[int] = None,
    ) -> str:
        """
        Generate response from the model.

        Args:
            messages: List of message dictionaries
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            seed: Random seed

        Returns:
            Generated text response
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not initialized")

        try:
            # Prepare inputs
            inputs = self.prepare_image_inputs(messages)

            # Create sampling parameters
            sampling_params = SamplingParams(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                seed=seed if seed is not None else 0,
            )

            # Generate
            outputs = self.model.generate(inputs, sampling_params=sampling_params)

            # Extract generated text
            if outputs and len(outputs) > 0:
                output = outputs[0]
                if output.outputs and len(output.outputs) > 0:
                    return output.outputs[0].text

            return ""
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def generate_stream(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048,
        temperature: float = 0.0,
        top_p: float = 1.0,
        seed: Optional[int] = None,
    ):
        """
        Generate response from the model with streaming.

        Args:
            messages: List of message dictionaries
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            seed: Random seed

        Yields:
            Generated text chunks
        """
        if self.model is None or self.processor is None:
            raise RuntimeError("Model not initialized")

        try:
            # Prepare inputs
            inputs = self.prepare_image_inputs(messages)

            # Create sampling parameters
            sampling_params = SamplingParams(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                seed=seed if seed is not None else 0,
            )

            # Generate with streaming
            accumulated_text = ''
            for output in self.model.generate(inputs, sampling_params=sampling_params):
                for completion in output.outputs:
                    new_text = completion.text
                    if new_text:
                        # Yield only the new portion
                        yield new_text[len(accumulated_text):]
                        accumulated_text = new_text
        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            raise

    def is_ready(self) -> bool:
        """Check if the engine is ready."""
        return self.model is not None and self.processor is not None
