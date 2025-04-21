def generate_sparql_query(prompt):
    """
    Function to generate a query based on the given prompt.
    Currently, it only prints the prompt.
    
    Args:
        prompt (str): The input prompt for generating the query.
    
    Returns:
        str: A message indicating the query generation.
    """
    print(f"Generating query for prompt: {prompt}")
    return f"Query generated for prompt: {prompt}"

if __name__ == "__main__":
    # Example usage
    example_prompt = "What is the capital of France?"
    result = generate_sparql_query(example_prompt)
    print(result)