import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = "llama-3.3-70b-versatile"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

MAX_TOKENS = 4096

TEMPERATURE = 0.3

MAX_FILE_SIZE_MB = 10

MAX_PAGES = 50

# REPORT SETTINGS

REPORT_TITLE = "Detailed Diagnostic Report (DDR)"

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
