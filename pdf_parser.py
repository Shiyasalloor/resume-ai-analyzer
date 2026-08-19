import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from an uploaded PDF resume.
    """

    pdf_bytes = uploaded_file.getvalue()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()
        text += "\n"

    document.close()

    return text.strip()