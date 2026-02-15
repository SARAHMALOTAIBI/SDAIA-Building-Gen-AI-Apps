"""
Lab 2 — Steps 1 & 2: Environment Setup + First API Call

Step 1: Read through the get_api_token() function — understand why we
        never hardcode tokens.
Step 2: Complete the TODO at the bottom to make your first API call.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
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
        raise ValueError(
            "Invalid OpenRouter key format. Should start with 'sk-'."
        )
    return token


# --- Configuration ---
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_ID = "mistralai/mistral-7b-instruct"


TOKEN = get_api_token()

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


# =====================================================================
# TODO (Step 2): Make your first API call
#
# Use requests.post() to send a request to the API.
#
# Hints:
#   - URL: API_URL
#   - Pass `headers=HEADERS`
#   - Pass a JSON body with model + messages
#   - Key parameters: max_tokens=150, temperature=0.7
#   - Call response.raise_for_status() to catch HTTP errors
#   - Parse with response.json()
#   - Extract text from result["choices"][0]["message"]["content"]
# =====================================================================

prompt = "Explain what a vector database is in one paragraph:"

response = requests.post(
    API_URL,
    headers=HEADERS,
    json={
        "model": MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    },
    timeout=60
)

response.raise_for_status()

result = response.json()

print("Generated Text:")
print(result["choices"][0]["message"]["content"])
