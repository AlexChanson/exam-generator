from PyPDF4 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from random import randint, choice
from copy import deepcopy


# change this to draw a random list of questions
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


def make_for_class(input_pdf, output, n_students, ):
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for i in range(n_students):
        questions = get_questions()
        page = deepcopy(pdf_reader.getPage(0))

        # Questions top of the page
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(270, 575, questions) # Adjust position here
        can.save()
        new_text = PdfFileReader(packet)
        packet.seek(0)
        page.mergePage(new_text.getPage(0))

        # Questions answer section
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        textobject = can.beginText(140, 320) # Adjust position here
        textobject.setFont("Helvetica", 12)
        for line in questions.split(","):
            textobject.textLine(line.strip() + " -->")
            textobject.textLine()
        can.drawText(textobject)
        can.save()
        new_text = PdfFileReader(packet)
        packet.seek(0)
        page.mergePage(new_text.getPage(0))

        pdf_writer.addPage(page)

    with open(output, 'wb') as out:
        pdf_writer.write(out)


if __name__ == '__main__':
    make_for_class(input_pdf='data/input.pdf', output='data/output.pdf', n_students=80)
