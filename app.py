import os
import fitz  # PyMuPDF
from langchain_community.document_loaders import PyPDFLoader
# Run the asynchronous function
import asyncio


def save_images(fitz_document, fitz_page, page_number):
    images = fitz_page.get_images(full=True)
    if not os.path.exists('images'):
        os.makedirs('images')
    for i, img in enumerate(images):
        xref = img[0]
        base_image = fitz_document.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        with open(f'images/page_{page_number}_image_{i}.{image_ext}', "wb") as image_file:
            image_file.write(image_bytes)


def save_text(text, page_number):
    if not os.path.exists('texts'):
        os.makedirs('texts')
    with open(f'texts/page_{page_number}.txt', 'w', encoding='utf-8') as f:
        f.write(text)


async def extract_images_and_text(pdf_path):
    loader = PyPDFLoader(pdf_path)

    fitz_document = fitz.open(pdf_path)

    page_number = 0
    async for page in loader.alazy_load():
        page_number += 1

        # Extract and save images using PyMuPDF
        fitz_page = fitz_document.load_page(page_number - 1)
        save_images(fitz_document, fitz_page, page_number)

        # Extract and save text using PyPDFLoader
        text = page.page_content
        save_text(text, page_number)

    print("Extraction complete.")


# Replace with the path to your PDF file
pdf_path = "/home/bayu-budianto/Documents/source_doc.pdf"
asyncio.run(extract_images_and_text(pdf_path))
