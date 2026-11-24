"""
Phase 4 - PDF Extraction Tests
Tests:
- Streaming download with size capping and signature verification
- Extraction of valid text-layer PDFs
- Detection of scanned / image-only / empty PDFs
- Graceful handling of corrupted / non-PDF byte streams
- Abstract fallback when PDF is missing or unreachable
- Sentence-aware truncation to MAX_TEXT_LENGTH
- Batch concurrent extraction
"""

import io
import sys
import os
import pypdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.pdf_extractor import (
    download_pdf_bytes,
    extract_text_from_pdf_bytes,
    extract_paper_content,
    batch_extract_papers
)

passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name} - {detail}")
        failed += 1

print("=" * 60)
print("  ResearchGap AI - Phase 4 PDF Extraction Tests")
print("=" * 60)

# -----------------------------------------------------------------------------
# 1. Download Validation & Signature Verification
# -----------------------------------------------------------------------------
print("\n--- 1. Download Validation & Header Checks ---")
bytes_none, msg = download_pdf_bytes("not_a_url")
test("Rejects malformed URL", bytes_none is None)

bytes_none, msg = download_pdf_bytes("https://example.com/not-a-pdf")
# example.com returns HTML, not PDF
test("Rejects non-PDF URL returning HTML", bytes_none is None)

# -----------------------------------------------------------------------------
# 2. Corrupt / Empty PDF Byte Handling
# -----------------------------------------------------------------------------
print("\n--- 2. Corrupt / Empty PDF Stream Handling ---")
res_empty = extract_text_from_pdf_bytes(b"")
test("Handles empty byte stream", res_empty["status"] == "error")

res_corrupt = extract_text_from_pdf_bytes(b"This is not a PDF at all")
test("Handles corrupt byte stream without crashing", res_corrupt["status"] in ["corrupt", "error"])

# -----------------------------------------------------------------------------
# 3. Scanned / Image-Only PDF Detection
# -----------------------------------------------------------------------------
print("\n--- 3. Scanned / Image-Only PDF Detection ---")
# Generate a blank 1-page PDF using PyPDF
writer = pypdf.PdfWriter()
writer.add_blank_page(width=612, height=792)
blank_pdf_stream = io.BytesIO()
writer.write(blank_pdf_stream)
blank_pdf_bytes = blank_pdf_stream.getvalue()

res_blank = extract_text_from_pdf_bytes(blank_pdf_bytes)
test("Reports page count of 1", res_blank["page_count"] == 1)
test("Identifies scanned/image/empty PDF without text", res_blank["is_scanned_or_image"] is True)
test("Reports status as scanned", res_blank["status"] == "scanned")
test("Contains informative message without claiming OCR", "OCR not configured" in res_blank["message"])

# -----------------------------------------------------------------------------
# 4. Fallback Handling in extract_paper_content
# -----------------------------------------------------------------------------
print("\n--- 4. Abstract Fallback Handling ---")
paper_no_pdf = {
    "title": "A Theoretical Paper Without PDF",
    "abstract": "This is the paper abstract describing federated learning protocols.",
    "pdf_url": "",
    "doi": "10.1000/1"
}
res_fallback = extract_paper_content(paper_no_pdf)
test("Preserves original metadata", res_fallback["title"] == paper_no_pdf["title"])
test("Content matches abstract when no PDF provided", res_fallback["content_for_analysis"] == paper_no_pdf["abstract"])
test("Extraction info reports abstract source", res_fallback["extraction_info"]["content_source"] == "abstract")

paper_broken_pdf = {
    "title": "A Paper With Dead Link",
    "abstract": "This abstract is the fallback text.",
    "pdf_url": "https://example.com/dead_link.pdf",
    "doi": "10.1000/2"
}
res_broken = extract_paper_content(paper_broken_pdf)
test("Falls back to abstract on dead link", res_broken["content_for_analysis"] == paper_broken_pdf["abstract"])
test("Records download failure in extraction_info", "failed" in res_broken["extraction_info"]["message"].lower())

# -----------------------------------------------------------------------------
# 5. Live PDF Download & Text Extraction (arXiv)
# -----------------------------------------------------------------------------
print("\n--- 5. Live PDF Download & Full Extraction ---")
# Use a lightweight stable arXiv paper: https://arxiv.org/pdf/2306.14753v1.pdf
live_paper = {
    "title": "Deep Polynomial Chaos Neural Network",
    "abstract": "Artificial Intelligence and Machine learning have been widely used in various fields.",
    "pdf_url": "https://arxiv.org/pdf/2306.14753v1.pdf",
    "doi": ""
}
extracted_live = extract_paper_content(live_paper, max_length=5000)
test("Live PDF downloaded and extracted", extracted_live["extraction_info"]["content_source"] == "pdf_text")
test("Extracted text exceeds 500 characters", len(extracted_live["pdf_text"]) > 500)
test("Content for analysis is populated", len(extracted_live["content_for_analysis"]) > 0)
test("Strictly honors max_length limit", len(extracted_live["content_for_analysis"]) <= 5050) # allowance for truncation note
print(f"    Extracted {len(extracted_live['pdf_text'])} chars from live PDF.")

# -----------------------------------------------------------------------------
# 6. Batch Concurrent Extraction
# -----------------------------------------------------------------------------
print("\n--- 6. Batch Concurrent Extraction ---")
test_batch = [
    live_paper,
    paper_no_pdf,
    paper_broken_pdf
]
batch_results = batch_extract_papers(test_batch, max_to_extract=2, max_workers=2)
test("Batch preserves list length", len(batch_results) == 3)
test("All items have 'content_for_analysis'", all("content_for_analysis" in p for p in batch_results))

# Summary
print("\n" + "=" * 60)
print(f"  Results: {passed} passed, {failed} failed, {passed + failed} total")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("  🎉 All Phase 4 PDF Extraction tests passed!")
