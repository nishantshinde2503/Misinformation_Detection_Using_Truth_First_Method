import google.generativeai as genai
import json
import requests

# Configure the API key for Gemini securely
def configure_genai(api_key: str):
    if not api_key:
        raise Exception("API key not found")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# Wrapper function to interact with the Gemini API
def generate_gemini_response(model, prompt: str):
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Error with Gemini response: {e}")

# Function to generate subclaims
def generate_subclaims(model, claim: str):
    prompt = f"""
    You are an AI that extracts explicit subclaims from a given claim. Given the following claim:
    Claim: "{claim}"
    Break down the claim into distinct subclaims, ensuring that each subclaim is a direct, structured statement that preserves the wording and logical meaning of the original claim.
    Subclaims:
    1.
    2.
    3.
    """
    try:
        response = model.generate_content(prompt)
        # Assuming Gemini response text is comma-separated subclaims
        subclaims = response.text.strip().split("\n")
        return [subclaim.strip() for subclaim in subclaims if subclaim.strip()]
    except Exception as e:
        raise Exception(f"Error generating subclaims: {e}")

# Function to generate 1 question per subclaim using Gemini, limiting to top 1
def generate_questions_for_subclaims(model, subclaims):
    questions = []
    for subclaim in subclaims:
        prompt = f"""
        Generate one interview question related to the following subclaim:
        Subclaim: "{subclaim}"
        1. 
        """
        try:
            response = model.generate_content(prompt)
            # Extract the top question
            question_list = response.text.strip().split("\n")[:1]  # Limit to top 1 question
            questions.append(question_list)
        except Exception as e:
            raise Exception(f"Error generating questions: {e}")
    return questions

# Function to interact with SerpAPI for search results
def fetch_serpapi_results(query: str, serpapi_key: str):
    url = f"https://serpapi.com/search?q={query}&api_key={serpapi_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  
    else:
        return {"error": "Error fetching results from SerpAPI"}

# Function to clean and store relevant SerpAPI output
def process_serpapi_results(response):
    related_questions = []

    if "related_questions" in response:
        for item in response["related_questions"]:
            question_data = {
                "question": item.get("question", ""),
                "snippet": item.get("snippet", ""),
                "title": item.get("title", "")
            }
            related_questions.append(question_data)

    return json.dumps(related_questions, indent=2)

# Function to get response from Jina API for a given subclaim
def fetch_jina_response(subclaim: str):
    headers = {
        "Authorization": "Bearer jina_352aaafd36df4b2fa772f9a182482321ONoyLxaA35QmkrCvqcwFPgue8fLO"
    }
    
    # Properly format the URL
    url = f"https://g.jina.ai/{subclaim}"
    
    try:
        # Make the API request
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.text  # Return the response text to be used later
        else:
            return f"Error fetching response for subclaim '{subclaim}': {response.status_code}"
    
    except Exception as e:
        return f"An error occurred while fetching the response: {e}"

# Function to generate final results from Jina and SerpAPI responses
def generate_final_result_from_jina_and_serpapi(jina_response_text, cleaned_results, model, main_claim, subclaims):
    prompt = f"""
    Based on the following information, generate a cohesive answer for the main claim:

    Main Claim:
    {main_claim}

    The following subclaims are references to better understand the main claim:
    Subclaim 1: {subclaims[0]}
    Subclaim 2: {subclaims[1]}  # You can add more subclaims if needed
    Subclaim 3: {subclaims[2]}  # Adjust the number of subclaims based on your data

    Jina Response:
    {jina_response_text}

    Cleaned SerpAPI Results:
    {cleaned_results}

    Based on this information, generate a final answer for the main claim.
    """
    try:
        # Use Gemini model to generate a final response
        final_result = generate_gemini_response(model, prompt)
        return final_result
    except Exception as e:
        raise Exception(f"Error generating final result: {e}")

# Example Usage (same as before)
gemini_key = "AIzaSyAj8P8tfNWx385yVJk4y4dxvlzwWZzEIqA"  # Replace with your actual key
serpapi_key = "dcec1c37a6d7163a4fc766569d65cd6165e651202614add793aec4ebd7b3989d"  # Replace with your actual SerpAPI key
claim_input = "Yesterday there was snowfall in Pune which is located in Goa"

try:
    model = configure_genai(gemini_key)
    
    # Generate subclaims
    subclaims = generate_subclaims(model, claim_input)
    
    # Generate 1 question per subclaim (limited to top 1)
    questions = generate_questions_for_subclaims(model, subclaims)
    
    for question_set in questions:
        for question in question_set:
            # Fetch SerpAPI results and process them
            serpapi_results = fetch_serpapi_results(question, serpapi_key)
            cleaned_results = process_serpapi_results(serpapi_results)

            # Now fetch Jina API response for the main claim (not just the subclaim)
            jina_response = fetch_jina_response(claim_input)  # Capture the response for the main claim

            # Call the final result function with both Jina and SerpAPI responses
            final_result = generate_final_result_from_jina_and_serpapi(
                jina_response_text=jina_response,  # Pass the Jina response for the main claim here
                cleaned_results=cleaned_results,    # Pass the cleaned SerpAPI results here
                model=model,
                main_claim=claim_input,             # Pass the main claim here
                subclaims=subclaims                # Pass the subclaims as references
            )

            # Print the final result generated by Gemini
            print("\nFinal Generated Result for Main Claim:")
            print(final_result)

except Exception as e:
    print(f"An error occurred: {e}")
