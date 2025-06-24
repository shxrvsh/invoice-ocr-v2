import os
import requests
import json
import json5
from dotenv import load_dotenv
import re
load_dotenv() 
# Load keys from environment or config (recommended in prod)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

def generate_llm_response(text, llm="gemini"):
    prompt = f"""
You are an invoice parser. Extract and return the following from the text below as structured JSON:
make necessary spelling corrections, and ensure the output is clean and structured.
correctly identify and extract the following fields(if those fields are not present create new fields with what you can extract):
try to make the most sense of the text and match the fields as best and as logical as possible.
when you are returning numbers make sure you return them as strings and follow the american number format, i.e. use '.' as decimal separator and ' ' as thousands separator and do not round off the decimals.
do not add trailing decimal zeros if not given in the actual text.
1. "Seller Information" – name, address, tax ID, IBAN (if present)
2. "Client Information" – name, address, tax ID
3. "Products" – list of items with: description, quantity, unit price, net amount, VAT, gross amount
4. "Totals" – Net worth, VAT amount, Gross worth

Return in proper JSON format only. No explanation.

Text:
{text}
""".strip()

    if llm == "gemini":
        return call_gemini(prompt)
    elif llm == "cohere":
        return call_cohere(prompt)
    elif llm == "together":
        return call_together(prompt)
    else:
        raise ValueError(f"Unsupported LLM: {llm}")

def clean_json_response(text):
    # 1. Remove markdown formatting
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if "{" in part:
                text = part.strip()
                break

    # 2. Remove 'json' label prefix
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # 3. Extract only the first valid JSON block using regex
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if not json_match:
        raise ValueError("No valid JSON found in LLM response.")

    json_text = json_match.group(0)

    try:
        return json5.loads(json_text)
    except Exception as e:
        print("❌ JSON5 parsing failed.")
        print("Raw Text Was:\n", json_text)
        raise e

def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    return clean_json_response(text)

def call_cohere(prompt):
    url = "https://api.cohere.ai/v1/chat"
    payload = {
        "message": prompt,
        "model": "command-r-plus",
        "temperature": 0.3,
        "preamble": "You are a professional invoice parser and must return only clean JSON output.",
    }
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    text = response.json()["text"]
    return clean_json_response(text)

def call_together(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "top_p": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    text = response.json()["choices"][0]["message"]["content"]
    print(f"Together Response:\n{text}\n")
    return clean_json_response(text)

# Make a prompt for the chatbot


def call_gemini_chat(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, headers=headers, json=payload)
    return res.json()["candidates"][0]["content"]["parts"][0]["text"]

def call_cohere_chat(prompt: str) -> str:
    url = "https://api.cohere.ai/v1/chat"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"message": prompt}
    res = requests.post(url, headers=headers, json=payload)
    return res.json()["text"]

def call_together_chat(prompt: str) -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4,
        "top_p": 0.7,
    }
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, json=payload)
    return res.json()["choices"][0]["message"]["content"]

def chatbot_llm_response(flat_text: str, question: str, llm: str = "gemini") -> str:
    prompt = f"""
    You are an intelligent assistant. Use the following extracted document fields to answer user questions accurately.

    Extracted Data:
    {flat_text}

    Question: {question}
    Only answer based on the extracted data above.
    """.strip()

    if llm == "gemini":
        return call_gemini_chat(prompt)
    elif llm == "cohere":
        return call_cohere_chat(prompt)
    elif llm == "together":
        return call_together_chat(prompt)
    else:
        raise ValueError("Invalid LLM choice")
