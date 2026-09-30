"""PDF utilities (extracted from legacy testing.py)."""
import os
from pdf2image import convert_from_path
from PIL import Image
import pypandoc

def convert_docx_to_pdf(input_docx, temp_pdf, pdf_engine='pdflatex'):
    """Convert DOCX to PDF using pypandoc."""
    pypandoc.convert_file(input_docx, 'pdf', outputfile=temp_pdf, extra_args=['--pdf-engine=' + pdf_engine])


def convert_pdf_to_images(temp_pdf):
    """Convert PDF to images using pdf2image."""
    return convert_from_path(temp_pdf, dpi=300)

def convert_images_to_pdf(images, final_pdf):
    """Convert images back to a non-searchable PDF."""
    images[0].save(final_pdf, save_all=True, append_images=images[1:], quality=100)

def cleanup(intermediate_files):
    """Remove intermediate files if they exist."""
    for f in intermediate_files:
        if os.path.exists(f):
            os.remove(f)

def main():
    input_docx = 'input.docx'
    temp_pdf = 'temp_output.pdf'
    final_pdf = 'final_output.pdf'

    try:
        convert_docx_to_pdf(input_docx, temp_pdf)
        images = convert_pdf_to_images(temp_pdf)

        # Convert the images back to a PDF
        convert_images_to_pdf(images, final_pdf)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up intermediate files
        cleanup([temp_pdf])

if __name__ == "__main__":
    main()

