import json
import argparse
import re
import requests
from openai import OpenAI
from utility import Utils

def extract_entities_with_llm(nlq, api_key, model, llm_provider, system_prompt_path, max_tokens, temperature):
    """
    Uses an LLM to extract the most relevant entities from a natural language query.
    Cleans and parses the extracted entity names into a clean list (without quotes).
    """

    # Load prompt template
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Inject question into template
    user_prompt = prompt_template.replace("{nlq}", nlq)

    # resolve provider
    client = OpenAI(api_key=api_key, base_url=Utils.resolve_llm_provider(llm_provider))

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

    print(f"Question: {nlq}")
    print(f"LLM response: {response.choices[0].message.content}")

    # Parse entity names
    raw_response = response.choices[0].message.content.strip()

    # Better parsing: use regular expression to extract text inside quotes if they exist
    entities = re.findall(r'"([^"]+)"', raw_response)

    # If no quotes are found, fallback to simple comma split
    if not entities:
        entities = [e.strip() for e in raw_response.split(",") if e.strip()]

    return entities

  
def get_entities(entity_names, sparql_endpoint_url, lang="en"):
    """
    Queries a Fuseki SPARQL endpoint to resolve entity names to URIs.
    
    Args:
        entity_names (list): List of entity names to resolve.
        sparql_endpoint_url (str): URL of the hosted Fuseki SPARQL endpoint (e.g., http://host:3030/dbpedia/sparql).
        lang (str): Language tag for labels (default: 'en').

    Returns:
        dict: Mapping from entity name to resolved URI.
    """

    entities = {}
    lang_tag = f"@{lang}"  # Dynamic language tag
    predicate = "rdfs:label"  # Standard label in DBpedia-style RDF

    print(f"[INFO] Using Fuseki endpoint at {sparql_endpoint_url}")
    print(f"[INFO] Resolving entities: {entity_names}")

    headers = {"Accept": "application/sparql-results+json", "User-Agent": "EntityResolver/1.0"}

    for entity_name in entity_names:
        sparql_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?entity WHERE {{
            ?entity {predicate} "{entity_name}"{lang_tag} .
        }}
        LIMIT 1
        """

        print(f"[DEBUG] Querying for entity: '{entity_name}'")

        try:
            response = requests.get(
                sparql_endpoint_url,
                params={"query": sparql_query, "format": "json"},
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] Failed request for '{entity_name}': {e}")
            continue

        try:
            bindings = response.json().get("results", {}).get("bindings", [])
            if bindings:
                entity_uri = bindings[0]["entity"]["value"]
                entities[entity_name] = entity_uri
                print(f"[INFO] Resolved '{entity_name}' -> {entity_uri}")
            else:
                print(f"[WARNING] No entity found for '{entity_name}'")
        except Exception as e:
            print(f"[ERROR] JSON parse error for '{entity_name}': {e}")

    return entities

    
def extract_entities(question, dataset):
    """
    Extracts entities from the given question using an LLM and resolves them against a SPARQL endpoint.
    
    Args:
        question (str): The natural language question.
        dataset (str): The dataset URL for entity resolution.
    
    Returns:
        list: A list of resolved entities.
    """
    # Load configuration
    config = load_config()
    api_key = config["LLM_API_KEY"]
    model = config["LLM_MODEL"]
    llm_provider = config["LLM_PROVIDER"]
    system_prompt_path = config["SYSTEM_PROMPT_PATH"]
    max_tokens = config["MAX_TOKENS"]
    temperature = config["TEMPERATURE"]
    sparql_endpoint_url = config["SPARQL_ENDPOINT_URL"]

    # Extract entities using LLM
    llm_extracted_entities = extract_entities_with_llm(question, api_key, model, llm_provider, system_prompt_path, max_tokens, temperature)

    # Query dataset to get entity IDs for all extracted names
    dataset_entities_resolved = get_entities(llm_extracted_entities, sparql_endpoint_url)
    
    return dataset_entities_resolved
