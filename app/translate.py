import os
import openai
from typing import Dict
from utils import Utils  # Adjust import if needed

# Set your OpenAI API key
openai.api_key = os.getenv("LLM_API_KEY")

def translate_question(question: Dict[str, str], llm_provider: str = "openai") -> str:
    """
    Translates a question dictionary to English if necessary.

    Args:
        question (dict): A dictionary with language codes ('en', 'de', etc.) as keys and question texts as values.
        llm_provider (str): The LLM provider to use ('openai' by default).

    Returns:
        str: The question in English.
    """

    if not question:
        raise ValueError("Empty question dictionary provided.")

    # If English version already exists
    if "en" in question:
        return question["en"]

    # Otherwise, pick the first available language
    lang, text = next(iter(question.items()))

    print(f"[INFO] Detected non-English question ({lang}), translating to English.")

    model_name = Utils.resolve_llm_provider(llm_provider)

    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Translate the following question to English."},
                {"role": "user", "content": text}
            ],
            temperature=0.0  # Deterministic output
        )
        translated_text = response["choices"][0]["message"]["content"].strip()
        print(f"[INFO] Translation completed.")
        return translated_text

    except Exception as e:
        print(f"[ERROR] Failed to translate question: {e}")
        raise RuntimeError(f"Translation failed: {e}")
