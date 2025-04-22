from fastapi import FastAPI, HTTPException
from app.entity_extraction import extract_entities
from app.shape_generation import generate_shape
from app.llm_query_generator import generate_sparql_query
from app.capture_questions import capture_questions
from app.translate import translate_question
from app.utility import Utils
import json

# Known datasets for validation
KNOWN_DATASETS = [
    "https://text2sparql.aksw.org/2025/dbpedia/",
    "https://text2sparql.aksw.org/2025/corporate/"
]

# Initialize the FastAPI application
app = FastAPI(
    title="TEXT2SPARQL Challenge API",
    description="API for translating NLQ to SPARQL for the TEXT2SPARQL'25 competition",
    version="0.1.0",
)

@app.get("/")
async def get_answer(question: str, dataset: str):
    if dataset not in KNOWN_DATASETS:
        raise HTTPException(status_code=404, detail="Unknown dataset")

    original_question = question
    capture_questions(original_question, dataset)

    # Translate the original_question to ensure it is in the correct format
    english_question = translate_question(original_question)
    print(f"[INFO] Original question: {original_question}")
    print(f"[INFO] Translated question: {english_question}")
    
    # Extract entities if the dataset is not a local graph
    entities = None
    if not Utils.is_local_graph(dataset):
        entities = extract_entities(english_question)
    print(f"[INFO] Extracted entities: {entities}")
    
    # Generate the ShEx shape based on the entities and dataset
    shape = generate_shape(entities, dataset)
    print(f"[INFO] Generated shape: {shape}")
    
    # Generate the SPARQL query using the english_question, shape, and dataset
    sparql_query = generate_sparql_query(english_question, shape, dataset)
    
    # Return the response with the dataset, question, and generated query
    return {
        "dataset": dataset,
        "question": question,
        "query": sparql_query
    }
    
@app.get("/health")
async def health_check():
    return {"status": "ok"}
