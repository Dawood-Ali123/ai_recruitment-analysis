import pymupdf
#fitz pyMupdf libraray ko import krtaha is ka name python me fitz ha
from docx import Document
from pathlib import Path
import re
def extract_pdf_text(file_path:str)->str:
    text=""

    with pymupdf.open(file_path) as pdf:
        for page in pdf :
            page_text=page.get_text()
            text+=page_text+"\n"

    return text.strip()

def extract_docx_text(file_path: str) -> str:
    document = Document(file_path)

    text = []

# Extract paragraphs
    for paragraph in document.paragraphs:

        if paragraph.text.strip():

            text.append(paragraph.text)

# Extract tables
    for table in document.tables:

        for row in table.rows:

            row_text = []

            for cell in row.cells:

                cell_text = cell.text.strip()

                if cell_text:

                    row_text.append(cell_text)

            if row_text:

                text.append(" | ".join(row_text))

    return "\n".join(text).strip()

def clean_cv_text(text:str)->str:
    text=re.sub(r"[ \t]+"," ",text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    return text.strip()


#har pdf sae text extract nahi hota kunkay kuch images scanned PDF Detection implement krti ha
def validate_extracted_text(text:str)->str:
    if not text or not text.strip():
        raise ValueError(
            "No text is found the document may be scanned or empty"
        )
    if len(text.strip())<50:
        raise ValueError(
            "Very little text extracted from CV. Manual review required"
        )
    return text


#now  we make a function jo in tamam functions ko combine kr klay complete CV extraction pipeline banaya ga
def extract_cv_text(file_path:str)->str:
    file_extension=Path(file_path).suffix.lower()
    if file_extension==".pdf":
        text=extract_pdf_text(file_path)

    elif file_extension==".docx":
        text=extract_docx_text(file_path)
    else:
        raise ValueError("Unsupported CV file format")
    text=clean_cv_text(text)
    text=validate_extracted_text(text)
    return text

