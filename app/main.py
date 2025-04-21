from fastapi import FastAPI, HTTPException
from app.entity_extraction import extract_entities
from app.shape_generation import generate_shape
from app.llm_query_generator import generate_sparql_query
from app.models.response_models import SPARQLResponse
from app.translate import translate_question

# Known datasets for validation
KNOWN_DATASETS = [
    "https://text2sparql.aksw.org/2025/dbpedia/",
    "https://text2sparql.aksw.org/2025/corporate/"
]

app = FastAPI(
    title="TEXT2SPARQL Challenge API",
    description="API for translating NLQ to SPARQL for the TEXT2SPARQL'25 competition",
    version="0.1.0",
)

@app.get("/", response_model=SPARQLResponse)
async def get_answer(question: str, dataset: str):
    if dataset not in KNOWN_DATASETS:
        raise HTTPException(status_code=404, detail="Unknown dataset")

    question = translate_question(question)

    entities = None
    if dataset != "https://text2sparql.aksw.org/2025/corporate/":
        entities = extract_entities(question, dataset)

    # Step 2: Shape Generation
    shape = generate_shape(entities, dataset)

    # Step 3: LLM SPARQL Query Generation
    sparql_query = generate_sparql_query(question, shape, dataset)

    return SPARQLResponse(
        dataset=dataset,
        question=question,
        query=sparql_query
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
