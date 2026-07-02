import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Opens a PDF and extracts text page by page.
    Returns a list of dicts: [{"page_number": 1, "text": "..."}, ...]
    """
    doc = fitz.open(file_path)
    pages = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()

        # Skip empty pages (e.g. pages with only images, no extractable text)
        if text.strip():
            pages.append({
                "page_number": page_number + 1,  # human-friendly, starts at 1 not 0
                "text": text
            })

    doc.close()
    return pages


def chunk_pages(pages: list[dict], chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    """
    Takes extracted pages and splits each page's text into smaller chunks.
    Returns a list of dicts: [{"text": "...", "page_number": 1, "chunk_index": 0}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks = []
    chunk_index = 0

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_text in page_chunks:
            all_chunks.append({
                "text": chunk_text,
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })
            chunk_index += 1

    return all_chunks


def process_pdf(file_path: str) -> list[dict]:
    """
    Full pipeline: PDF file path -> extracted, chunked text ready for embedding.
    """
    pages = extract_text_from_pdf(file_path)
    chunks = chunk_pages(pages)
    return chunks