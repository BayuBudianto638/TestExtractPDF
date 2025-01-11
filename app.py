from flask import Flask, request, jsonify
import pdfplumber
import numpy as np
import warnings
import os
from typing import Any, Iterator, Mapping, Optional

_PDF_FILTER_WITH_LOSS = ["DCTDecode", "DCT", "JPXDecode"]
_PDF_FILTER_WITHOUT_LOSS = [
    "LZWDecode",
    "LZW",
    "FlateDecode",
    "Fl",
    "ASCII85Decode",
    "A85",
    "ASCIIHexDecode",
    "AHx",
    "RunLengthDecode",
    "RL",
    "CCITTFaxDecode",
    "CCF",
    "JBIG2Decode",
]


# Placeholder function for image text extraction
def extract_from_images_with_rapidocr(images):
    # Implement your image text extraction logic here
    return "Extracted text from images."


class Blob:
    def __init__(self, source):
        self.source = source

    def as_bytes_io(self):
        import io
        with open(self.source, 'rb') as f:
            return io.BytesIO(f.read())


class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata


class BaseBlobParser:
    def lazy_parse(self, blob):
        raise NotImplementedError


class PDFPlumberParser(BaseBlobParser):
    """Parse `PDF` with `PDFPlumber`."""

    def __init__(
            self,
            text_kwargs: Optional[Mapping[str, Any]] = None,
            dedupe: bool = False,
            extract_images: bool = False,
            image_output_dir: str = 'extracted_images'
    ) -> None:
        """Initialize the parser.

        Args:
            text_kwargs: Keyword arguments to pass to ``pdfplumber.Page.extract_text()``
            dedupe: Avoiding the error of duplicate characters if `dedupe=True`.
            image_output_dir: Directory to save extracted images.
        """
        self.text_kwargs = text_kwargs or {}
        self.dedupe = dedupe
        self.extract_images = extract_images
        self.image_output_dir = image_output_dir

        if self.extract_images:
            os.makedirs(self.image_output_dir, exist_ok=True)

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:  # type: ignore[valid-type]
        """Lazily parse the blob."""
        import pdfplumber

        with blob.as_bytes_io() as file_path:  # type: ignore[attr-defined]
            doc = pdfplumber.open(file_path)  # open document

            yield from [
                Document(
                    page_content=self._process_page_content(page),
                    metadata=dict(
                        {
                            "source": blob.source,  # type: ignore[attr-defined]
                            "file_path": blob.source,  # type: ignore[attr-defined]
                            "page": page.page_number - 1,
                            "total_pages": len(doc.pages),
                            "chapter": self._extract_chapter_from_page(page),
                            "subsection": self._extract_subsection_from_page(page),
                            "images": self._extract_images_from_page(page, page.page_number - 1),
                        },
                        **{
                            k: doc.metadata[k]
                            for k in doc.metadata
                            if type(doc.metadata[k]) in [str, int]
                        },
                    ),
                )
                for page in doc.pages
            ]

    def _process_page_content(self, page: pdfplumber.page.Page) -> str:
        """Process the page content based on dedupe."""
        if self.dedupe:
            return page.dedupe_chars().extract_text(**self.text_kwargs)
        return page.extract_text(**self.text_kwargs)

    def _extract_chapter_from_page(self, page: pdfplumber.page.Page) -> str:
        """Extract chapter title from the page."""
        text = self._process_page_content(page)
        for line in text.splitlines():
            if line.isupper():
                return line
        return ""

    def _extract_subsection_from_page(self, page: pdfplumber.page.Page) -> str:
        """Extract subsection title from the page."""
        text = self._process_page_content(page)
        for line in text.splitlines():
            if line.startswith("Section"):
                return line
        return ""

    def _extract_images_from_page(self, page: pdfplumber.page.Page, page_number: int) -> list:
        """Extract images from page, save to files, and return list of image file paths."""
        if not self.extract_images:
            return []

        images = []
        image_files = []
        for idx, img in enumerate(page.images):
            if img["stream"]["Filter"].name in _PDF_FILTER_WITHOUT_LOSS:
                image_data = np.frombuffer(img["stream"].get_data(), dtype=np.uint8).reshape(
                    img["stream"]["Height"], img["stream"]["Width"], -1
                )
                image_path = os.path.join(self.image_output_dir, f'page_{page_number}_img_{idx}.png')
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                image_files.append(image_path)
            elif img["stream"]["Filter"].name in _PDF_FILTER_WITH_LOSS:
                image_path = os.path.join(self.image_output_dir, f'page_{page_number}_img_{idx}.jpg')
                with open(image_path, 'wb') as f:
                    f.write(img["stream"].get_data())
                image_files.append(image_path)
            else:
                warnings.warn("Unknown PDF Filter!")

        return image_files


app = Flask(__name__)


@app.route('/parse_pdf', methods=['POST'])
def parse_pdf():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected for uploading", 400

    file.save(file.filename)
    pdf_blob = Blob(file.filename)

    pdf_parser = PDFPlumberParser(dedupe=True, extract_images=True)
    results = []
    all_image_files = []
    for document in pdf_parser.lazy_parse(pdf_blob):
        results.append({
            "page_content": document.page_content,
            "metadata": document.metadata
        })
        all_image_files.extend(document.metadata["images"])

    os.remove(file.filename)  # Clean up the uploaded file

    return jsonify({
        "results": results,
        "all_image_files": all_image_files
    })


if __name__ == "__main__":
    app.run(debug=True)
