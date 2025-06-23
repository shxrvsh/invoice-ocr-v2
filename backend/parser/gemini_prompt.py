import requests
import json5
from config import GEMINI_API_KEY
from .utils import clean_gemini_response



def generate_gemini_response(ocr_data):
    prompt = f"""
You are an invoice parser. Extract and return the following from the text below as structured JSON:
make necessary spelling corrections, and ensure the output is clean and structured.
correctly identify and extract the following fields(if those fields are not present create new fields with what you can extract):
try to make the most sense of the text and match the fields as best and as logical as possible.
when you are returning numbers make sure you return them as strings and follow the american number format, i.e. use '.' as decimal separator and ' ' as thousands separator and do not round off the decimals.
do not add trailing decimal zeros if not given in the actual text.
1. "Seller Information"
2. "Client Information"
3. "Products"
4. "Totals"
Return in proper JSON format only. No explanation.

Text:
{ocr_data["full_text"]}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers=headers, json=payload)
    raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
    clean_text = clean_gemini_response(raw_text)
    return json5.loads(clean_text)