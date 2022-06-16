# import module
import json
from pdf2image import convert_from_path
from pylibdmtx.pylibdmtx import decode as decode_dm
import cv2
import numpy as np


def find_checkboxes(image):
    # Load image, convert to grayscale, Gaussian blur, Otsu's threshold
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find contours and filter using contour area filtering to remove noise
    cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    AREA_THRESHOLD = 10
    for c in cnts:
        area = cv2.contourArea(c)
        if area < AREA_THRESHOLD:
            cv2.drawContours(thresh, [c], -1, 0, -1)

    # Repair checkbox horizontal and vertical walls
    repair_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))
    repair = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, repair_kernel1, iterations=1)
    repair_kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 5))
    repair = cv2.morphologyEx(repair, cv2.MORPH_CLOSE, repair_kernel2, iterations=1)

    # Detect checkboxes using shape approximation and aspect ratio filtering
    checkbox_contours = []
    cnts, _ = cv2.findContours(repair, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.035 * peri, True)
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = w / float(h)
        if len(approx) == 4 and (aspect_ratio >= 0.8 and aspect_ratio <= 1.2):
            cv2.rectangle(original, (x, y), (x + w, y + h), (36, 255, 12), 3)
            checkbox_contours.append(c)

    print('Checkboxes:', len(checkbox_contours))
    cv2.namedWindow("sortie_debug", cv2.WINDOW_NORMAL)

    cv2.imshow("sortie_debug", thresh)
    cv2.resizeWindow("sortie_debug", 550, 940)
    cv2.waitKey()
    cv2.imshow("sortie_debug", repair)
    cv2.waitKey()
    cv2.imshow("sortie_debug", original)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Converts pdf scan directly to list of images (one per page)
    # need poppler binary in /bin
    scan = convert_from_path("./data/scan_test.pdf", poppler_path="./bin/poppler-22.04.0/Library/bin")
    print("Input File is", len(scan), "pages.")
    for page_nb, pil_img in enumerate(scan):
        if page_nb == 0: #TODO debug only remove me
            continue
        print("  Handling page", page_nb)
        # Convert immage to opencv
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        # Decode codes
        data = decode_dm(cv_img)
        print(data)

        #TODO check for flag instead
        if page_nb == 0:
            find_checkboxes(cv_img)
        else:
            for code in data:
                question = json.loads(code.data)

                sub = cv_img.copy()
                r = code.rect
                r_y = sub.shape[0]-r.top # y is reversed apparently

                cv2.rectangle(sub, (r.left, r_y), (r.left + r.width, r_y - r.height), (36, 255, 12), 3)

                cv2.namedWindow("sortie_debug", cv2.WINDOW_NORMAL)
                cv2.imshow("sortie_debug", sub)
                cv2.resizeWindow("sortie_debug", 550, 920)
                cv2.waitKey()
                cv2.destroyAllWindows()




