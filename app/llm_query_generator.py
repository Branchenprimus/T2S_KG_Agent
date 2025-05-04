import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.utility import Utils  

# Load environment variables
load_dotenv(dotenv_path=".env")

def generate_sparql_query(question, shape, dataset):
    """
    Generates a SPARQL query from a natural language question and shape description.
    Retries only if the generated query is faulty.
    """

    # Load environment config
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    system_prompt_path_sparql_generation_dbpedia = os.getenv("SYSTEM_PROMPT_SPARQL_GENERATION_DBPEDIA")
    system_prompt_path_sparql_generation_corporate = os.getenv("SYSTEM_PROMPT_SPARQL_GENERATION_CORPORATE")
    max_tokens = int(os.getenv("MAX_TOKENS_SPARQL_GENERATION"))
    temperature = float(os.getenv("TEMPERATURE_SPARQL_GENERATION"))
    retry_count = int(os.getenv("RETRY_COUNT"))

    # Load graph locations
    corporate_graph_path = os.getenv("CORPORATE_GRAPH_LOCATION")
    dbpedia_endpoint = os.getenv("DBPEDIA_SPARQL_URL")

    if not all([api_key, model, system_prompt_path_sparql_generation_dbpedia, system_prompt_path_sparql_generation_corporate, corporate_graph_path, dbpedia_endpoint]):
        raise ValueError("Missing required environment variables.")

    if Utils.is_local_graph(dataset):
        with open(system_prompt_path_sparql_generation_corporate, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
            print(f"[INFO] Using system prompt for local graph: {system_prompt_path_sparql_generation_corporate} ")
    else:
        with open(system_prompt_path_sparql_generation_dbpedia, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
            print(f"[INFO] Using system prompt for DBpedia: {system_prompt_path_sparql_generation_dbpedia} ")

    client = OpenAI(api_key=api_key)

    def build_prompt(previous_attempt=None):
        prompt = f"""{system_prompt}

### User Query:
{question}

### Shape Constraints:
{shape}

### Expected SPARQL Query:
```sparql
"""
        if previous_attempt:
            prompt += f"\n\n### Previous attempt (failed):\n{previous_attempt}\n\n### Please correct the query."
        return prompt

    attempt = 0
    last_response = None
    base_temperature = temperature  # Save initial temperature


    while attempt <= retry_count:
        full_prompt = build_prompt(previous_attempt=last_response)

        # Dynamically increase temperature
        current_temperature = base_temperature + (0.1 * attempt)
        current_temperature = min(current_temperature, 1.0)  # Limit to 1.0 max

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a SPARQL expert. Only output valid SPARQL queries."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens,
                temperature=current_temperature
            )

            raw_response = response.choices[0].message.content.strip()
            sparql_query = raw_response.replace("```sparql", "").replace("```", "").strip()

            # Test query
            if Utils.is_local_graph(dataset):
                query_result = Utils.query_local_graph(corporate_graph_path, sparql_query)
            else:
                query_result = Utils.query_sparql_endpoint(sparql_query, dbpedia_endpoint)

            print(f"\n[ATTEMPT {attempt+1}] Temperature: {current_temperature:.2f}")
            print(f"[INFO] Generated SPARQL query:\n{sparql_query}")
            print(f"[INFO] Query result:\n{query_result}")

            
            if not Utils.is_faulty_result(query_result):
                print(f"✅ Valid SPARQL query generated on attempt {attempt + 1}")
                print(f"✅ Last response: {sparql_query}")
                print(f"✅ Query result: {query_result}")
                return (sparql_query, query_result)

            else:
                print(f"⚠️ Attempt {attempt + 1}: Faulty query result detected.")
                last_response = sparql_query

        except Exception as e:
            print(f"❌ Attempt {attempt + 1}: Error during LLM call: {e}")
            last_response = str(e)

        attempt += 1
        time.sleep(1)


    print(f"[WARNING] Failed to generate a valid SPARQL query after {retry_count} retries. Skipping...")

    fallback_info = (f"# Failed to generate SPARQL query for question: {question}# Attempts: {retry_count}")
    
    print(f"⚠️ Fallback information: {fallback_info}")
    print(f"❌ Last response: {last_response}")

    return (last_response, fallback_info)  



