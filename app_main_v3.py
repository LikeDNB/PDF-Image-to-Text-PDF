import os
import re
import time
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
from fpdf import FPDF
import shutil


# Path to your PDF file
pdf_path = 'test.pdf'
# Specify the path to the folder for storing images
image_folder = 'images'
output_pdf_path = 'output.pdf'
language = "eng"  # rus, eng, deu
tesseract_path = r"""C:\\Program Files\\Tesseract-OCR\\tesseract.exe"""


def create_image():
    """
    Converts the pages of the PDF file into images
    and saves them to the specified folder.
    """

    # Path to Tesseract OCR executable
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Convert PDF to images with a resolution of 300 DPI
    pages = convert_from_path(pdf_path, 300)

    # Process each page and save as an image
    for i, page in enumerate(pages):
        image_path = os.path.join(image_folder, f'page_{i}.png')
        page.save(image_path, 'PNG')
        print(f"Page {i} saved as {image_path}")


def convert_img_to_pdf():
    """
    Converts the images generated from the PDF into a new PDF and performs OCR
    (Optical Character Recognition) on each image, then embeds the recognized
    text into the new PDF.
    """

    def extract_page_number(filename):
        """
        Extracts the numerical page number from the image file name.
        Args:
            filename (str): The name of the image file.
        Returns:
            int: The page number extracted from the filename.
        """
        match = re.search(r'page_(\d+)', filename)
        return int(match.group(1)) if match else 0

    # Get a list of all PNG image files in the image folder
    image_list = [os.path.join(image_folder, f)
                  for f in os.listdir(image_folder) if f.endswith('.png')]

    # Ensure that the files are sorted by page number
    image_list.sort(key=lambda f: extract_page_number(f))

    # Create a new PDF with recognized text
    pdf = FPDF()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 10)

    total_time = 0
    for image in image_list:
        try:
            # Measure the time taken for OCR processing
            start_time = time.time()
            text = pytesseract.image_to_string(Image.open(image),
                                               lang=f'{language}+fast')
            end_time = time.time()

            processing_time = end_time - start_time
            total_time += processing_time
            print(f"Processing {image} took {processing_time:.2f} seconds")

            # Add a new page to the PDF and write the recognized text
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.multi_cell(0, 10, text)
        except Exception as e:
            print(f"Error recognizing text on image {image}: {e}")

    # Save the new PDF with the recognized text
    pdf.output(output_pdf_path)

    # Print the total time taken for processing
    print(f"Total processing time: {total_time:.2f} seconds")


def clear_image_folder(folder_path):
    """
    Removes all files and subdirectories within the specified folder.

    Args:
        folder_path (str): The path to the folder
        whose contents need to be deleted.
    """
    # Check if the folder exists
    if os.path.exists(folder_path):
        # Remove all contents of the folder
        shutil.rmtree(folder_path)
        # Optionally recreate the folder after clearing
        os.makedirs(folder_path)
        print(f"All contents of the folder '{folder_path}' have been deleted.")
    else:
        print(f"The folder '{folder_path}' does not exist.")


create_image()
convert_img_to_pdf()
clear_image_folder(image_folder)
