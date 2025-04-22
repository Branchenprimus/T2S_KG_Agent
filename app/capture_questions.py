import os
import json
from urllib.parse import urlparse

def capture_questions(question, dataset_url):
    """
    Captures and appends a new question to a dataset file based on the dataset URL.

    Args:
        question (str): The natural language question.
        dataset_url (str): The dataset identifier URL (e.g., "https://text2sparql.aksw.org/2025/dbpedia/").
    """
    # Map dataset URL to a local dataset file
    dataset_name = urlparse(dataset_url).path.strip("/").split("/")[-1]  # e.g., 'dbpedia' from URL
    output_dir = "/root/T2S_KG_Agent/captured_questions"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{dataset_name}_captured.json")

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
        "question": [
            {
                "language": "en",
                "string": question
            }
        ],
        "query": {
            "sparql": ""
        },
        "answers": []
    }

    data["questions"].append(new_entry)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Captured question '{question}' into {output_file} (ID {next_id})")
