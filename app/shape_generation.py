import os
from shexer.shaper import Shaper
from app.utility import Utils
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

def generate_shape_from_local_graph(local_graph_location):
    """
    Loads all RDF files from a folder, generates ShEx shapes using Shexer,
    and annotates shape lines with labels using rdflib.

    Args:
        local_graph_location (str): Path to the folder containing RDF files.

    Returns:
        str: The generated ShEx shape as a string, or None if an error occurs.
    """
    try:
        g = Graph()

        # Load RDF files from the specified folder
        for fname in os.listdir(local_graph_location):
            if fname.endswith((".ttl", ".rdf", ".nt")):
                fpath = os.path.join(local_graph_location, fname)
                fmt = (
                    "ttl" if fname.endswith(".ttl")
                    else "nt" if fname.endswith(".nt")
                    else "xml"
                )
                print(f"📥 Loading {fname} as {fmt}")
                g.parse(fpath, format=fmt)

        # Check if the graph is empty
        if len(g) == 0:
            print(f"⚠️ No RDF triples loaded from {local_graph_location}")
            return None

        # Generate shapes from the combined graph
        shaper = Shaper(
            rdflib_graph=g,
            all_classes_mode=True,
            disable_comments=True
        )

        shape = shaper.shex_graph(string_output=True)
        print(f"✅ Shape generation successful.")
        return shape

    except Exception as e:
        print(f"❌ Error generating shape from local graph: {e}")
        return None


def generate_combined_shape(dbpedia_sparql_url, entity_labels):
    print(f"Entity labels: {entity_labels}")
    shape_lines = []
    
    try:
        for label in entity_labels:
            label_clean = label.replace(' ', '_')
            entity_id = f"http://dbpedia.org/resource/{label_clean}"
            shape_label = f"http://shapes.dbpedia.org/{label_clean}"
            shape_lines.append(f"<{entity_id}>@<{shape_label}>")

        shape_map_raw = "\n".join(shape_lines)
        print(f"Generated shape map:\n{shape_map_raw}")
        
        namespaces_dict = {
            "http://example.org/": "ex",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://xmlns.com/foaf/0.1/": "foaf",
            "http://dbpedia.org/resource/": "dbr",
            "http://dbpedia.org/ontology/": "dbo",
            "http://dbpedia.org/property/": "dbp",
            "http://dbpedia.org/class/yago/": "yago",
            "http://purl.org/dc/terms/": "dcterms",
            "http://www.w3.org/2002/07/owl#": "owl",
            "http://www.w3.org/2007/05/powder-s#": "powders",
            "http://www.w3.org/ns/prov#": "prov",
            "http://umbel.org/umbel/rc/": "umbel",
            "http://schema.org/": "schema",
            "http://shapes.dbpedia.org/": "shapes"
        }

        shaper = Shaper(
            shape_map_raw=shape_map_raw,
            url_endpoint=dbpedia_sparql_url,
            namespaces_dict=namespaces_dict,
            disable_comments=True,
        )
        shape = shaper.shex_graph(string_output=True)
        print(f"✅ Shape generation successful: {shape}")

        return shape
    except Exception as e:
        print(f"Error generating ShEx graph: {e}")
        return None


def generate_shape(entities, dataset):

    load_dotenv(dotenv_path=".env")
    local_graph_location = os.getenv("CORPORATE_GRAPH_LOCATION")
    dbpedia_sparql_url = os.getenv("DBPEDIA_SPARQL_URL")
    
    if Utils.is_local_graph(dataset):
        print(f"✅ Generating shape from local graph at {local_graph_location}")
        return generate_shape_from_local_graph(local_graph_location)
    else:
        print(f"✅ Generating shape using sparql endpoint {dbpedia_sparql_url} and generated shapes.")
        return generate_combined_shape(dbpedia_sparql_url, entities)
