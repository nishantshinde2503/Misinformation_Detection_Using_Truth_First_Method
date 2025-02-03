import google.generativeai as genai
import json
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access API keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
JINA_API_KEY = os.getenv("JINA_API_KEY")

# Configure Gemini model
def configure_genai(api_key):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# Generate response from Gemini model
def generate_gemini_response(model, prompt):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()  # Return the clean response
    except Exception as e:
        return f"Error generating response: {str(e)}"  # Enhanced error message

# Generate subclaims from the main claim
def generate_subclaims(model, claim):
    prompt = f"""
    Extract explicit subclaims from the claim:
    Claim: "{claim}"
    Subclaims:
    1.
    2.
    3.
    """
    response = generate_gemini_response(model, prompt)
    return response.split("\n")  # Return the subclaims as a list of strings

# Fetch related questions from SerpAPI
def fetch_serpapi_results(query):
    url = f"https://serpapi.com/search?q={query}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract URLs and Titles from the search results
        sources = []
        for result in data.get('related_questions', []):
            question = result.get('question', 'No question available')
            snippet = result.get('snippet', 'No snippet available')
            title = result.get('title', 'No title available')
            sources.append(f"{question}: {snippet}: {title}")
        return sources  # Return list of sources (titles with URLs)
    else:
        return {"error": "Failed to fetch results from SerpAPI"} # Error message if failed


# Fetch response from Jina AI
def fetch_jina_response(subclaim):
    url = f"https://g.jina.ai/{subclaim}"
    headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text  # Return the Jina response text
    else:
        return "Error fetching Jina response"  # Error message if failed

# Generate the final result based on multiple inputs
def generate_final_result(model, main_claim, subclaims, jina_response, serpapi_sources):
    prompt = f"""
    Main Claim: {main_claim}
    Subclaims: {', '.join(subclaims)}
    Jina Response: {jina_response}
    SerpAPI Sources: {', '.join(serpapi_sources)}
    Generate a final response based on this information.
    Keep the response short focus only on main , whether it is true or false and then the reason and the supporting references and sources.
    """
    return generate_gemini_response(model, prompt)

# Sample claim for testing
claim = "Climate change is real and its impacts are visible across the globe."

# Main processing function
def process_claim(claim):
    try:
        # Configure Gemini model
        model = configure_genai(GEMINI_API_KEY)
        
        # Generate subclaims, Jina response, and SerpAPI results
        subclaims = generate_subclaims(model, claim)
        print("Subclaims:", subclaims)
        
        jina_response = fetch_jina_response(claim)
        print("Jina Response:", jina_response)
        
        serpapi_sources = fetch_serpapi_results(claim)
        print("SerpAPI Sources:", serpapi_sources)
        
        # Generate the final result
        final_result = generate_final_result(model, claim, subclaims, jina_response, serpapi_sources)
        print("Final Result:", final_result)
        
    except Exception as e:
        print(f"Error processing the claim: {str(e)}")

# Call the function with a sample claim
process_claim(claim)
