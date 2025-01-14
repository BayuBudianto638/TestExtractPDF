
'''
import os
import pdfplumber


def extract_chapters_and_text(pdf_path, output_folder):
    """Extracts chapters, subsections, and full text from a PDF using PDFPlumber."""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open the PDF
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Extract the text of the page
            text = page.extract_text()
            if not text:
                text = "No text found on this page."

            # Split text into sentences for chapter and subsection
            sentences = [s.strip() for s in text.splitlines() if s.strip()]
            chapter = sentences[0] if sentences else "Unknown Chapter"
            subsection = sentences[1] if len(sentences) > 1 else "Unknown Subsection"

            # Save text to file
            text_file_path = os.path.join(output_folder, f"page_{page_number}.txt")
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(f"Chapter: {chapter}\n")
                text_file.write(f"Subsection: {subsection}\n\n")
                text_file.write(text)

            print(f"Page {page_number} extracted: Chapter - '{chapter}', Subsection - '{subsection}'")

    print(f"Extraction completed. Files are saved in '{output_folder}'")


# Example usage
pdf_path = "/home/bayu-budianto/Documents/source_doc.pdf"  # Replace with your PDF path
output_folder = "output_folder"  # Replace with your desired output folder
extract_chapters_and_text(pdf_path, output_folder)

import io
import os
import pdfplumber
from PIL import Image


def save_image(image, output_folder, page_number, image_index):
    """Save an image extracted from the PDF to a file."""
    image_path = os.path.join(output_folder, f"image_page_{page_number}_{image_index}.png")
    image.save(image_path)
    print(f"Saved image: {image_path}")


def extract_text_and_images_with_pdfplumber(pdf_path, output_folder):
    """Extract text and images from a PDF using PDFPlumber."""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Open the PDF with PDFPlumber
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Extract text
            page_text = page.extract_text()
            text_file_path = os.path.join(output_folder, f"page_{page_number}.txt")
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(page_text or "No text found on this page.")
            print(f"Saved text for Page {page_number} to {text_file_path}")

            # Extract images
            if page.images:
                for image_index, img_dict in enumerate(page.images, start=1):
                    x0, y0, x1, y1 = img_dict["x0"], img_dict["y0"], img_dict["x1"], img_dict["y1"]
                    # Crop the image from the page
                    cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image()
                    pil_image = cropped_image.original
                    save_image(pil_image, output_folder, page_number, image_index)

    print(f"Extraction completed. Files are saved in {output_folder}")


# Open the PDF file
with pdfplumber.open("/home/bayu-budianto/Downloads/Learn_from_Defect_M&E_No_20_Lack_of_Electrical_Capacity_for_Emergency.pdf") as pdf:
    # Iterate through the pages
    for page_num, page in enumerate(pdf.pages):
        # Extract text from the page
        text = page.extract_text()
        print(f"Text on page {page_num + 1}:\n", text)

        # Extract images from the page
        for image in page.images:
            # Extract image information
            #x0, y0, x1, y1 = image['x0'], image['y0'], image['x1'], image['y1']
            image_bytes = image['stream'].get_data()

            # Convert image bytes to a PIL Image object
            image_obj = Image.open(io.BytesIO(image_bytes))

            # Save the extracted image (or do further processing)
            image_obj.save(f"image_page_{page_num + 1}.png")
            print(f"Saved image from page {page_num + 1}")

# Example usage
#pdf_path = "/home/bayu-budianto/Downloads/Learn_from_Defect_M&E_No_20_Lack_of_Electrical_Capacity_for_Emergency.pdf"  # Replace with your PDF file path
#output_folder = "output_folder"  # Replace with your desired output folder
#extract_text_and_images_with_pdfplumber(pdf_path, output_folder)
'''

import os
import pdfplumber
from PIL import Image


def save_image(image, output_folder, page_number, image_index):
    """Save a PDF image as a file."""
    image_path = os.path.join(output_folder, f"image_page_{page_number}_{image_index}.png")
    image.save(image_path)
    print(f"Saved image: {image_path}")


def extract_text_and_images(pdf_path, text_output_folder, image_output_folder):
    """Extract text and images from a PDF using PDFPlumber."""
    # Ensure the output folders exist
    os.makedirs(text_output_folder, exist_ok=True)
    os.makedirs(image_output_folder, exist_ok=True)

    # Open the PDF with PDFPlumber
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # Extract text
            text = page.extract_text() or "No text found on this page."
            lines = [line.strip() for line in text.splitlines() if line.strip()]

            # Get chapter and subsection
            chapter = lines[0] if lines else "Unknown Chapter"
            subsection = lines[1] if len(lines) > 1 else "Unknown Subsection"

            # Save text to file
            text_file_path = os.path.join(text_output_folder, f"page_{page_number}.txt")
            with open(text_file_path, "w", encoding="utf-8") as text_file:
                text_file.write(f"Chapter: {chapter}\n")
                text_file.write(f"Subsection: {subsection}\n\n")
                text_file.write(text)
            print(f"Saved text for Page {page_number}: Chapter - '{chapter}', Subsection - '{subsection}'")

            # Extract and save images
            for image_index, img_dict in enumerate(page.images, start=1):
                # Get image bounding box and raw data
                x0, y0, x1, y1 = img_dict["x0"], img_dict["y0"], img_dict["x1"], img_dict["y1"]
                cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image()
                pil_image = cropped_image.original
                save_image(pil_image, image_output_folder, page_number, image_index)

    print(f"Extraction completed. Text saved in '{text_output_folder}' and images saved in '{image_output_folder}'.")


# Example usage
pdf_path = "/home/bayu-budianto/Documents/source_doc.pdf"  # Replace with the path to your PDF file
text_output_folder = "text_output"  # Folder to save extracted text
image_output_folder = "image_output"  # Folder to save extracted images

extract_text_and_images(pdf_path, text_output_folder, image_output_folder)


# Example usage
pdf_path = "/home/bayu-budianto/Documents/source_doc.pdf"  # Replace with your PDF file path
output_folder = "output_folder"  # Replace with your desired output folder
