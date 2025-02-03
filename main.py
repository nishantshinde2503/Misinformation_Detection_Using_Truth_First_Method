import google.generativeai as genai
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI()


# CORS middleware to allow frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],
)

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

# Fetch search results from SerpAPI
def fetch_serpapi_results(query):
    url = f"https://serpapi.com/search?q={query}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract URLs and Titles from the search results
        sources = []
        for result in data.get('organic_results', []):
            title = result.get('title', 'No title available')
            url = result.get('link', 'No link available')
            sources.append(f"{title}: {url}")
        return sources  # Return list of sources (titles with URLs)
    else:
        return {"error": "Failed to fetch results from SerpAPI"}  # Error message if failed

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
    """
    return generate_gemini_response(model, prompt)

# Request body model for claim processing
class ClaimRequest(BaseModel):
    claim: str

# Process the claim and generate the result
@app.post("/process-claim")
async def process_claim(request: ClaimRequest):
    try:
        # Configure Gemini model
        model = configure_genai(GEMINI_API_KEY)
        
        # Generate subclaims, Jina response, and SerpAPI results
        subclaims = generate_subclaims(model, request.claim)
        jina_response = fetch_jina_response(request.claim)
        serpapi_sources = fetch_serpapi_results(request.claim)
        
        # Generate the final result
        final_result = generate_final_result(model, request.claim, subclaims, jina_response, serpapi_sources)
        
        # Return the final result
        return {"final_result": final_result}
    
    except Exception as e:
        # Catch any exceptions and return a generic error message
        raise HTTPException(status_code=500, detail=f"Error processing the claim: {str(e)}")

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")