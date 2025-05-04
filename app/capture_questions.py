import os
import json
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

def capture_results(question, dataset_url, entities, sparql_query, query_result):

    """
    Captures and appends a new question to a dataset file based on the dataset URL.

    Args:
        question (str): The natural language question.
        dataset_url (str): The dataset identifier URL (e.g., "https://text2sparql.aksw.org/2025/dbpedia/").
    """
    # Map dataset URL to a local dataset file
    dataset_name = urlparse(dataset_url).path.strip("/").split("/")[-1]  # e.g., 'dbpedia' from URL
    output_dir = os.getenv("CAPTURE_PATH")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{dataset_name}_captured.json")
    print(f"➡Output file: {output_file}")
    # Initialize file if it doesn't exist
    if not os.path.exists(output_file):
        data = {"questions": []}
    else:
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"questions": []}

    # Determine next ID
    next_id = str(len(data["questions"]) + 1)

    new_entry = {
        "id": next_id,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "dataset_url": dataset_url,
        "extracted_entities": entities,
        "generated_sparql_query": sparql_query,
        "query_result": query_result  
    }

    data["questions"].append(new_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Captured question '{question}' into {output_file} (ID {next_id})")
