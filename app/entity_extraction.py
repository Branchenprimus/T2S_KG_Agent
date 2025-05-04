import re
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def extract_entities_with_llm(nlq, api_key, model, system_prompt_path, max_tokens, temperature):
    """
    Uses an LLM to extract the most relevant entities from a natural language query.
    Cleans and parses the extracted entity names into a clean Python list of strings.
    
    Args:
        nlq (str): The natural language question.
        api_key (str): OpenAI API key.
        model (str): OpenAI model name (e.g., gpt-4o).
        system_prompt_path (str): Path to the system prompt template.
        max_tokens (int): Maximum tokens for LLM completion.
        temperature (float): LLM creativity setting.

    Returns:
        list[str]: A list of extracted entity names.
    """

    # Load prompt template
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Inject question into template
    user_prompt = prompt_template.replace("{nlq}", nlq)

    # Resolve provider
    api_key = os.getenv("LLM_API_KEY", api_key)  # fallback if not found
    if not api_key:
        raise ValueError("❌ API key missing.")

    client = OpenAI(api_key=api_key)

    # Call LLM
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in extracting named entities from questions."},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )

    print(f"✅ Question: {nlq}")
    print(f"✅ LLM response:\n{response.choices[0].message.content.strip()}")

    # Parse entity names
    raw_response = response.choices[0].message.content.strip()

    # Extract quoted entities first
    entities = re.findall(r'"([^"]+)"', raw_response)

    # If no quotes are found, fallback to comma split
    if not entities:
        entities = [e.strip() for e in raw_response.split(",") if e.strip()]

    # Final cleaning: filter out empty or nonsense entries
    entities = [e for e in entities if len(e) > 0 and not e.isspace()]

    if not isinstance(entities, list):
        raise ValueError("❌ Extraction failed, result is not a list.")

    print(f"✅ Extracted entities: {entities}")
    return entities
    
def extract_entities(question):
    """
    Extracts entities from the given question using an LLM and resolves them against a SPARQL endpoint.
    
    Args:
        question (str): The natural language question.
        dataset (str): The dataset URL for entity resolution.
    
    Returns:
        list: A list of resolved entities.
    """
    
    print(f"[INFO] Extracting entities from question: {question}")
    # Load configuration
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    system_prompt_path = os.getenv("SYSTEM_PROMPT_ENTITY_EXTRACTION")
    max_tokens = int(os.getenv("MAX_TOKENS_ENTITY_EXTRACTION"))
    temperature = float(os.getenv("TEMPERATURE_ENTITY_EXTRACTION"))
    dbpedia_sparql_url = os.getenv("DBPEDIA_SPARQL_URL")

    # Log configuration variables for debugging
    print(f"[DEBUG] Model: {model}")
    print(f"[DEBUG] System Prompt Path entity extraction: {system_prompt_path}")
    print(f"[DEBUG] Max Tokens entity extraction: {max_tokens}")
    print(f"[DEBUG] Temperature entity extraction: {temperature}")
    print(f"[DEBUG] dbpedia_sparql_url: {dbpedia_sparql_url}")
    
    return extract_entities_with_llm(question, api_key, model, system_prompt_path, max_tokens, temperature)
