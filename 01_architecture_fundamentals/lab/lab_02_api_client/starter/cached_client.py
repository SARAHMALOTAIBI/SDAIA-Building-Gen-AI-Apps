"""
Lab 2 — Step 5: Cached Client

Extends HuggingFaceClient with local caching to minimize API calls.
Essential for development on free tier.

The cache directory setup and key generation are complete.
Complete the three TODOs in the query() method.
"""

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Import the client you built in Step 3-4
from hf_client import HuggingFaceClient, get_api_token


class CachedHFClient(HuggingFaceClient):
    """
    Extends HuggingFaceClient with local caching to minimize API calls.
    """

    def __init__(self, token: str, cache_dir: str = ".cache/hf_responses"):
        super().__init__(token)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, model_id: str, payload: dict) -> str:
        """Generate a unique cache key from the request."""
        content = json.dumps({"model": model_id, "payload": payload}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def query(self, model_id: str, payload: dict, use_cache: bool = True) -> dict:
        """Query with optional local caching."""
        cache_key = self._cache_key(model_id, payload)
        cache_file = self.cache_dir / f"{cache_key}.json"


        # =================================================================
        # TODO 1: Check cache — return cached response if available
        #
        # If use_cache is True AND cache_file.exists():
        #   - Print "[Cache HIT] Using cached response"
        #   - Read the file: cache_file.read_text(encoding="utf-8")
        #   - Parse JSON and return it
        # =================================================================

        # Your code here (cache check)
        if use_cache and cache_file.exists():
            print("[Cache HIT] Using cached response")
            cached_response = cache_file.read_text(encoding="utf-8")
            return json.loads(cached_response)

        # =================================================================
        # TODO 2: Make the API call (cache miss)
        #
        # - Print "[Cache MISS] Calling API..."
        # - Call the parent's query method: super().query(model_id, payload)
        # - Store the result in a variable
        # =================================================================

        # Your code here (API call)
        print("[Cache MISS] Calling API...")
        result = super().query(model_id, payload) # Replace with: super().query(model_id, payload)

        # =================================================================
        # TODO 3: Write result to cache
        #
        # - Convert result to JSON string: json.dumps(result, ensure_ascii=False)
        # - Write to cache_file: cache_file.write_text(..., encoding="utf-8")
        # =================================================================

        # Your code here (cache write)
        cache_content = json.dumps(result, ensure_ascii=False)
        cache_file.write_text(cache_content, encoding="utf-8")

        return result


# --- Main: demonstrate cache behavior ---
if __name__ == "__main__":
    client = CachedHFClient(token=get_api_token())

    prompt_payload = {
        "messages": [
            {"role": "user", "content": "What is retrieval-augmented generation?"}
        ],
        "max_tokens": 100,
        "temperature": 0.3,
    }

    print("--- First call (should be Cache MISS) ---")
    result1 = client.query("mistralai/mistral-7b-instruct", prompt_payload)
    if result1:
        print(result1["choices"][0]["message"]["content"][:200])

    print("\n--- Second call (should be Cache HIT) ---")
    result2 = client.query("mistralai/mistral-7b-instruct", prompt_payload)
    if result2:
        print(result2["choices"][0]["message"]["content"][:200])