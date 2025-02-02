import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow CORS from all origins (you can restrict to specific origins later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configure the API key
def configure_genai(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# Wrapper function to interact with the Gemini API
def generate_gemini_response(model, prompt: str, max_retries: int = 3):
    """
    A wrapper function to generate a response from the Gemini API.

    Args:
        model: The Gemini model instance.
        prompt (str): The prompt to send to the model.
        max_retries (int): Maximum number of retries if the API call fails.

    Returns:
        str: The generated response text.

    Raises:
        HTTPException: If the API call fails after max_retries.
    """
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to generate response. Error: {e}")
            if attempt == max_retries - 1:
                raise HTTPException(status_code=500, detail="Failed to generate response from Gemini API.")

# Function to generate subclaims
def generate_subclaims(model, claim: str):
    prompt = f"""
    You are an AI that extracts explicit subclaims from a given claim. Given the following claim:

    Claim: "{claim}"

    Break down the claim into distinct subclaims, ensuring that each subclaim is a direct, structured statement that preserves the wording and logical meaning of the original claim.
    If claim is not in correct format or user input garbage text then return "Please Provide proper claim For verification" else

    Subclaims:
    1.
    2.
    3.
    """
    return generate_gemini_response(model, prompt)

# Function to verify and fix subclaims
def verify_and_fix_subclaims(model, claim: str, subclaims: str):
    prompt = f"""
    You are an AI that verifies and corrects extracted subclaims for logical consistency. Given the original claim and its extracted subclaims, check if the subclaims are correct and make necessary corrections if any errors exist.

    Claim: "{claim}"

    Extracted Subclaims:
    {subclaims}

    If any subclaims contain incorrect information, rephrase them correctly while keeping them logically aligned with the original claim. If the subclaims are correct, return them as they are.

    Verified and Corrected Subclaims:
    1.
    2.
    3.
    """
    return generate_gemini_response(model, prompt)

# Pydantic model for request validation
class ClaimRequest(BaseModel):
    claim: str

# Initialize the model
API_KEY = "AIzaSyAj8P8tfNWx385yVJk4y4dxvlzwWZzEIqA"  # Replace with your actual API key
model = configure_genai(API_KEY)

# API endpoint to generate subclaims and verify them
@app.post("/generate_subclaims")
async def generate_subclaims_endpoint(request: ClaimRequest):
    claim = request.claim
    
    try:
        # Generate subclaims
        subclaims = generate_subclaims(model, claim)
        
        # Verify and fix subclaims
        verified_subclaims = verify_and_fix_subclaims(model, claim, subclaims)
        
        # Return the verified subclaims as JSON
        return JSONResponse(content={"verified_subclaims": verified_subclaims})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)