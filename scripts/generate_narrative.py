import requests
import json
import os
import sys
import dotenv

dotenv.load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
API_ENDPOINT = os.getenv("MODEL_INFERENCE_URL")

def query_origin_narrative(instruction, context, max_tokens=300, temperature=0.3, output_filename=None):
    """
    Sends a structured payload to the OriginZero Gemma-4 API endpoint
    and processes the generated narrative response.
    """
    
    # 1. Structure payload according to your FastAPI InferenceRequest schema
    payload = {
        "instruction": instruction,
        "context": context,
        "max_new_tokens": max_tokens,
        "temperature": temperature
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("⏳ Processing prompt and transmitting vectors to inference gateway...")
    
    try:
        # 2. Transmit the synchronous POST request
        response = requests.post(API_ENDPOINT, json=payload, headers=headers, timeout=120)
        
        # Check if the server returned an error (e.g., 500 Internal Server Error)
        response.raise_for_status()
        
        # 3. Parse JSON returned bytes
        result = response.json()
        narrative_output = result.get("response", "No narrative payload found in response object.")
        
        # 4. Present generated text cleanly on screen
        print("\n" + "="*60)
        print("AI-GENERATED ORIGIN NARRATIVE DETECTED:")
        print("="*60)
        print(narrative_output)
        print("="*60 + "\n")
        
        # 5. Voluntarily commit the output to a local text file
        if output_filename:
            with open(output_filename, "w", encoding="utf-8") as file:
                file.write(f"--- SYSTEM METADATA ---\n")
                file.write(f"Instruction: {instruction}\n")
                file.write(f"Parameters: Temp={temperature}, Tokens={max_tokens}\n")
                file.write(f"-----------------------\n\n")
                file.write(narrative_output)
            print(f"Successfully saved output text log into file: '{output_filename}'")
            
        return narrative_output

    except requests.exceptions.HTTPError as http_err:
        print(f"\nBackend Server returned an HTTP Error Status: {response.status_code}")
        print(f"Details: {response.text}")
    except requests.exceptions.ConnectionError:
        print("\nConnection Error: Failed to reach the server.")
        print(f"Please verify your Cloudflare URL '{API_ENDPOINT}' is active and running.")
    except requests.exceptions.Timeout:
        print("\nTimeout Error: The inference generation exceeded the allowed window.")
    except Exception as err:
        print(f"\nAn unexpected pipeline exception occurred: {err}")
    
    return None

if __name__ == "__main__":
    print("Starting OriginZero Client Generation Framework...")
    
    # Mock Data Input Context (Type 2 Diabetes Example Vector)
    sample_instruction = "Analyze the underlying social, institutional, and root causes linking to 'Type 2 diabetes' using the extracted knowledge graph relationships and source text."
    
    sample_context = (
        "KNOWLEDGE GRAPH CONNECTIONS:\n"
        "Fact #1: 'Type 2 diabetes' features a systemic link to high-impact node 'Low-carbohydrate diet' (Network Weight Score: 0.2451).\n"
        "Fact #2: 'Type 2 diabetes' features a systemic link to high-impact node 'Low-fat diet' (Network Weight Score: 0.1892).\n"
        "Fact #3: 'Type 2 diabetes' features a systemic link to high-impact node 'Weight loss' (Network Weight Score: 0.1143).\n\n"
        "RAW ARTICLE EXTRACT:\n"
        "Type 2 diabetes (T2D), formerly known as adult-onset diabetes, is a form of diabetes mellitus that is "
        "characterized by high blood sugar, insulin resistance, and relative lack of insulin. Common symptoms include "
        "increased thirst, frequent urination, fatigue and unexplained weight loss."
    )
    
    # Trigger request pipeline
    query_origin_narrative(
        instruction=sample_instruction,
        context=sample_context,
        max_tokens=256,
        temperature=0.3,
        output_filename="diabetes_origin_narrative.txt"
    )