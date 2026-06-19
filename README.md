# 📋 DDR Report Generator

A **Streamlit web app** that takes two PDF documents, extracts their content using AI, and generates a professional **Detailed Diagnostic Report (DDR)** — downloadable as a PDF.

> Built with: Python · Streamlit · Groq AI · PyMuPDF · ReportLab

---

## 🎯 What It Does

1. **Upload** two PDF documents
2. **Extracts** text and images from both PDFs automatically
3. **Sends** the content to Groq AI (llama-3.3-70b-versatile)
4. **Generates** a structured DDR report with 8 sections
5. **Download** the report as a clean, formatted PDF

---

## 📊 Report Sections

| # | Section |
|---|---|
| 1 | Executive Summary |
| 2 | Document 1 Overview |
| 3 | Document 2 Overview |
| 4 | Key Findings |
| 5 | Comparative Analysis |
| 6 | Risk Assessment |
| 7 | Recommendations |
| 8 | Conclusion |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Streamlit** | Web app UI |
| **PyMuPDF (fitz)** | Extract text + images from PDFs |
| **Groq AI** | LLM for report generation |
| **llama-3.3-70b-versatile** | AI model (free, very fast) |
| **ReportLab** | Generate downloadable PDF |
| **Python-dotenv** | Manage API keys |

---

## 📁 Project Structure

```
ddr-report-generator/
├── app.py               ← Streamlit UI - main entry point
├── config.py            ← All settings and API keys
├── grok_service.py      ← Groq API communication
├── pdf_parser.py        ← Extract text + images from PDFs
├── report_generator.py  ← Structure and format the report
├── pdf_export.py        ← Generate downloadable PDF
├── requirements.txt     ← Python dependencies
├── README.md            ← This file
└── .env                 ← API keys (NOT uploaded to GitHub)
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/saurabhshirole1/ddr-report-generator.git
cd ddr-report-generator
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your Groq API key

Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_key_here
```

Get a free API key at: https://console.groq.com

### 5. Run the app

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🚀 How to Use

1. Open the app in your browser
2. Upload **Document 1** (first PDF)
3. Upload **Document 2** (second PDF)
4. Click **"Generate DDR Report"**
5. Wait 30-60 seconds for AI analysis
6. Read the report on screen
7. Click **"Download Report as PDF"**

---

## 🔒 API Key Security

- Never commit your `.env` file to GitHub
- The `.gitignore` file already excludes `.env`
- Get your free Groq API key at https://console.groq.com
- Groq free tier: **14,400 requests/day**

---

## 📝 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Groq API key from console.groq.com |

---

## 🔧 What I Would Improve

- Add support for more file formats (DOCX, TXT)
- Add option to choose report template
- Add chart generation for numerical data
- Add support for scanned PDFs using OCR
- Add multi-language report generation

---

## 🤖 AI Model Details

**Model:** `llama-3.3-70b-versatile`  
**Provider:** Groq AI  
**Context window:** 128K tokens  
**Speed:** ~500 tokens/second (very fast)  
**Cost:** Free on Groq's free tier
