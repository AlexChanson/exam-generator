from PyPDF4 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from random import choice
from copy import deepcopy
from answers import get_datamatrix, get_a4_with_image, read_answers


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


def make_for_student(all_questions, pools, questions_per_pool, questions_pdf, out, fuzz, per_page, y_offset, answers):
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

    page0 = deepcopy(questions_pdf.getPage(0))
    q_pages = 0
    # add marker to first page
    if answers is not None:
        page0.mergeTranslatedPage(get_a4_with_image(255, 50, get_datamatrix({"flag": "42"})), tx=0, ty=0)
    out.addPage(page0)

    q_page = get_blank_a4()
    cnt = 0
    for i, q in enumerate(student_questions):
        if cnt == per_page:
            cnt = 0
            out.addPage(q_page)
            q_page = get_blank_a4()
            q_pages += 1
        # add question
        q_page.mergeTranslatedPage(questions_pdf.getPage(q+1), tx=0, ty=-cnt*y_offset)
        f = ""
        if fuzz:
            f = str(choice("ABCDEF"))
        # add question number
        # x offset -> 182
        q_page.mergeTranslatedPage(get_a4_with_string(172, 708, f+str(q+1)), tx=0, ty=-cnt*y_offset)
        cnt += 1
        # add answer
        if answers is not None:
            q_page.mergeTranslatedPage(get_a4_with_image(50, 840-y_offset, get_datamatrix(answers[q])), tx=0, ty=-(cnt-1)*y_offset)
    out.addPage(q_page)
    q_pages += 1

    # This is for double-sided printing
    # We need an even number of pages per student (odd number of question pages + the front page)
    if q_pages % 2 == 0:
        out.addPage(get_blank_a4())


def make_for_class(input_pdf, output, n_students, questions_pools, questions_per_pool, fuzz=False, per_page=4, y_offset=130, encode_answers=None):
    if encode_answers is not None:
        answers = read_answers(encode_answers)
    else:
        answers = None

    all_questions = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()

    for i in range(n_students):
        make_for_student(range(all_questions.getNumPages()-1), questions_pools, questions_per_pool, all_questions, pdf_writer, fuzz, per_page, y_offset, answers)

    with open(output, 'wb') as out:
        pdf_writer.write(out)


if __name__ == '__main__':
    students = 1
    question_pools = [6]
    questions_per_pool = [5,5]
    fuzz = True

    make_for_class("./data/QCM_Archi_L2.pdf",
                   "./data/test.pdf",
                   students, question_pools, questions_per_pool, fuzz, y_offset=200, per_page=3, encode_answers="./data/ans.csv")