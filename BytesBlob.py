from io import BytesIO
from pathlib import Path
from pdf import PyPDFParser  # Assuming pdf.py contains this class


class BytesBlob:
    def __init__(self, data: bytes, source: str = None):
        self.data = data
        self.source = source

    def as_bytes_io(self):
        """Return a BytesIO object for the data."""
        return BytesIO(self.data)
