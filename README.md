# PDF to Markdown Converter

Convert heavy PDF files to lightweight Markdown with compressed images — optimized for feeding to LLMs.

## Why?

PDFs are often too large to give directly to LLMs, especially when they contain high-resolution images. This tool:

1. Extracts text from PDFs into clean Markdown
2. Extracts images and compresses them (resized + JPEG conversion)
3. Places images at their correct positions in the document

The result: a small `.md` file + a folder of compressed images that you can easily feed to any multimodal LLM.

## Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic conversion

```bash
python pdf_to_md.py document.pdf
```

Output:
```
output/
├── document.md              # Markdown text
└── document_images/         # Compressed images
    ├── image_001.jpg
    ├── image_002.jpg
    └── ...
```

### Image compression options

Images are compressed by default (800px max width, 70% JPEG quality).

```bash
# Default settings (good balance)
python pdf_to_md.py document.pdf

# Higher quality for detailed diagrams
python pdf_to_md.py document.pdf -q 85 -w 1000

# Aggressive compression for smaller files
python pdf_to_md.py document.pdf -q 50 -w 600

# Keep original images (no compression)
python pdf_to_md.py document.pdf --no-compress
```

Options:
- `-q, --quality` — JPEG quality 1-100 (default: 70)
- `-w, --max-width` — Max image width in pixels (default: 800)
- `-o, --output` — Output directory (default: ./output/)
- `--no-compress` — Skip compression, keep original images

### Expected size reduction

A 4MB PDF with high-res images typically becomes:
- ~10-50KB markdown file
- ~200-500KB total for all images (with default settings)

## Using with LLMs

1. **Run the converter** on your PDF
2. **Upload the markdown** as text context
3. **Attach the images** from the `_images/` folder

Most LLM interfaces (Claude, ChatGPT) let you upload images separately. The markdown references them by filename, so the LLM can understand which image goes where.

Example markdown output:
```markdown
# Chapter 1: Introduction

This diagram shows the system architecture:

![image](document_images/image_001.jpg)

As you can see, the components are organized in layers...
```

## Optional: Convert to HTML

If you need a single portable file (e.g., for sharing), you can convert the markdown to self-contained HTML with embedded images:

```bash
python md_to_html.py output/document.md
```

This embeds images as base64 directly in the HTML. Note: this increases file size (~33% larger than separate files), so it's not recommended for LLM use.

## Features

- Extracts text preserving reading order
- Detects headings based on font size
- Places images at their correct positions
- Compresses images for LLM-friendly sizes
- Adds page separators (`---`) for multi-page PDFs
