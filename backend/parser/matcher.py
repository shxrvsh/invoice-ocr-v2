from difflib import SequenceMatcher
from .utils import flatten_json, normalize

def map_fields_to_boxes(structured_data, box_to_text=None):
    if box_to_text is None:
        raise ValueError("box_to_text missing")

    flat_data = flatten_json(structured_data)
    ui_data = {}

    for label, value in flat_data.items():
        value_str = str(value).strip()
        value_norm = normalize(value_str)

        matched_box = None
        for item in box_to_text:
            text_norm = normalize(item["text"])
            if (value_norm in text_norm) or (text_norm in value_norm):
                matched_box = item["box"]
                break

        if not matched_box:
            best_score = 0
            for item in box_to_text:
                score = SequenceMatcher(None, value_norm, normalize(item["text"])).ratio()
                if score > best_score:
                    best_score = score
                    matched_box = item["box"]
        ui_data[label] = {"value": value_str, "box": matched_box}
    return ui_data