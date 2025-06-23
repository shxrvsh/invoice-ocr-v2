from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
import requests
import os
from django.conf import settings
import pickle
from PIL import Image, ImageDraw
import uuid

FASTAPI_URL = "http://localhost:8000"  # Update if your FastAPI runs elsewhere

def home(request):
    return render(request, 'invoice_app/home.html')

def upload_view(request):
    if request.method == "POST" and request.FILES["document"]:
        uploaded_file = request.FILES["document"]
        relative_path = default_storage.save(uploaded_file.name, uploaded_file)
        full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        with open(full_path, "rb") as f:
            files = {"file": (uploaded_file.name, f, uploaded_file.content_type)}
            response = requests.post(f"{FASTAPI_URL}/parse", files=files)
        
        if response.status_code == 200:
            file_id = response.json()["file_id"]
            request.session["file_id"] = file_id
            request.session["image_name"] = full_path
            return redirect("viewer")
        else:
            return render(request, 'invoice_app/upload.html', {"error": "Failed to parse."})
    return render(request, 'invoice_app/upload.html')

def viewer(request):
    try:
        file_id = request.session.get("file_id")
        file_path = os.path.join(settings.BASE_DIR, "../backend", "models", file_id)
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        image_path = request.session.get("image_name")
        image_url = settings.MEDIA_URL + os.path.basename(image_path)
        print("Image Path:", image_url)
        fields = data["fields"]
        selected = request.GET.get("field") or list(fields.keys())[0]
        selected_box = fields[selected].get("box")

        value = fields[selected]["value"]

        # Draw box
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        if selected_box:
            x1, y1, x2, y2 = selected_box
            draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
            draw.text((x1, y1 - 10), selected, fill="red")

        # Save new image temporarily
        new_filename = f"boxed_{uuid.uuid4().hex}.jpg"
        boxed_path = os.path.join(settings.MEDIA_ROOT, new_filename)
        image.save(boxed_path)

        # Prepare media URL for the new image
        image_url = settings.MEDIA_URL + new_filename
        

        return render(request, 'invoice_app/viewer.html', {
            "image_path": image_url,
            "fields": fields,
            "selected_key": selected,
            "selected_box": selected_box,
            "value": fields[selected]["value"]
        })
    except FileNotFoundError:
        return redirect("upload")

def chatbot(request):
    if request.method == "POST":
        question = request.POST.get("question")
        file_id = request.session.get("file_id")
        file_path = os.path.join(settings.BASE_DIR, "../backend", "models", file_id)
        with open(file_path, "rb") as f:
            data = pickle.load(f)
        fields = data["fields"]
        flat_text = "\n".join([f"{k}: {v['value']}" for k, v in fields.items()])
        prompt = f"""
You are an intelligent assistant. Use the following extracted document fields to answer user questions accurately.

Extracted Data:
{flat_text}

Question: {question}
Only answer based on the extracted data above.
"""
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        api_key = "AIzaSyAxy3LkOnpgZhzHiyCuoz_ZbpciPOTDJWk"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        reply = requests.post(url, headers=headers, json=payload).json()['candidates'][0]['content']['parts'][0]['text']
        return render(request, 'invoice_app/chatbot.html', {"response": reply, "question": question})

    return render(request, 'invoice_app/chatbot.html')