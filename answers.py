from PIL import Image
from pylibdmtx.pylibdmtx import encode
import json
import io
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PyPDF4 import PdfFileReader


# format dict {"pts": 1.5, "ans": 0}
def get_datamatrix(question):
    encoded = encode(json.dumps(question).encode('utf8'))
    return Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)


def get_a4_with_image(x, y, img):
    reportlab_pil_img = ImageReader(img)
    packet = io.BytesIO()
    blank = Canvas(packet, pagesize=A4)
    blank.drawImage(reportlab_pil_img, x, y, width=75, height=75)
    blank.save()
    packet.seek(0)

    new = PdfFileReader(packet)
    return new.getPage(0)


# format csv
# answer id,points_true,points_false
# 0,1.5,0
# 2,1,-0.5
# same order as questions in the PDF
def read_answers(path):
    questions = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = line.strip().split(",")
            questions.append({"pts": float(line[1]), "ans": int(line[0]), "neg": line[2]})
    return questions
