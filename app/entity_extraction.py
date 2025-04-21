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

  
def get_entities(entity_names, local_graph_location, lang="en"):
    """
    Queries a local RDF graph to resolve entity names to URIs.

    Args:
        entity_names (list): List of entity names to resolve.
        local_graph_location (str): Path to folder containing RDF files.
        lang (str): Language tag for labels (default: 'en').

    Returns:
        dict: Mapping from entity name to resolved URI.
    """

    resolved_entities = {}
    lang_tag = f"@{lang}"  # Dynamic language tag
    predicate = "rdfs:label"  # Standard RDF label

    print(f"[INFO] Querying local RDF graph at {local_graph_location}")
    print(f"[INFO] Resolving entities: {entity_names}")

    for entity_name in entity_names:
        sparql_query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?entity WHERE {{
            ?entity {predicate} "{entity_name}"{lang_tag} .
        }}
        LIMIT 1
        """

        print(f"[DEBUG] Running SPARQL for entity: '{entity_name}'")

        try:
            results = Utils.query_local_graph(local_graph_location, sparql_query)
            if results:
                resolved_entities[entity_name] = results[0]  # pick first match
                print(f"[INFO] Resolved '{entity_name}' -> {results[0]}")
            else:
                print(f"[WARNING] No entity found for '{entity_name}'")
        except Exception as e:
            print(f"[ERROR] Failed query for '{entity_name}': {e}")

    return resolved_entities

    
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
    local_graph_location = config["DBPEDIA_GRAPH_LOCATION"]

    # Extract entities using LLM
    llm_extracted_entities = extract_entities_with_llm(question, api_key, model, llm_provider, system_prompt_path, max_tokens, temperature)

    # Query dataset to get entity IDs for all extracted names
    dataset_entities_resolved = get_entities(llm_extracted_entities, local_graph_location)
    
    return dataset_entities_resolved
