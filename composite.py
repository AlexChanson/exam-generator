from PyPDF4 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from random import randint, choice
from copy import deepcopy


def get_questions(pool, k):
    assert k <= len(pool)
    drawn = []
    while len(drawn) < k:
        drawn.append(choice(list(filter(lambda x: x not in drawn, pool))))
    return drawn


def get_blank_a4():
    return get_a4_with_string(0, 0, ".")


def get_a4_with_string(x, y, code):
    packet = io.BytesIO()
    blank = canvas.Canvas(packet, pagesize=A4)
    blank.drawString(x, y, code)
    blank.save()
    packet.seek(0)

    new = PdfFileReader(packet)
    return new.getPage(0)


def make_for_student(all_questions, pools, questions_per_pool, pdf_reader, out, fuzz):
    # Separate pools
    if pools is None or len(pools) == 0:
        question_pools = all_questions
    else:
        question_pools = []
        for i in range(len(pools)):
            if i == 0:
                question_pools.append([all_questions[q] for q in range(0, pools[i])])
            else:
                question_pools.append([all_questions[q] for q in range(pools[i-1], pools[i])])
        question_pools.append([all_questions[q] for q in range(pools[-1], len(all_questions))])

    # randomly draw questions
    student_questions = []
    for i, pool in enumerate(question_pools):
        student_questions.extend(get_questions(pool, questions_per_pool[i]))

    page0 = deepcopy(pdf_reader.getPage(0))
    out.addPage(page0)

    q_page = get_blank_a4()
    cnt = 0
    for i, q in enumerate(student_questions):
        if cnt == 4:
            cnt = 0
            out.addPage(q_page)
            q_page = get_blank_a4()
        q_page.mergeTranslatedPage(pdf_reader.getPage(q+1), tx=0, ty=-cnt*130)
        f = ""
        if fuzz:
            f = str(choice("ABCDEF"))
        q_page.mergeTranslatedPage(get_a4_with_string(182, 708, f+str(q+1)), tx=0, ty=-cnt*130)
        cnt += 1
    out.addPage(q_page)


def make_for_class(input_pdf, output, n_students, questions_pools, questions_per_pool, fuzz=False):
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for i in range(n_students):
        make_for_student(range(pdf_reader.getNumPages()-1), questions_pools, questions_per_pool, pdf_reader, pdf_writer, fuzz)

    with open(output, 'wb') as out:
        pdf_writer.write(out)


if __name__ == '__main__':
    students = 1
    question_pools = [6, 12]
    questions_per_pool = [1, 2, 1]
    fuzz = True

    make_for_class("/home/alex/PycharmProjects/exam-generator/data/QCM_BD_L2__1Q_per_page_(1).pdf",
                   "/home/alex/PycharmProjects/exam-generator/data/out.pdf",
                   students, question_pools, questions_per_pool, fuzz)