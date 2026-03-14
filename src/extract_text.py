import sys
import fitz  # pymupdf

# best sections to scan for instrument detection
# - Observations
# - Observations and Data Reduction
# - Instrumentation
# - Data


def extract_block_text(pdf_file):
    '''
    Improves
    - keyword detection
    - embeddings
    - transformer classification
    '''
    doc = fitz.open(pdf_file)
    pages = []

    for page in doc:
        # block method is layout driven 
        # ApJ, AJ, MNRAS, A&A, etc. journals sometimes shift column widths or places figures across both columns
        # figures or wide equations will still disrupt the order, but mostly preserves
        # readable sentences so telescope and instrument mentions may still be detected
        blocks = page.get_text("blocks")
        blocks = [b for b in blocks if b[4].strip()]
        # filter out non-text blocks to avoid blank junk
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))
        text = "\n".join(b[4] for b in blocks)
        pages.append(text)

    doc.close()
    return "\n".join(pages)


def extract_two_column_text(pdf_file):
    '''
    '''
    doc = fitz.open(pdf_file)
    pages = []

    for page in doc:
        # most arxivs are single column
        #if rect.width > 500:
            #two_column = True   # ??? False ???

        # split-column method (astronomy journals)
        rect = page.rect
        mid_x = rect.width / 2

        left = fitz.Rect(0, 0, mid_x, rect.height)
        right = fitz.Rect(mid_x, 0, rect.width, rect.height)

        left_text = page.get_text("text", clip=left)
        right_text = page.get_text("text", clip=right)

        pages.append(left_text)
        pages.append(right_text)

    doc.close()
    return "\n".join(pages)


if __name__ == "__main__":
    #pdf = "data/pdf/1998AJ....116.1009R.pdf"
    pdf = sys.argv[1] if len(sys.argv) > 1 else "data/pdf/1998AJ....116.1009R.pdf"
    #full_text = extract_two_column_text(pdf)
    text = extract_block_text(pdf)
    print(text[:2000])  # preview

