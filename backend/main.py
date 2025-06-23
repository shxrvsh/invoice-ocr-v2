from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from parser.ocr_layout import extract_layout_and_text
from parser.gemini_prompt import generate_gemini_response
from parser.matcher import map_fields_to_boxes
import pickle
import uuid
import os

app = FastAPI()

DATA_DIR = "./models"
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/parse")
async def parse_invoice(file: UploadFile = File(...)):
    img_path, layout_text = extract_layout_and_text(file)
    gemini_json = generate_gemini_response(layout_text)
    print("Generated JSON from Gemini:", gemini_json)
    ui_data = map_fields_to_boxes(gemini_json,layout_text["box_to_text"])

    file_id = f"ui_data_{uuid.uuid4().hex}.pkl"
    file_path = os.path.join(DATA_DIR, file_id)
    with open(file_path, "wb") as f:
        pickle.dump({"image": img_path, "fields": ui_data}, f)

    return JSONResponse({
        "message": "✅ Invoice parsed",
        "file_id": file_id,
        "preview": dict(list({k: v['value'] for k, v in ui_data.items()}.items())[:5])
    })