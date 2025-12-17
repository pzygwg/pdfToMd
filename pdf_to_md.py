#!/usr/bin/env python3
"""
PDF to Markdown converter with image extraction and table support.
Converts PDF files to Markdown, extracting images, tables, and text at their correct positions.
Images are compressed and resized for optimal LLM consumption.
"""

import argparse
import io
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from PIL import Image


def compress_image(image_bytes, max_width=800, quality=70):
    """
    Compress and resize an image for LLM consumption.

    Args:
        image_bytes: Raw image bytes
        max_width: Maximum width in pixels (height scales proportionally)
        quality: JPEG quality (1-100)

    Returns:
        tuple: (compressed_bytes, extension)
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Convert RGBA/P to RGB for JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize if larger than max_width
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    # Save as JPEG
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=quality, optimize=True)
    output.seek(0)

    return output.read(), "jpg"


def table_to_markdown(table):
    """
    Convert a pdfplumber table to markdown format.

    Args:
        table: List of rows, each row is a list of cell values

    Returns:
        str: Markdown table string
    """
    if not table or len(table) < 1:
        return ""

    # Clean up cells (replace None with empty string, strip whitespace)
    cleaned = []
    for row in table:
        cleaned_row = []
        for cell in row:
            if cell is None:
                cleaned_row.append("")
            else:
                # Replace newlines with spaces, strip whitespace
                cleaned_row.append(str(cell).replace("\n", " ").strip())
        cleaned.append(cleaned_row)

    # Ensure all rows have same number of columns
    max_cols = max(len(row) for row in cleaned)
    for row in cleaned:
        while len(row) < max_cols:
            row.append("")

    if not cleaned:
        return ""

    # Build markdown table
    lines = []

    # Header row
    header = cleaned[0]
    lines.append("| " + " | ".join(header) + " |")

    # Separator row
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # Data rows
    for row in cleaned[1:]:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def extract_tables_from_page(plumber_page):
    """
    Extract tables from a pdfplumber page.

    Returns:
        list of tuples: (y_position, markdown_table, bbox)
    """
    tables = []

    # Find tables on the page
    found_tables = plumber_page.find_tables()

    for table in found_tables:
        # Get table bounding box (x0, y0, x1, y1)
        bbox = table.bbox
        y_pos = bbox[1]  # Top of table

        # Extract table data
        table_data = table.extract()

        # Convert to markdown
        md_table = table_to_markdown(table_data)

        if md_table:
            tables.append((y_pos, md_table, bbox))

    return tables


def is_in_table_region(y_pos, table_bboxes, margin=5):
    """
    Check if a y position falls within any table region.

    Args:
        y_pos: Y coordinate to check
        table_bboxes: List of table bounding boxes (x0, y0, x1, y1)
        margin: Extra margin around tables

    Returns:
        bool: True if position is within a table region
    """
    for bbox in table_bboxes:
        if bbox[1] - margin <= y_pos <= bbox[3] + margin:
            return True
    return False


def extract_images_from_page(page, doc, images_dir, image_counter, table_bboxes, max_width=800, quality=70, no_compress=False):
    """
    Extract images from a PDF page and save them to the images directory.

    Returns:
        list of tuples: (y_position, markdown_image_string, image_counter)
    """
    images = []
    image_list = page.get_images(full=True)

    for img_index, img_info in enumerate(image_list):
        xref = img_info[0]

        # Get image position on page
        img_rects = page.get_image_rects(xref)
        if not img_rects:
            continue

        # Use the first rectangle for positioning
        rect = img_rects[0]
        y_pos = rect.y0  # Top of the image

        # Skip images inside table regions
        if is_in_table_region(y_pos, table_bboxes):
            continue

        # Extract image data
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]

        # Compress unless disabled
        if not no_compress:
            image_bytes, image_ext = compress_image(image_bytes, max_width, quality)

        # Save image
        image_filename = f"image_{image_counter:03d}.{image_ext}"
        image_path = images_dir / image_filename

        with open(image_path, "wb") as img_file:
            img_file.write(image_bytes)

        # Create markdown reference (relative path)
        relative_path = f"{images_dir.name}/{image_filename}"
        md_image = f"\n![image]({relative_path})\n"

        images.append((y_pos, md_image))
        image_counter += 1

    return images, image_counter


def extract_text_blocks_from_page(page, table_bboxes):
    """
    Extract text blocks from a PDF page with position and formatting info.
    Skips text that falls within table regions.

    Returns:
        list of tuples: (y_position, markdown_text)
    """
    blocks = []

    # Get page text as dictionary for detailed info
    text_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

    # Collect font sizes to determine what might be a heading
    font_sizes = []
    for block in text_dict.get("blocks", []):
        if block.get("type") == 0:  # Text block
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        font_sizes.append(span.get("size", 12))

    # Calculate thresholds for headings
    if font_sizes:
        avg_size = sum(font_sizes) / len(font_sizes)
        max_size = max(font_sizes)
    else:
        avg_size = 12
        max_size = 12

    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:  # Skip non-text blocks
            continue

        bbox = block.get("bbox", [0, 0, 0, 0])
        y_pos = bbox[1]  # Top of block

        # Skip text blocks that are inside table regions
        block_center_y = (bbox[1] + bbox[3]) / 2
        if is_in_table_region(block_center_y, table_bboxes):
            continue

        block_text = []
        block_max_size = 0
        is_bold = False

        for line in block.get("lines", []):
            line_text = []
            for span in line.get("spans", []):
                text = span.get("text", "")
                if text.strip():
                    line_text.append(text)
                    size = span.get("size", 12)
                    if size > block_max_size:
                        block_max_size = size
                    # Check for bold
                    flags = span.get("flags", 0)
                    if flags & 2 ** 4:  # Bold flag
                        is_bold = True

            if line_text:
                block_text.append("".join(line_text))

        if not block_text:
            continue

        text = "\n".join(block_text).strip()
        if not text:
            continue

        # Determine if this is a heading based on font size
        md_text = text
        if block_max_size >= max_size * 0.95 and max_size > avg_size * 1.2:
            # Likely a main heading
            md_text = f"# {text}"
        elif block_max_size > avg_size * 1.15 or (is_bold and len(text) < 100):
            # Likely a subheading
            if block_max_size > avg_size * 1.3:
                md_text = f"## {text}"
            else:
                md_text = f"### {text}"

        blocks.append((y_pos, md_text))

    return blocks


def convert_page_to_markdown(fitz_page, plumber_page, doc, images_dir, image_counter, max_width=800, quality=70, no_compress=False):
    """
    Convert a single PDF page to markdown.

    Returns:
        tuple: (markdown_string, updated_image_counter)
    """
    # Extract tables first (to get their bounding boxes)
    table_results = extract_tables_from_page(plumber_page)
    table_bboxes = [t[2] for t in table_results]
    table_blocks = [(t[0], t[1]) for t in table_results]

    # Extract text (excluding table regions)
    text_blocks = extract_text_blocks_from_page(fitz_page, table_bboxes)

    # Extract images (excluding table regions)
    image_blocks, image_counter = extract_images_from_page(
        fitz_page, doc, images_dir, image_counter, table_bboxes, max_width, quality, no_compress
    )

    # Merge all blocks and sort by vertical position
    all_blocks = text_blocks + image_blocks + table_blocks
    all_blocks.sort(key=lambda x: x[0])

    # Build markdown
    md_parts = [block[1] for block in all_blocks]

    return "\n\n".join(md_parts), image_counter


def convert_pdf_to_markdown(pdf_path, output_dir=None, max_width=800, quality=70, no_compress=False):
    """
    Convert a PDF file to Markdown with extracted images and tables.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Output directory (default: ./output/)
        max_width: Maximum image width in pixels
        quality: JPEG quality (1-100)
        no_compress: If True, keep original images without compression

    Returns:
        tuple: (markdown_file_path, images_dir_path)
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Set up output directory
    if output_dir is None:
        output_dir = Path("output")
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Create images directory
    pdf_name = pdf_path.stem
    images_dir = output_dir / f"{pdf_name}_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF with both libraries
    fitz_doc = fitz.open(pdf_path)
    plumber_doc = pdfplumber.open(pdf_path)

    markdown_parts = []
    image_counter = 1

    for page_num in range(len(fitz_doc)):
        fitz_page = fitz_doc[page_num]
        plumber_page = plumber_doc.pages[page_num]

        # Add page separator for multi-page documents
        if page_num > 0:
            markdown_parts.append("\n---\n")

        page_md, image_counter = convert_page_to_markdown(
            fitz_page, plumber_page, fitz_doc, images_dir, image_counter, max_width, quality, no_compress
        )
        markdown_parts.append(page_md)

    fitz_doc.close()
    plumber_doc.close()

    # Write markdown file
    md_path = output_dir / f"{pdf_name}.md"
    full_markdown = "\n".join(markdown_parts)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_markdown)

    # Clean up empty images directory
    if not any(images_dir.iterdir()):
        images_dir.rmdir()
        images_dir = None

    return md_path, images_dir


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF to Markdown with image extraction and table support (optimized for LLM consumption)"
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to convert"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (default: ./output/)",
        default=None
    )
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=70,
        help="JPEG quality 1-100 (default: 70)"
    )
    parser.add_argument(
        "-w", "--max-width",
        type=int,
        default=800,
        help="Maximum image width in pixels (default: 800)"
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Keep original images without compression"
    )

    args = parser.parse_args()

    try:
        md_path, images_dir = convert_pdf_to_markdown(
            args.pdf_path,
            args.output,
            args.max_width,
            args.quality,
            args.no_compress
        )
        print(f"Markdown file created: {md_path}")
        if images_dir:
            print(f"Images extracted to: {images_dir}")
        else:
            print("No images found in PDF")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
