import os
import fitz  # pymupdf


def valid_pdf(path):
    """
    Check whether a file is a valid readable PDF.
    """
    if not os.path.exists(path):
        return False

    # small files are almost always HTML error pages
    if os.path.getsize(path) < 5000:
        return False

    try:
        doc = fitz.open(path)
        doc.close()
        return True
    except Exception:
        return False
