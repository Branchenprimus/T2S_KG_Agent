import os
import openai
from typing import Dict, Union

# Set your OpenAI API key
openai.api_key = os.getenv("LLM_API_KEY")

def translate_question(question: Union[Dict[str, str], str], llm_provider: str = "openai") -> str:
    """
    Translates a question to English if necessary.

    Args:
        question: Either a dictionary with language codes ('en', 'de', etc.) as keys 
                 and question texts as values, or a string containing the question directly.
        llm_provider (str): The LLM provider to use ('openai' by default).

    Returns:
        str: The question in English.
    """
    # If the input is already a string
    if isinstance(question, str):
        # Simple language detection - check for common German words
        german_indicators = ["ist", "der", "die", "das", "in", "welcher", "wieviele", "was", "wie"]
        is_likely_german = any(word in question.lower().split() for word in german_indicators)
        
        if is_likely_german:
            print(f"[INFO] Detected likely German question, translating to English.")
            try:
                from app.utility import Utils
                model_name = Utils.resolve_llm_provider(llm_provider)
                
                response = openai.ChatCompletion.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "Translate the following question to English."},
                        {"role": "user", "content": question}
                    ],
                    temperature=0.0  # Deterministic output
                )
                translated_text = response["choices"][0]["message"]["content"].strip()
                print(f"[INFO] Translation completed.")
                return translated_text
            except Exception as e:
                print(f"[WARNING] Translation failed: {e}. Using original text.")
                return question
        
        # If not likely German or translation failed, return the original text
        return question
    
    # Handle dictionary input as before
    if isinstance(question, dict):
        if not question:
            raise ValueError("Empty question dictionary provided.")

        # If English version already exists
        if "en" in question:
            return question["en"]

        # Otherwise, pick the first available language
        lang, text = next(iter(question.items()))

        print(f"[INFO] Detected non-English question ({lang}), translating to English.")

        try:
            from app.utility import Utils
            model_name = Utils.resolve_llm_provider(llm_provider)
            
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
    
    # Default fallback for unexpected input types
    return str(question)
