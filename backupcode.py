import google.generativeai as genai

# Configure the API key
def configure_genai(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

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
    response = model.generate_content(prompt)
    return response.text

# Function to verify and fix errors in subclaims
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
    response = model.generate_content(prompt)
    return response.text

# Main function
def main():
    API_KEY = "AIzaSyAj8P8tfNWx385yVJk4y4dxvlzwWZzEIqA"  # Replace with your actual API key
    model = configure_genai(API_KEY)

    claim = "Pune is in the state of Goa in Europe"
    
    # Generate subclaims
    subclaims = generate_subclaims(model, claim)
    print("Generated Subclaims:\n", subclaims)

    # Verify and fix subclaims if needed
    verified_subclaims = verify_and_fix_subclaims(model, claim, subclaims)
    print("\nVerified and Corrected Subclaims:\n", verified_subclaims)

# Run the main function
if __name__ == "__main__":
    main()
