import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")


def extract_json_block(text: str) -> str:
    """
    Extract the first JSON block from the text using regex.
    """
    # Remove ◁think▷ and similar artifacts
    cleaned = re.sub(r"◁.*?▷", "", text, flags=re.DOTALL)

    # Prefer code block with `json`
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", cleaned, flags=re.DOTALL)
    if not match:
        match = re.search(r"({.*})", cleaned, flags=re.DOTALL)

    return match.group(1).strip() if match else None


def parse_user_input(user_input: str) -> dict:
    if not api_key:
        print("❌ API key not found. Make sure OPENROUTER_API_KEY is set.")
        return None

    prompt = f"""
You are a smart scheduling assistant.

Extract a JSON object with:
- "title": short name for the event
- "datetime": in ISO 8601 format (e.g., "2025-06-20T15:00:00")
- "attendees": list of names or emails

User: "{user_input}"

Respond ONLY with valid JSON. No markdown, no explanations, no ◁think▷.
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "moonshotai/kimi-dev-72b:free",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=60,
        )
        response.raise_for_status()

        content = response.json()["choices"][0]["message"]["content"]
        print("📤 Prompt Sent:\n", prompt)
        print("📥 Raw LLM Response:\n", content)

        json_str = extract_json_block(content)
        if not json_str:
            print("⚠️ No valid JSON block found.")
            return None

        return json.loads(json_str)

    except Exception as e:
        print("❌ Error during OpenRouter call or JSON parsing:", e)
        return None
