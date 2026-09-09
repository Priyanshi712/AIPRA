"""
image_input.py
================
Image input module for AIPRA.

Lets the user upload a photo or screenshot (e.g. a photographed
question, a chart, a document snippet) and extracts any text from it
using OCR (pytesseract), so it can be used or edited as the research
question.

Install:
    pip install pytesseract Pillow

    Also requires the Tesseract OCR binary on the system:
        macOS:   brew install tesseract
        Ubuntu:  sudo apt-get install tesseract-ocr
        Windows: https://github.com/UB-Mannheim/tesseract/wiki

Usage (inside app.py):
    from image_input import get_image_query
    image_text = get_image_query()
"""

import streamlit as st
from PIL import Image

try:
    import pytesseract
    _OCR_AVAILABLE = True
except ImportError:
    _OCR_AVAILABLE = False


def get_image_query():
    """
    Renders an image uploader. If the image contains readable text,
    OCR is run and the extracted text is offered back as an editable
    research question.

    Returns:
        str: the (possibly user-edited) extracted text, or
        None: if no image has been uploaded, no text was found, or
              the required packages aren't installed.
    """

    st.caption("📷 Upload a photo or screenshot of your question.")

    uploaded = st.file_uploader(
        "Upload image",
        type=["png", "jpg", "jpeg", "webp"],
        label_visibility="collapsed",
        key="aipra_image_uploader"
    )

    if uploaded is None:
        return None

    image = Image.open(uploaded)
    st.image(image, caption="Uploaded image", use_container_width=True)

    if not _OCR_AVAILABLE:
        st.warning(
            "Text extraction needs `pytesseract` (plus the Tesseract OCR "
            "binary installed on your system). Install the Python package "
            "with:\n\n`pip install pytesseract Pillow`"
        )
        return None

    with st.spinner("Reading text from image..."):
        try:
            extracted = pytesseract.image_to_string(image).strip()
        except Exception as e:
            st.error(f"OCR failed: {e}")
            return None

    if not extracted:
        st.info("No readable text found in that image.")
        return None

    edited = st.text_area(
        "Extracted text — edit if needed, then it'll be used as your question:",
        value=extracted,
        key="aipra_image_extracted_text"
    )

    return edited.strip()