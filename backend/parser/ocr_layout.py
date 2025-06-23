import layoutparser as lp
import cv2
import tempfile
from PIL import Image

def extract_layout_and_text(uploaded_file):
    tmp_path = tempfile.NamedTemporaryFile(delete=False).name
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.file.read())

    image_cv = cv2.imread(tmp_path)
    model = lp.Detectron2LayoutModel(
        config_path="lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
        model_path="/Users/sharveshwars/.torch/iopath_cache/s/dgy9c10wykk4lq4/model_final.pth",
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.3]
    )

    layout = model.detect(image_cv)
    layout_sorted = sorted(layout, key=lambda b: (b.block.y_1, b.block.x_1))
    ocr_agent = lp.TesseractAgent(languages='eng')
    box_to_text = []

    for block in layout_sorted:
        if block.type in ["Text", "Title", "Table", "List"]:
            segment = block.crop_image(image_cv)
            text = ocr_agent.detect(segment)
            if text.strip():
                box = tuple(map(int, block.coordinates))
                box_to_text.append({"box": box, "text": text.strip()})

    full_text = "\n\n".join([b["text"] for b in box_to_text])
    return tmp_path, {"full_text": full_text, "box_to_text": box_to_text}