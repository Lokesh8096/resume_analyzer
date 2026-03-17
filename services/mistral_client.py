from mistralai.client import Mistral
from config.mistral_keys import MISTRAL_KEYS


def get_mistral_client(index: int):
    # Ensure at least one key is present and non-empty
    available_keys = [k for k in MISTRAL_KEYS if k]
    if not available_keys:
        raise ValueError("No Mistral API keys found. Set MISTRAL_KEY_1/2/3 in .env")

    key = available_keys[index % len(available_keys)]
    return Mistral(api_key=key)
