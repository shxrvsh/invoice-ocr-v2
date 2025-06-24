from fastapi import FastAPI, UploadFile, File,Form
from fastapi.responses import JSONResponse
from parser.ocr_layout import extract_layout_and_text
from parser.llm_router import generate_llm_response, chatbot_llm_response
from parser.matcher import map_fields_to_boxes
import pickle
import uuid
import os

app = FastAPI()

DATA_DIR = "./models"
os.makedirs(DATA_DIR, exist_ok=True)

@app.post("/parse")
async def parse_invoice(file: UploadFile = File(...),
    llm_choice: str = Form("gemini") ):
    img_path, layout_text = extract_layout_and_text(file)
    parsed_json = generate_llm_response(layout_text["full_text"], llm=llm_choice)
    print("Generated JSON from LLM:", parsed_json)
    ui_data = map_fields_to_boxes(parsed_json,layout_text["box_to_text"])

    file_id = f"ui_data_{uuid.uuid4().hex}.pkl"
    file_path = os.path.join(DATA_DIR, file_id)
    with open(file_path, "wb") as f:
        pickle.dump({"image": img_path, "fields": ui_data}, f)

    return JSONResponse({
        "message": "✅ Invoice parsed",
        "file_id": file_id,
        "preview": dict(list({k: v['value'] for k, v in ui_data.items()}.items())[:5])
    })

@app.post("/chat")
async def chat_with_invoice(
    file_id: str = Form(...),
    question: str = Form(...),
    llm_choice: str = Form("gemini")
):
    file_path = os.path.join(DATA_DIR, file_id)
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    
    flat_text = "\n".join([f"{k}: {v['value']}" for k, v in data["fields"].items()])

    response = chatbot_llm_response(flat_text, question, llm=llm_choice)
    return JSONResponse({"reply": response})