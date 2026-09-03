import os
import re
import time
import logging

from dotenv import load_dotenv
from google import genai

from ai.llm.base import LLM

# =======================================================
# Load Environment Variables
# =======================================================

load_dotenv()

logger = logging.getLogger(__name__)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment.")

# =======================================================
# Retry Configuration
# =======================================================

MAX_MODEL_RETRIES = 5
DEFAULT_BACKOFF = 2  # Seconds

# =======================================================
# Gemini LLM Wrapper
# =======================================================


class GeminiLLM(LLM):
    """
    Shared Gemini client used across all AI agents.

    Features
    --------
    - Uses Gemini Chat API (avoids direct Models.generate_content usage).
    - Primary model + multiple fallback models.
    - Automatic retry for temporary Gemini failures.
    - Handles 429 quota errors using Gemini RetryInfo delay.
    - Handles 503 unavailable errors with exponential backoff.
    """

    def __init__(self):
        self.client = genai.Client(api_key=api_key)

        # -------------------------------------------------------
        # Model Configuration
        # -------------------------------------------------------

        # Primary model (fast + low token usage)
        self.primary_model = "gemini-3.7-flash"

        # Fallback models (tried in order)
        self.fallback_models = [
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
        ]

        logger.info(
            f"Primary Gemini model: {self.primary_model} | "
            f"Fallback models: {', '.join(self.fallback_models)}"
        )

    # =======================================================
    # Internal Chat API Call
    # =======================================================

    def _chat_generate(self, model: str, prompt: str) -> str:
        """
        Sends a prompt using Gemini Chat API.
        """

        chat = self.client.chats.create(model=model)

        response = chat.send_message(prompt)

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()

    # =======================================================
    # Retry Wrapper
    # =======================================================

    def _generate_with_retry(self, model: str, prompt: str) -> str:
        """
        Retry Gemini request on temporary failures.
        """

        last_error = None

        for attempt in range(1, MAX_MODEL_RETRIES + 1):

            try:
                logger.info(
                    f"Using Gemini model: {model} "
                    f"(Attempt {attempt}/{MAX_MODEL_RETRIES})"
                )

                return self._chat_generate(model=model, prompt=prompt)

            except Exception as e:

                last_error = e
                error_text = str(e)

                retryable = any(
                    keyword in error_text
                    for keyword in [
                        "429",
                        "RESOURCE_EXHAUSTED",
                        "503",
                        "UNAVAILABLE",
                        "500",
                        "INTERNAL",
                    ]
                )

                # Non-retryable errors
                if not retryable:
                    logger.error(f"Non-retryable Gemini error ({model}): {e}")
                    raise

                # Gemini sometimes tells us exactly how long to wait.
                retry_match = re.search(
                    r"retry in ([0-9.]+)s",
                    error_text,
                    re.IGNORECASE,
                )

                if retry_match:
                    wait_time = float(retry_match.group(1))
                else:
                    wait_time = DEFAULT_BACKOFF * (2 ** (attempt - 1))

                if attempt < MAX_MODEL_RETRIES:

                    logger.warning(
                        f"{model} unavailable "
                        f"(Attempt {attempt}/{MAX_MODEL_RETRIES}). "
                        f"Retrying in {wait_time:.1f}s..."
                    )

                    time.sleep(wait_time)

                else:

                    logger.error(
                        f"{model} failed after "
                        f"{MAX_MODEL_RETRIES} attempts."
                    )

        raise last_error

    # =======================================================
    # Public Generate Method
    # =======================================================

    def generate(self, prompt: str) -> str:
        """
        Generate text using the primary model and fallback models.

        Order:
            1. Gemini 3.1 Flash Lite
            2. Gemini 3.5 Flash
            3. Gemini 3.7 Flash
        """

        models = [self.primary_model] + self.fallback_models

        last_error = None

        for model in models:

            try:
                return self._generate_with_retry(model, prompt)

            except Exception as e:

                last_error = e

                logger.warning(
                    f"Model {model} failed. Trying next fallback model..."
                )

        # ---------------------------------------------------
        # All models failed
        # ---------------------------------------------------

        error_text = str(last_error)

        if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
            raise RuntimeError(
                "Gemini free-tier quota exceeded. Please retry after a few seconds."
            ) from last_error

        if "503" in error_text or "UNAVAILABLE" in error_text:
            raise RuntimeError(
                "Gemini service is temporarily unavailable. Please retry in a few minutes."
            ) from last_error

        raise RuntimeError(
            "Gemini request failed after all retry attempts."
        ) from last_error
