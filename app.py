from flask import Flask, request, jsonify
import pdfplumber
import json
import re
import google.generativeai as genai
from flask_cors import CORS

# ----------------------------
# Configure Gemini API
# ----------------------------
genai.configure(api_key="AIzaSyBcidCvMN3fF3LfKmZNFr1ZRo64P-7GdlU")

app = Flask(__name__)
CORS(app)  # enable CORS for all routes


# ----------------------------
# Helpers
# ----------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # handle blank pages safely
    return text

def clean_response_text(response_text: str) -> str:
    """Remove markdown fences and clean text."""
    cleaned = re.sub(r"```(?:json)?", "", response_text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    return cleaned

def generate_flashcards(text: str):
    prompt = f"""
    Create at least 5 flashcards from the following study material.
    Return output strictly in JSON format as:
    {{
      "flashcards": [
        {{"question": "...", "answer": "..."}},
        ...
      ]
    }}

    Text: {text[:4000]}
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    try:
        cleaned_text = clean_response_text(response.text)
        data = json.loads(cleaned_text)

        # Validate structure
        if "flashcards" not in data or not isinstance(data["flashcards"], list):
            data = {"flashcards": [{"question": "Parsing error", "answer": response.text}]}

    except json.JSONDecodeError:
        data = {"flashcards": [{"question": "Parsing error", "answer": response.text}]}
    
    return data

# ----------------------------
# Flask Routes
# ----------------------------
@app.route("/generate-flashcards", methods=["POST"])
def generate_flashcards_api():
    if "file" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files["file"]

    try:
        text = extract_text_from_pdf(pdf_file)
        flashcards = generate_flashcards(text)
        return jsonify(flashcards)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# Run Flask App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
