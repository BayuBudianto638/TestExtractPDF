import os
import re
import warnings

from langchain_community.document_loaders.blob_loaders import Blob
from pdf import PyPDFParser, _PDF_FILTER_WITHOUT_LOSS, \
    _PDF_FILTER_WITH_LOSS  # Import PyPDFParser from the provided file
from PIL import Image
import numpy as np


def save_images(images: list[np.ndarray], page_number: int):
    """Save images extracted from the PDF to files."""
    os.makedirs("extracted_images", exist_ok=True)  # Create folder to save images
    for idx, img_data in enumerate(images):
        image_filename = f"extracted_images/image_page_{page_number}_{idx + 1}.png"
        img = Image.fromarray(img_data)
        img.save(image_filename)
        print(f"Saved image: {image_filename}")


def extract_structure_and_images(pdf_path: str):
    """Extract chapters, subsections, text, and images from the PDF."""
    blob = Blob.from_path(pdf_path)  # Load PDF as binary data
    parser = PyPDFParser(extract_images=True)  # Enable image extraction

    chapter_pattern = r"^Chapter (\d+): (.*)$"  # Regex for chapter detection
    subsection_pattern = r"^\d+(\.\d+)+ (.*)$"  # Regex for subsection detection

    # Iterate through each page
    for document in parser.lazy_parse(blob):
        page_number = document.metadata.get("page", 0) + 1
        print(f"\nPage {page_number}:")
        page_content = document.page_content.split("\n")  # Split text into lines

        current_chapter = None
        current_subsection = None
        content_lines = []  # Collect remaining text for the subsection

        images = []

        for line in page_content:
            # Check for chapter titles
            chapter_match = re.match(chapter_pattern, line)
            if chapter_match:
                current_chapter = chapter_match.group(2)
                print(f"  Chapter: {current_chapter}")
                continue

            # Check for subsection titles
            subsection_match = re.match(subsection_pattern, line)
            if subsection_match:
                current_subsection = subsection_match.group(0)
                print(f"    Subsection: {current_subsection}")
                continue

            # Accumulate text
            content_lines.append(line)

        # Handle default chapter and subsection if none were found
        if not current_chapter:
            current_chapter = content_lines[0] if content_lines else "Untitled Chapter"
        if not current_subsection:
            current_subsection = (
                content_lines[1] if len(content_lines) > 1 else "Untitled Subsection"
            )

        print(f"  Chapter (default): {current_chapter}")
        print(f"    Subsection (default): {current_subsection}")

        # Print the remaining content as subsection text
        print("    Content:")
        print("\n".join(content_lines[2:]))

        # Extract and save images
        images = extract_images_from_page(document)  # Helper for raw image data
        if images:
            save_images(images, page_number)

        print("-" * 40)


def extract_images_from_page(document):
    """
    Extract raw images from the document if available.

    Args:
        document: The parsed document containing page content and metadata.

    Returns:
        List of numpy arrays representing images extracted from the page.
    """
    images = []

    # Check if the page contains any "/XObject" entries (PDF image resources)
    if "/Resources" in document.metadata and "/XObject" in document.metadata["/Resources"]:
        xObject = document.metadata["/Resources"]["/XObject"].get_object()

        for obj in xObject:
            if xObject[obj]["/Subtype"] == "/Image":
                # Handle different image types
                if xObject[obj]["/Filter"][1:] in _PDF_FILTER_WITHOUT_LOSS:
                    # Extract raw pixel data as numpy array
                    height, width = xObject[obj]["/Height"], xObject[obj]["/Width"]
                    img_data = np.frombuffer(xObject[obj].get_data(), dtype=np.uint8).reshape(height, width, -1)
                    images.append(img_data)

                elif xObject[obj]["/Filter"][1:] in _PDF_FILTER_WITH_LOSS:
                    # For lossy images, keep the raw bytes (e.g., JPEG, JPX)
                    img_data = xObject[obj].get_data()
                    images.append(img_data)

                else:
                    warnings.warn("Unknown PDF Filter!")

    return images



if __name__ == "__main__":
    pdf_file_path = "/home/bayu-budianto/Documents/source_doc.pdf"  # Path to the PDF file
    extract_structure_and_images(pdf_file_path)
