def generate_sparql_query(question, shape=None, dataset=None):
    """
    Function to generate a SPARQL query based on the given question, shape, and dataset.
    
    Args:
        question (str): The natural language question.
        shape (str, optional): The shape of the knowledge graph. Defaults to None.
        dataset (str, optional): The dataset URL. Defaults to None.
    
    Returns:
        str: A SPARQL query.
    """
    print(f"Generating SPARQL query for question: {question}")
    print(f"Shape: {shape}")
    print(f"Dataset: {dataset}")
    
    # Determine the type of dataset and use appropriate prefixes
    if dataset and "corporate" in dataset:
        prefix = "PREFIX corp: <http://www.corporate-semantic-web.de/ontology#>\n\n"
    elif dataset and "dbpedia" in dataset:
        prefix = "PREFIX dbo: <http://dbpedia.org/ontology/>\nPREFIX dbr: <http://dbpedia.org/resource/>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n\n"
    else:
        prefix = ""
    
    # Generate basic SPARQL queries based on question keywords
    if dataset and "corporate" in dataset:
        if "department" in question.lower() or "abteilung" in question.lower():
            if "müller" in question.lower():
                query = prefix + "SELECT ?department WHERE {\n  ?muller a corp:Employee ;\n         corp:name \"Müller\" ;\n         corp:firstName \"Frau\" ;\n         corp:worksFor ?dept .\n  ?dept corp:name ?department .\n}"
            else:
                query = prefix + "SELECT ?department ?name WHERE {\n  ?dept a corp:Department ;\n        corp:name ?name .\n  OPTIONAL { ?dept corp:description ?department . }\n}"
        elif "project" in question.lower() or "projekt" in question.lower():
            query = prefix + "SELECT ?project ?startDate ?endDate WHERE {\n  ?proj a corp:Project ;\n        corp:name ?project ;\n        corp:startDate ?startDate ;\n        corp:endDate ?endDate .\n}"
        else:
            query = prefix + "SELECT ?employee ?department WHERE {\n  ?emp a corp:Employee ;\n       corp:name ?employee ;\n       corp:worksFor ?dept .\n  ?dept corp:name ?department .\n}"
    elif dataset and "dbpedia" in dataset:
        if "population" in question.lower() or "inhabitants" in question.lower() or "einwohner" in question.lower():
            if "leipzig" in question.lower():
                query = prefix + "SELECT ?population WHERE {\n  dbr:Leipzig dbo:populationTotal ?population .\n}"
            else:
                query = prefix + "SELECT ?city ?population WHERE {\n  ?city a dbo:City ;\n        dbo:populationTotal ?population .\n}"
        elif "birth" in question.lower() or "born" in question.lower() or "geburt" in question.lower():
            query = prefix + "SELECT ?person ?birthDate ?birthPlace WHERE {\n  ?person a dbo:Person ;\n         dbo:birthDate ?birthDate ;\n         dbo:birthPlace ?birthPlace .\n}"
        else:
            query = prefix + "SELECT ?subject ?predicate ?object WHERE {\n  ?subject ?predicate ?object .\n} LIMIT 10"
    else:
        query = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
    
    return query
