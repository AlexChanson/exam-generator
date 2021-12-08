from PyPDF4 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from random import randint, choice
from copy import deepcopy


def get_questions():
    s = "A"
    s += str(randint(1, 6))
    s += ", B"
    b1 = randint(1, 6)
    s += str(b1)
    s += ", B"
    s += str(choice(list(filter(lambda x: x != b1, range(1, 7)))))
    s += ", C"
    s += str(randint(1, 6))
    return s


def create_watermark(input_pdf, output):
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for i in range(80):
        questions = get_questions()
        page = deepcopy(pdf_reader.getPage(0))

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(270, 575, questions)
        can.save()
        # create a new PDF with Reportlab
        new_text = PdfFileReader(packet)
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        page.mergePage(new_text.getPage(0))

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        textobject = can.beginText(140, 320)
        textobject.setFont("Helvetica", 12)
        for line in questions.split(","):
            textobject.textLine(line.strip() + " -->")
            textobject.textLine()
        can.drawText(textobject)
        can.save()
        # create a new PDF with Reportlab
        new_text = PdfFileReader(packet)
        # move to the beginning of the StringIO buffer
        packet.seek(0)
        page.mergePage(new_text.getPage(0))

        pdf_writer.addPage(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)


if __name__ == '__main__':
    create_watermark(
        input_pdf='data/input.pdf',
        output='data/output.pdf')
