# T2S-KG-Agent

**T2S-KG-Agent** is a lightweight API service, that receives natural language questions and generates **SPARQL queries** based on entity extraction and shape constraints generation. It supports answering questions over **DBpedia** and a **corporate knowledge graph**.

This software artefact is part of the [TEXT2SPARQL’25](https://text2sparql.aksw.org/) submission from team [AIFB @ KIT](https://www.aifb.kit.edu/index.php).

The service is built with **FastAPI** and runs inside a **Docker container** inside a [DigitalOcean](https://www.digitalocean.com/) Droplet with 2 vCPUs and a 4GB / 80GB Disk.

By the time of evaluation, the API can be called under http://167.172.162.197:8000.

---

## Features

- Translate questions (multi-language support)
- Entity extraction using an LLM (currently using OpenAI GPT-4o)
- Shape generation (ShEx) for guiding SPARQL query construction (using [shexer](https://github.com/weso/shexer) library)
- LLM-based SPARQL query generation with retry logic (set to 9 retries, increasing model temperature for every retry)
- Local graph querying (via rdflib) or remote SPARQL endpoint

---

## Requirements

- Docker installed
- Valid `.env` file with API keys and configurations (example below)

---

## Environment Variables

You must provide a `.env` file. Example:

```env
LLM_API_KEY="" 

CORPORATE_GRAPH_LOCATION="./KGs/corporate_graphs"
DBPEDIA_SPARQL_URL="https://dbpedia.org/sparql"
RETRY_COUNT="3" # Number of retries for the SPARQL query

LLM_MODEL="gpt-4o-mini"

SYSTEM_PROMPT_ENTITY_EXTRACTION="./system_prompts/system_prompt_entity_extraction.txt"
MAX_TOKENS_ENTITY_EXTRACTION="50" # Maximum number of tokens for the SPARQL generation
TEMPERATURE_ENTITY_EXTRACTION="0.2" # Temperature for the SPARQL generation

SYSTEM_PROMPT_SPARQL_GENERATION="./system_prompts/system_prompt_SPARQL_generation.txt"
MAX_TOKENS_SPARQL_GENERATION="512" # Maximum number of tokens for the SPARQL generation
TEMPERATURE_SPARQL_GENERATION="0.1" # Temperature for the SPARQL generation

```

---

## Build the Docker Image

```bash
docker build -t t2s_kg_agent .
```

---

## Run the Docker Container

```bash
docker run -d --name t2s_kg_agent -p 8000:8000 --env-file .env t2s_kg_agent
```

**Important:**  
Make sure your `.env` file is in the same directory where you run the command or provide the absolute path.

---

## Access the API

Once running, access it at:

```bash
http://localhost:8000/
```

Example GET request:

```bash
http://localhost:8000/?dataset=https://text2sparql.aksw.org/2025/dbpedia/&question=Who is the mayor of Berlin?
```

It returns:

```json
{
  "dataset": "https://text2sparql.aksw.org/2025/dbpedia/",
  "question": "Who is the mayor of Berlin?",
  "query": "SELECT ... (SPARQL query here)"
}
```

---

# License

MIT License

---
Build with 🫶