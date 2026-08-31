import os
import time
import logging

from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError, ClientError

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiLLM:
    """
    Shared Gemini LLM wrapper for the Meridian AI Research Engine.

    Models:
    - gemini-3.5-flash-lite : Planner, Research, Extraction, Validation
    - gemini-3.5-flash      : Report Generation
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.client = genai.Client(api_key=api_key)

        # Two Gemini models used by different agents
        self.fast_model = "gemini-3.5-flash-lite"
        self.report_model = "gemini-3.5-flash"

        # Retry configuration
        self.max_retries = 5
        self.initial_delay = 2

    def generate(self, prompt: str, model_type: str = "fast") -> str:
        """
        Generate text from Gemini.

        Args:
            prompt: Prompt sent to Gemini.
            model_type:
                "fast"   -> gemini-3.5-flash-lite
                "report" -> gemini-3.5-flash

        Returns:
            Generated text.

        Raises:
            Exception after retry exhaustion or permanent errors.
        """

        model = (
            self.report_model
            if model_type == "report"
            else self.fast_model
        )

        delay = self.initial_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    f"Gemini request using {model} "
                    f"(attempt {attempt}/{self.max_retries})"
                )

                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                # SDK safety check
                if hasattr(response, "text") and response.text:
                    return response.text

                if hasattr(response, "output_text") and response.output_text:
                    return response.output_text

                raise ValueError("Gemini returned an empty response.")

            # Retryable server-side errors (500/503)
            except ServerError as e:
                logger.warning(
                    f"Gemini ServerError ({model}): {e}. "
                    f"Retrying in {delay}s..."
                )

                if attempt == self.max_retries:
                    logger.error("Gemini retries exhausted.")
                    raise

                time.sleep(delay)
                delay *= 2

            # Retry only temporary client errors
            except ClientError as e:
                message = str(e)

                retryable = any(
                    code in message
                    for code in ["429", "500", "503", "UNAVAILABLE"]
                )

                if retryable:
                    logger.warning(
                        f"Gemini temporary error ({model}): {message}. "
                        f"Retrying in {delay}s..."
                    )

                    if attempt == self.max_retries:
                        logger.error("Gemini retries exhausted.")
                        raise

                    time.sleep(delay)
                    delay *= 2

                else:
                    logger.error(
                        f"Gemini permanent ClientError ({model}): {message}"
                    )
                    raise

            except Exception as e:
                logger.exception(
                    f"Unexpected Gemini error using {model}: {e}"
                )
                raise

    # -------------------------------------------------------
    # Convenience methods for agents
    # -------------------------------------------------------

    def generate_fast(self, prompt: str) -> str:
        """Planner / Research / Extraction / Validation"""
        return self.generate(prompt, model_type="fast")

    def generate_report(self, prompt: str) -> str:
        """Report generation"""
        return self.generate(prompt, model_type="report")