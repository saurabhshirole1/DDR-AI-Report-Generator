# config.py
# ---------------------------------------------------------------------------
# This file holds all the settings for our app in one place.
# Instead of hardcoding values everywhere, we keep them here.
# If we want to change something (like the model), we change it here only.
# ---------------------------------------------------------------------------

import os
from dotenv import load_dotenv

# load_dotenv() reads the .env file and loads the API key into our program
# Without this, os.getenv() won't find our GROQ_API_KEY
load_dotenv()

# ---------------------------------------------------------------------------
# GROQ API SETTINGS
# ---------------------------------------------------------------------------

# This reads GROQ_API_KEY from the .env file
# Example .env file:  GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# The model we are using from Groq
# llama-3.3-70b-versatile is a very powerful free model
GROQ_MODEL = "llama-3.3-70b-versatile"

# Groq API URL - this is where we send our requests
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Max tokens = how long the AI response can be
# 4096 is enough for a full detailed report
MAX_TOKENS = 4096

# Temperature controls creativity of the AI
# 0.3 = more focused and factual (good for reports)
# 1.0 = very creative (good for stories)
TEMPERATURE = 0.3

# ---------------------------------------------------------------------------
# PDF SETTINGS
# ---------------------------------------------------------------------------

# Maximum file size allowed for uploaded PDFs (in MB)
MAX_FILE_SIZE_MB = 10

# Maximum number of pages to extract from each PDF
# We limit this to avoid sending too much text to Groq
MAX_PAGES = 50

# ---------------------------------------------------------------------------
# REPORT SETTINGS
# ---------------------------------------------------------------------------

# Name of the report shown at the top
REPORT_TITLE = "Due Diligence Report (DDR)"

# Company/app name shown in the header
APP_NAME = "DDR Report Generator"

# These are the sections our DDR report will have (in order)
REPORT_SECTIONS = [
    "Executive Summary",
    "Document 1 Overview",
    "Document 2 Overview",
    "Key Findings",
    "Comparative Analysis",
    "Risk Assessment",
    "Recommendations",
    "Conclusion"
]
