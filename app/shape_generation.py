def generate_shape(entities, dataset=None):
    """
    Function to generate a shape based on the extracted entities and dataset.
    
    Args:
        entities: Extracted entities from the question
        dataset (str, optional): The dataset URL. Defaults to None.
    
    Returns:
        str: A knowledge graph shape description.
    """
    print(f"Generating shape for entities: {entities} and dataset: {dataset}")
    
    # Handle the case where entities might be None
    if entities is None or not entities:
        # Return a generic shape for corporate dataset
        if dataset and "corporate" in dataset:
            shape = """
            The knowledge graph has the following structure:
            - Employees have names (corp:name), first names (corp:firstName), and work for departments (corp:worksFor)
            - Departments have names (corp:name) and may have managers (corp:hasManager)
            - Projects have names (corp:name), start and end dates (corp:startDate, corp:endDate), and team members (corp:hasTeamMember)
            - Locations have names (corp:name) and addresses (corp:address)
            """
            return shape
        # Return a generic shape for dbpedia dataset
        elif dataset and "dbpedia" in dataset:
            shape = """
            The knowledge graph has the following structure:
            - Cities have population (dbo:populationTotal), country (dbo:country), and location (dbo:location)
            - Persons have birth date (dbo:birthDate), birth place (dbo:birthPlace), and death date (dbo:deathDate)
            - Countries have capital (dbo:capital), language (dbo:officialLanguage), and population (dbo:populationTotal)
            """
            return shape
        else:
            # Default shape if no dataset information
            return "Generic knowledge graph with entities and relationships."
    
    # For real implementation, we would create a more specific shape based on entities
    return f"Shape generated for: {entities}"
