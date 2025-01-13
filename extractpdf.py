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


# Example usage
pdf_path = "/home/bayu-budianto/Documents/source_doc.pdf"  # Replace with your PDF file path
output_folder = "output_folder"  # Replace with your desired output folder
extract_text_and_images_with_pdfplumber(pdf_path, output_folder)


