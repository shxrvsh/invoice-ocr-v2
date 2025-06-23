import re

def clean_gemini_response(text):
    if "```" in text:
        # Extract content inside the first code block
        code_blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if code_blocks:
            text = code_blocks[0].strip()

    # Remove prefix like "json"
    if text.lower().startswith("json"):
        text = text[4:].strip()

    return text

def flatten_json(nested, parent_key=""):
    flat = {}
    if isinstance(nested, dict):
        for k, v in nested.items():
            new_key = f"{parent_key} → {k}" if parent_key else k
            flat.update(flatten_json(v, new_key))
    elif isinstance(nested, list):
        for i, item in enumerate(nested):
            new_key = f"{parent_key} → Row {i+1}"
            flat.update(flatten_json(item, new_key))
    else:
        flat[parent_key] = nested
    return flat

def normalize(text):
    return str(text).lower().strip().replace("\n", " ").replace(",", ".").replace("  ", " ").replace("$", "")