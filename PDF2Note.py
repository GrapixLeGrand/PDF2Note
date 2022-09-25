
import argparse
from pdf2image import convert_from_path
import os
from fpdf import FPDF

# conda install -c conda-forge pdf2image

TEST_PDF = "admin.pdf"
DEFAULT_OUT_PATH = "pdf2NoteOut.pdf"
SAVE_DIRECTORY = "save"
MARGIN = 20

def main():
    print("Welcome to pdf maker")
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_path", nargs='?', help="path to the pdf to mod", type=str)
    parser.add_argument("--pdf_out", nargs='?', help="path to the pdf output", type=str)
    parser.add_argument("--scale", nargs='?', help="scale of each mosaique", default=100, type=int)
    parser.add_argument("--margin", nargs='?', help="margin", default=MARGIN, type=int)
    parser.add_argument("--indices", nargs='+', help="indices to take as 1-2, 4-5, ...]", type=str)
    args = parser.parse_args()

    pdf_path = args.pdf_path
    if (args.pdf_path is None):
        print("Warining you didn't entered a path, using default " + TEST_PDF)
        pdf_path = TEST_PDF

    pdf_out = args.pdf_out
    if (pdf_out is None):
        print("Warining you didn't entered an output path, using default " + DEFAULT_OUT_PATH)
        pdf_out = DEFAULT_OUT_PATH

    print(f"using scale {args.scale}")
    print(f"using margin {args.margin}")
    print(f"indices: {args.indices}")

    print("path to the pdf: " + pdf_path)

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(0)
    pdf.set_font('Arial','', 10)

    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
    else:
        files = os.listdir(SAVE_DIRECTORY)
        [os.remove(SAVE_DIRECTORY + "/" + f) for f in files]

    images = convert_from_path(pdf_path, fmt="png")

    kept_image_ranges = []
    if (args.indices is None):
        kept_image_ranges.append((0, len(images)))
    else:
        l1 = [index.split("-") for index in args.indices]
        l2 = [(int(part[0])-1, int(part[1])) for part in l1]
        if (len(l2) > 0):
            for i in range(0, len(l2) - 1):
                a1, b1 = l2[i]
                a2, _ = l2[i+1]
                assert(a1 <= b1 and b1 < a2)
        kept_image_ranges = l2
    
    for a, b in kept_image_ranges:
        for i in range(a, b):
            images[i].save(SAVE_DIRECTORY + '/' + str(i) +'.png', 'PNG')
    
    print("finish")
    
    OFFSETX = args.margin
    OFFSETY = pdf.h / 2
    WIDTH = args.scale
    page_counter = 1
    for a, b in kept_image_ranges:
        for i in range(a, b, 2):
            pdf.add_page()
            pdf.line(OFFSETX, 0, OFFSETX, pdf.h)
            pdf.image(f"{SAVE_DIRECTORY}/{str(i)}.png", x=OFFSETX, y=0, w=WIDTH, type="png")

            h_image = WIDTH * images[i].height / images[i].width
            pdf.line(OFFSETX, h_image, OFFSETX + WIDTH, h_image)
            pdf.line(OFFSETX + WIDTH, h_image, OFFSETX + WIDTH, 0)


            pdf.text(OFFSETX / 2, pdf.h - OFFSETX / 2, str(page_counter))
            page_counter += 1
            if (i + 1 >= b):
                continue
            pdf.line(OFFSETX, OFFSETY, pdf.w, OFFSETY)

            pdf.line(OFFSETX, h_image + OFFSETY, OFFSETX + WIDTH, h_image + OFFSETY)
            pdf.line(OFFSETX + WIDTH, h_image + OFFSETY, OFFSETX + WIDTH, OFFSETY)

            pdf.image(f"{SAVE_DIRECTORY}/{str(i+1)}.png", x=OFFSETX, y=OFFSETY, w=WIDTH, type="png")

    pdf.output(pdf_out, "F")




if __name__ == "__main__":
    main()