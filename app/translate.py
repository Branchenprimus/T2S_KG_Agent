import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=".env")

def translate_question(question: str) -> str:
    """
    Always sends question to the LLM. 
    LLM decides whether to keep it or translate it to English.
    """

    if not question:
        raise ValueError("Empty question provided.")

    return _translate_with_llm(question)

def _translate_with_llm(text: str) -> str:
    """
    Sends the text to the LLM with smart prompt engineering.

    Args:
        text (str): The text to process.

    Returns:
        str: English version of the text.
    """
    api_key = os.getenv("LLM_API_KEY")
    client = OpenAI(api_key=api_key)

    try:
        model = "gpt-4o"
        max_tokens = 500
        temperature = 0.0
        user_prompt = (
            "You are a professional translator. "
            "If the question is already in English, simply return it unchanged. "
            "If it is not in English, translate it into English. "
            "Only output the English sentence without any additional explanation.\n\n"
            f"Question:\n{text}"
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a translator for any given language into English."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        translated_text = response.choices[0].message.content.strip()
        print("[INFO] Translation (or no-change) successful.")
        return translated_text

    except Exception as e:
        print(f"[ERROR] LLM translation failed: {e}")
        raise RuntimeError(f"Translation failed: {e}")
