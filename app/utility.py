import os
import logging
import requests
from rdflib import Graph

class Utils:
    @staticmethod
    def resolve_llm_provider(llm_provider: str) -> str:
        """Resolves the LLM provider to a specific string."""
        if llm_provider == "openai":
            return None
        elif llm_provider == "deepseek":
            return "https://api.deepseek.com/v1"
        elif llm_provider == "alibaba":
            return "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        elif llm_provider == "anthropic":
            return "https://api.anthropic.com/v1/"
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
    
    @staticmethod
    def str_to_bool(value: str) -> bool:
        """Convert a string to a boolean."""
        return value.lower() in ('true', '1', 'yes')
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """Reads content from a file and returns it as a string."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"WARNING: Could not read file {file_path}: {e}")
            return ""

    @staticmethod
    def query_sparql_endpoint(sparql_query: str, endpoint_url: str) -> list:
        """
        Executes a SPARQL query against a remote endpoint and returns the result values.

        Args:
            sparql_query: The SPARQL query string.
            endpoint_url: The URL of the SPARQL endpoint.

        Returns:
            A list of result values (as strings), or a dictionary with {"error": "..."}.
        """
        headers = {
            "User-Agent": "SPARQLQueryBot/1.0 (contact: example@example.com)"
        }
        data = {
            "query": sparql_query,
            "format": "json"
        }

        try:
            response = requests.get(endpoint_url, headers=headers, params=data)
            response.raise_for_status()
            json_response = response.json()

            vars_ = json_response.get("head", {}).get("vars", [])
            bindings = json_response.get("results", {}).get("bindings", [])

            return [
                binding[var]["value"]
                for var in vars_
                for binding in bindings
                if var in binding and "value" in binding[var]
            ]

        except requests.exceptions.RequestException as e:
            return {"error": str(e)} 

    @staticmethod
    def guess_rdf_format(file_path: str) -> str:
        """Guesses RDF serialization format based on file extension."""
        if file_path.endswith(".ttl"):
            return "turtle"
        elif file_path.endswith(".nt"):
            return "nt"
        elif file_path.endswith(".rdf") or file_path.endswith(".xml"):
            return "xml"
        else:
            return "turtle"  # default fallback
        
    @staticmethod
    def is_faulty_result(result):
        if isinstance(result, dict) and "error" in result:
            return True
        if not result:
            return True
        if all(str(r).strip() == "0" for r in result):
            return True
        return False
    
    @staticmethod
    def query_local_graph(local_graph_location: str, sparql_query: str) -> list:
        """
        Loads RDF triples from a local folder into an rdflib Graph and executes a SPARQL query.

        Args:
            local_graph_location (str): Path to folder containing .ttl, .rdf, or .nt files.
            sparql_query (str): SPARQL query string to execute.

        Returns:
            list: List of stringified query results (flattened).
        """
        g = Graph()

        if not os.path.isdir(local_graph_location):
            print(f"[ERROR] Provided path is not a directory: {local_graph_location}")
            return []

        rdf_extensions = (".ttl", ".rdf", ".nt")
        files = [f for f in os.listdir(local_graph_location) if f.endswith(rdf_extensions)]

        if not files:
            print(f"[WARNING] No RDF files found in {local_graph_location}")
            return []

        for fname in files:
            fpath = os.path.join(local_graph_location, fname)
            fmt = (
                "ttl" if fname.endswith(".ttl")
                else "nt" if fname.endswith(".nt")
                else "xml"
            )
            try:
                print(f"[INFO] Loading {fname} as format {fmt}")
                g.parse(fpath, format=fmt)
            except Exception as e:
                print(f"[ERROR] Failed to parse {fname}: {e}")

        if len(g) == 0:
            print(f"[WARNING] No triples loaded after parsing files in {local_graph_location}")
            return []

        print(f"[INFO] Loaded {len(g)} triples from {local_graph_location}")
        
        try:
            qres = g.query(sparql_query)
            results = [str(val) for row in qres for val in row]
            print(f"[INFO] Query returned {len(results)} result(s)")
            return results
        except Exception as e:
            print(f"[ERROR] Failed to execute SPARQL query: {e}")
            return []
