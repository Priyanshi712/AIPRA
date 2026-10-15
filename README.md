# AIPRA — Autonomous Intelligence Platform for Research & Analysis

A Streamlit research agent that plans, searches, and synthesizes answers to your questions — with text, voice, or image input.

## Features

- **Text input** — type your research question directly.
- **Voice input** — record a question in-browser; transcribed via the free Google Web Speech API.
- **Image input** — upload a photo/screenshot; text is extracted via OCR and used as your question.
- Configurable research depth (Quick / Standard / Deep) and number of evidence sources.
- Session history, query count, and research level tracking.

## Setup & Run Locally

### 1. Download or Clone the Source Code
```bash
git clone https://github.com/Priyanshi712/AIPRA.git
cd AIPRA
```
*(Or click the green **Code** button on GitHub and choose **Download ZIP**).*

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) System Binaries
- **Voice input**: Requires `ffmpeg` on your system PATH.
- **Image OCR**: Requires the Tesseract OCR binary:
  - **macOS**: `brew install tesseract`
  - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr ffmpeg`
  - **Windows**: [UB-Mannheim Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)

### 4. (Optional) API Keys
Create a `.env` file or export environment variables:
```bash
GEMINI_API_KEY="your-gemini-key"
SERPER_API_KEY="your-serper-key" # optional
```
*Note: AIPRA includes automatic zero-key fallbacks (DuckDuckGo + Wikipedia + extractive synthesis) if no API keys are provided.*

### 5. Launch the App
```bash
streamlit run app.py
```

## Online Deployment (Streamlit Community Cloud)

1. Fork or push this repository to your GitHub account: `https://github.com/Priyanshi712/AIPRA`
2. Log into [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app** and select:
   - **Repository**: `Priyanshi712/AIPRA`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Under **Advanced settings > Secrets**, you can optionally add your API keys:
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   SERPER_API_KEY = "your_serper_key_here"
   ```
5. Click **Deploy!**

## Project Structure

```
AIPRA/
├── app.py            # Streamlit dashboard and user interface
├── agent.py          # Research agent orchestration & execution flow
├── search.py         # Multi-strategy search engine (Serper, Google, DuckDuckGo, Wikipedia)
├── llm.py            # AI planning & synthesis (Gemini API with heuristic fallbacks)
├── Voice_Input.py    # Microphone recording and voice-to-text
├── Image_input.py    # Image upload and OCR text extraction
├── requirements.txt  # Python package dependencies
├── packages.txt      # Debian system packages for Streamlit Cloud (tesseract, ffmpeg)
└── README.md         # Documentation and setup guide
```