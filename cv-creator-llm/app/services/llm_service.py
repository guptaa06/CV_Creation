"""
LLM Service for interacting with Ollama models (gemma:2b and llama3.2-vision:11b)
"""
import requests
import json
import logging
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama API"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.text_model = settings.TEXT_MODEL
        self.vision_model = settings.VISION_MODEL
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

    def _make_request(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        format_json: bool = False,
    ) -> str:
        """
        Make request to Ollama API

        Args:
            model: Model name
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            format_json: Whether to request JSON format

        Returns:
            Model response text
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt

        if format_json:
            payload["format"] = "json"

        try:
            logger.info(f"Making request to Ollama with model: {model}")
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "").strip()

        except requests.exceptions.Timeout:
            logger.error("Request to Ollama timed out")
            raise TimeoutError("LLM request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            raise RuntimeError(f"Failed to call LLM: {str(e)}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate text using text model

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature
            model: Optional model override (defaults to text_model)

        Returns:
            Generated text
        """
        return self._make_request(
            model=model or self.text_model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = 0.3,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using text model

        Args:
            prompt: User prompt
            system_prompt: System instruction
            temperature: Sampling temperature (lower for structured output)
            model: Optional model override (defaults to text_model)

        Returns:
            Parsed JSON response
        """
        response = self._make_request(
            model=model or self.text_model,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            format_json=True,
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract and fix JSON from response
            logger.warning(f"Failed to parse JSON: {str(e)}, attempting to fix")
            import re

            # Remove markdown code blocks if present
            cleaned = re.sub(r'```json\s*|\s*```', '', response)
            cleaned = cleaned.strip()

            # Try parsing cleaned response
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError:
                # Extract JSON object
                json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if json_match:
                    try:
                        json_str = json_match.group()

                        # Apply multiple JSON fixes
                        # 1. Remove trailing commas before } or ]
                        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

                        # 2. Fix missing commas after ] followed by }
                        json_str = re.sub(r'(\])\s*\n\s*(\})', r'\1,\2', json_str)

                        # 3. Fix missing commas after ] followed by "
                        json_str = re.sub(r'(\])\s*\n\s*(")', r'\1,\2', json_str)

                        # 4. Fix missing commas after } followed by {
                        json_str = re.sub(r'(\})\s*\n\s*(\{)', r'\1,\2', json_str)

                        # 5. Fix missing commas after } followed by "
                        json_str = re.sub(r'(\})\s*\n\s*(")', r'\1,\2', json_str)

                        # 6. Remove newlines within string values
                        json_str = re.sub(r':\s*"([^"]*)\n([^"]*)"', r': "\1 \2"', json_str)

                        # 7. Fix multiple consecutive commas
                        json_str = re.sub(r',\s*,', ',', json_str)

                        # 5. Try to use a more lenient JSON parser
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            # Last resort: try to manually fix the JSON structure
                            # Log the problematic part
                            logger.error(f"JSON still invalid. First 1000 chars: {json_str[:1000]}")
                            logger.error(f"Last 500 chars: {json_str[-500:]}")

                            # Try json5 library if available (more lenient)
                            try:
                                import json5
                                return json5.loads(json_str)
                            except ImportError:
                                pass
                            except Exception as e3:
                                logger.error(f"json5 also failed: {str(e3)}")

                            raise ValueError(f"Failed to parse LLM response as JSON after all fixes. Error: {str(e)}")

                    except json.JSONDecodeError as e2:
                        logger.error(f"JSON parsing failed after fixes: {str(e2)}")
                        logger.error(f"Response length: {len(response)}")
                        logger.error(f"First 500 chars: {response[:500]}")
                        raise ValueError(f"Failed to parse LLM response as JSON: {str(e2)}")
                raise ValueError("No valid JSON found in LLM response")

    def analyze_with_vision(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Analyze document using vision model (llama3.2-vision:11b)

        Args:
            prompt: Analysis prompt
            image_path: Path to image file
            system_prompt: System instruction

        Returns:
            Analysis result
        """
        # For vision model, we can process document images
        # This is useful for understanding layout and formatting
        return self._make_request(
            model=self.vision_model,
            prompt=prompt,
            system_prompt=system_prompt,
        )

    def check_model_availability(self, model_name: str) -> bool:
        """
        Check if a model is available in Ollama

        Args:
            model_name: Name of the model

        Returns:
            True if model is available
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            models = response.json().get("models", [])
            available_models = [m.get("name", "") for m in models]

            return model_name in available_models

        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False

    def verify_models(self) -> Dict[str, bool]:
        """
        Verify that required models are available

        Returns:
            Dictionary with model availability status
        """
        return {
            "text_model": self.check_model_availability(self.text_model),
            "vision_model": self.check_model_availability(self.vision_model),
        }

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of all available Ollama models

        Returns:
            List of available models with metadata
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            models = response.json().get("models", [])

            # Format model information
            formatted_models = []
            for model in models:
                formatted_models.append({
                    "name": model.get("name", ""),
                    "size": model.get("size", 0),
                    "modified": model.get("modified_at", ""),
                })

            return formatted_models

        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            return []


# Global instance
llm_service = OllamaService()
