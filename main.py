import google.generativeai as genai
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from urllib.parse import quote  

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

# Fetch related questions from SerpAPI and return plain text output
def fetch_serpapi_results(query):
    # URL encode the query to safely handle special characters and spaces
    encoded_query = quote(query)
    url = f"https://serpapi.com/search?q={encoded_query}&api_key={SERPAPI_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        sources = []
        for result in data.get('related_questions', []):
            question = result.get('question', 'No question available')
            snippet = result.get('snippet', 'No snippet available')
            title = result.get('title', 'No title available')
            sources.append(f"{question}: {snippet}: {title}")
        # Convert the list to plain text by joining each item with a newline character
        plain_text_output = "\n".join(sources)
        return plain_text_output[:200]
    else:
        return "Error: Failed to fetch results from SerpAPI"

# Fetch response from Jina AI

def fetch_jina_response(subclaim):
    encoded_subclaim = quote(subclaim)  # Encode the subclaim for a valid URL
    url = f"https://g.jina.ai/{encoded_subclaim}"
    headers = {"Authorization": f"Bearer {JINA_API_KEY}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            # Attempt to parse JSON if response is structured
            data = response.json()
            # Extract text from the response (modify based on actual response structure)
            return json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
        except json.JSONDecodeError:
            # If response is not JSON, assume it's plain text
            return response.text[:200].strip()
    else:
        return "Error fetching Jina response"

# Generate the final result based on multiple inputs
def generate_final_result(model, main_claim, subclaims, jina_response, serpapi_sources):
    prompt = f"""
    Main Claim: {main_claim}
    Subclaims: {subclaims}
    Jina Response: {jina_response}
    SerpAPI Sources: {serpapi_sources}
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
        subclaims_text = "\n".join(subclaims)  # Convert list to plain text
        
        jina_response = fetch_jina_response(request.claim).strip()  # Ensure plain text
        
        serpapi_sources = fetch_serpapi_results(request.claim)
        serpapi_sources_text = "\n".join(serpapi_sources)  # Convert list to plain text
        
        # Generate the final result
        final_result = generate_final_result(model, request.claim, subclaims_text, jina_response, serpapi_sources_text)
        
        # Return the final result
        return {"final_result": final_result}
    
    except Exception as e:
        # Catch any exceptions and return a generic error message
        raise HTTPException(status_code=500, detail=f"Error processing the claim: {str(e)}")


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")