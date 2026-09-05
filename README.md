# AIPRA — Autonomous Intelligence Platform for Research & Analysis

A Streamlit research agent that plans, searches, and synthesizes answers to your questions — with text, voice, or image input.

## Features

- **Text input** — type your research question directly.
- **Voice input** — record a question in-browser; transcribed via the free Google Web Speech API.
- **Image input** — upload a photo/screenshot; text is extracted via OCR and used as your question.
- Configurable research depth (Quick / Standard / Deep) and number of evidence sources.
- Session history, query count, and research level tracking.

## Setup

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:
```
streamlit
streamlit-mic-recorder
SpeechRecognition
pytesseract
Pillow
```

Voice input also needs `ffmpeg` on your system PATH, and image OCR needs the Tesseract binary installed:
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- Windows: [UB-Mannheim Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)

## Run

```bash
streamlit run app.py
```

## Project structure

```
app.py            # main Streamlit UI
voice_input.py    # mic recording + speech-to-text
image_input.py    # image upload + OCR text extraction
agent.py          # research agent logic (not included here)
```