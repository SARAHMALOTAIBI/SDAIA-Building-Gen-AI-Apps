"""
Lab 2 — Steps 3 & 4: HuggingFaceClient Class + Retry Logic

Step 3: Read the class structure — __init__ and helpers are complete.
Step 4: Complete the three TODOs inside the query() method.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


def get_api_token():
    """Retrieve API token with validation."""
    token = os.getenv("OPENROUTER_API_KEY")
    if not token:
        raise EnvironmentError(
            "OPENROUTER_API_KEY not found. "
            "Create a .env file with your key."
        )
    if not token.startswith("sk-"):
        raise ValueError("Invalid OpenRouter key format.")
    return token


class HuggingFaceClient:
    """
    Production-ready client for the Hugging Face Inference API.
    Handles retries, cold starts, and rate limits.
    """
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    def __init__(self, token: str, max_retries: int = 3, retry_delay: float = 5.0):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def query(self, model_id: str, payload: dict) -> dict:
        """
        Query a model with automatic retry logic.

        Handles:
        - 503: Model loading (cold start) — waits and retries
        - 429: Rate limited — backs off exponentially
        - Timeout — retries with delay
        """

        response = None

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.BASE_URL,
                    headers=self.headers,
                    json={
                        "model": model_id,
                        **payload
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    return response.json()


                # =============================================================
                # TODO 1: Handle 503 — Model is loading (cold start)
                #
                # When status_code == 503, the model is being loaded into memory.
                # - Parse the estimated wait time: response.json().get("estimated_time", 30)
                # - Print a message like: "Model loading... waiting Xs (attempt N)"
                # - Sleep for min(estimated_time, 60) seconds
                # - Continue to the next attempt
                # =============================================================

                # Your code here (503 handling)
                if response.status_code == 503:
                    print(f"Model loading... waiting {self.retry_delay}s (attempt {attempt + 1})")
                    time.sleep(self.retry_delay)
                    continue

                # =============================================================
                # TODO 2: Handle 429 — Rate limited
                #
                # When status_code == 429, you've hit the rate limit.
                # - Calculate wait_time using exponential backoff:
                #   wait_time = self.retry_delay * (2 ** attempt)
                # - Print a message like: "Rate limited. Waiting Xs before retry..."
                # - Sleep for wait_time seconds
                # - Continue to the next attempt
                # =============================================================

                # Your code here (429 handling)
                if response.status_code == 429:
                    wait_time = self.retry_delay * (2 ** attempt)
                    print(f"Rate limited. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue

                response.raise_for_status()

            except requests.exceptions.Timeout:
                # Other errors — raise immediately
                response.raise_for_status()

            except requests.exceptions.Timeout:
                # =============================================================
                # TODO 3: Handle timeout
                #
                # - Print: "Request timed out (attempt N/max_retries)"
                # - If there are more attempts left, sleep for self.retry_delay
                #   and continue
                # - If this was the last attempt, re-raise the exception
                # =============================================================

                # Your code here (timeout handling)
                print(f"Request timed out (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise  # Remove this line once you implement the handler

        raise RuntimeError(
            f"Failed after {self.max_retries} attempts. "
            f"Last status: {response.status_code if response else 'N/A'}, "
            f"Body: {response.text[:200] if response else 'No response received'}"
        )

    # --- Helper methods (complete — no changes needed) ---

    def text_generation(
        self, prompt: str, model: str = "mistralai/mistral-7b-instruct"
    ) -> str:
        """Generate text from a prompt."""
        result = self.query(
            model,
            {
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.7,
            },
        )
        return result["choices"][0]["message"]["content"]

    def summarization(
        self, text: str, model: str = "mistralai/mistral-7b-instruct"
    ) -> str:
        """Summarize a long text into a shorter version."""
        result = self.query(
            model,
            {
                "messages": [
                    {"role": "user", "content": f"Summarize this:\n\n{text}"}
                ],
                "max_tokens": 150,
                "temperature": 0.3,
            },
        )
        return result["choices"][0]["message"]["content"]

    def text_classification(
        self, text: str, model: str = "mistralai/mistral-7b-instruct"
    ) -> str:
        """Classify text sentiment or category."""
        result = self.query(
            model,
            {
                "messages": [
                    {"role": "user", "content": f"Classify the sentiment of this text:\n\n{text}"}
                ],
                "max_tokens": 50,
                "temperature": 0,
            },
        )
        return result["choices"][0]["message"]["content"]




# --- Main: test all three task types ---
if __name__ == "__main__":
    client = HuggingFaceClient(token=get_api_token())

    print("=== Text Generation ===")
    print(client.text_generation("List 3 benefits of using RAG in production systems:"))

    print("\n=== Summarization ===")
    long_text = (
        "Retrieval-Augmented Generation (RAG) is a technique that combines the power of "
        "large language models with external knowledge retrieval. Instead of relying solely "
        "on the model's training data, RAG systems first search a knowledge base for relevant "
        "documents, then use those documents as context for generating responses. This approach "
        "reduces hallucinations, keeps responses grounded in factual data, and allows the system "
        "to access information beyond the model's training cutoff date."
    )
    print(client.summarization(long_text))

    print("\n=== Classification ===")
    print(client.text_classification("This product is amazing and exceeded my expectations!"))