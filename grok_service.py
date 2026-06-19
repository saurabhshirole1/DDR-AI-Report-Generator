# grok_service.py
# ---------------------------------------------------------------------------
# This file handles ALL communication with the Groq API.
# Groq is the service that runs our AI model (llama-3.3-70b-versatile).
#
# How it works:
# 1. We send a prompt (instructions + PDF content) to Groq
# 2. Groq sends back an AI-generated response
# 3. We return that response to the rest of our app
#
# Groq uses the OpenAI API format - so the request structure looks
# exactly like OpenAI requests but goes to Groq's servers.
# ---------------------------------------------------------------------------

import requests    # For making HTTP requests to Groq API
import json        # For working with JSON data

from config import (
    GROQ_API_KEY,    # Our API key
    GROQ_MODEL,      # Model name (llama-3.3-70b-versatile)
    GROQ_API_URL,    # API endpoint URL
    MAX_TOKENS,      # Max length of AI response
    TEMPERATURE,     # How creative the AI should be
    REPORT_SECTIONS  # The sections our report should have
)


def build_ddr_prompt(doc1_text: str, doc2_text: str, 
                     doc1_name: str, doc2_name: str) -> str:
    """
    Builds the prompt (instructions) we send to Groq.
    
    A prompt is like a set of instructions we give to the AI.
    The better our prompt, the better the AI's response.
    
    We tell the AI:
    - What its job is (generate a DDR report)
    - What the two documents contain
    - Exactly what sections the report should have
    - What format to use
    
    Returns:
    - A string containing the full prompt
    """
    
    # We limit text to 3000 characters per document
    # This is because Groq has a token limit (max text it can process)
    # If PDFs are very long, we take the first 3000 chars
    max_chars = 3000
    doc1_preview = doc1_text[:max_chars]
    doc2_preview = doc2_text[:max_chars]
    
    # Build the section list as a numbered string
    # Example: "1. Executive Summary\n2. Document 1 Overview\n..."
    sections_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(REPORT_SECTIONS)])
    
    # This is the full prompt we send to Groq
    # We use triple quotes for multi-line strings
    prompt = f"""You are an expert business analyst specializing in Detailed Diagnostic Report (DDR).

You have been given the content of two documents:

=== DOCUMENT 1: {doc1_name} ===
{doc1_preview}

=== DOCUMENT 2: {doc2_name} ===
{doc2_preview}

Your task is to generate a comprehensive, professional Detailed Diagnostic Report (DDR) based on these two documents.

The report MUST include ALL of the following sections in this exact order:
{sections_text}

FORMAT RULES:
- Use "## Section Name" for main section headers (with ## prefix)
- Use "### Subsection" for subsections
- Use bullet points (- ) for lists
- Use **bold text** for important terms
- Keep language professional, clear, and factual
- Each section must have at least 3-5 detailed sentences or bullet points
- If information is missing or unclear from the documents, state that explicitly
- Do NOT make up facts - only use information from the provided documents

Begin the report now:"""
    
    return prompt


def call_groq_api(prompt: str) -> str:
    """
    Sends our prompt to the Groq API and gets back the AI response.
    
    This is the core function that actually talks to Groq.
    
    How HTTP API calls work:
    1. We prepare our request (headers + data)
    2. We send it to Groq's server using requests.post()
    3. Groq processes it with the AI model
    4. Groq sends back a response
    5. We extract the text from the response
    
    Returns:
    - The AI-generated report text as a string
    """
    
    # Check if API key is set
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")
    
    # Headers tell the API who we are and what format we're sending
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",  # Our API key for authentication
        "Content-Type": "application/json"            # We're sending JSON data
    }
    
    # This is the request body - what we're asking Groq to do
    # It follows the OpenAI chat format
    payload = {
        "model": GROQ_MODEL,          # Which AI model to use
        "messages": [
            {
                "role": "system",      # System message = background instructions for AI
                "content": "You are an expert business analyst who creates professional Detailed Diagnostic Reports. Always be thorough, factual, and structured."
            },
            {
                "role": "user",        # User message = our actual request
                "content": prompt      # The prompt we built with document content
            }
        ],
        "max_tokens": MAX_TOKENS,      # Max length of response
        "temperature": TEMPERATURE     # How creative/focused the AI should be
    }
    
    try:
        # Send POST request to Groq API
        # timeout=120 means wait max 2 minutes for response
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,         # json= automatically converts dict to JSON
            timeout=120
        )
        
        # raise_for_status() throws an error if request failed (4xx or 5xx status)
        response.raise_for_status()
        
        # Parse the JSON response from Groq
        response_data = response.json()
        
        # Extract the AI's message from the response
        # The response structure is: choices[0].message.content
        ai_response = response_data["choices"][0]["message"]["content"]
        
        return ai_response
        
    except requests.exceptions.Timeout:
        # This happens if Groq takes too long to respond
        raise Exception("Request timed out. Groq API took too long to respond. Please try again.")
    
    except requests.exceptions.ConnectionError:
        # This happens if there's no internet connection
        raise Exception("Connection error. Please check your internet connection.")
    
    except requests.exceptions.HTTPError as e:
        # This happens if Groq returns an error (like 401 Unauthorized, 429 Rate limit)
        if response.status_code == 401:
            raise Exception("Invalid API key. Please check your GROQ_API_KEY in .env file.")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please wait a moment and try again.")
        else:
            raise Exception(f"API Error: {str(e)}")
    
    except KeyError:
        # This happens if Groq's response format is unexpected
        raise Exception("Unexpected response format from Groq API.")
    
    except Exception as e:
        # Catch-all for any other errors
        raise Exception(f"Error calling Groq API: {str(e)}")


def generate_ddr_report(doc1_data: dict, doc2_data: dict) -> str:
    """
    Main function to generate the complete DDR report.
    
    This is what we call from app.py.
    It combines everything:
    1. Build the prompt with document content
    2. Call Groq API
    3. Return the generated report
    
    Parameters:
    - doc1_data: dict with 'text', 'images', 'info' from pdf_parser
    - doc2_data: dict with 'text', 'images', 'info' from pdf_parser
    
    Returns:
    - Complete DDR report as a string
    """
    
    # Get document names for the prompt
    doc1_name = doc1_data["info"]["file_name"]
    doc2_name = doc2_data["info"]["file_name"]
    
    # Get document text
    doc1_text = doc1_data["text"]
    doc2_text = doc2_data["text"]
    
    # Build the prompt
    prompt = build_ddr_prompt(doc1_text, doc2_text, doc1_name, doc2_name)
    
    # Call Groq API and get the report
    report_text = call_groq_api(prompt)
    
    return report_text
