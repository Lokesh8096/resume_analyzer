import pdfplumber

def extract_text_from_pdf(pdf_file) -> str:
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()
