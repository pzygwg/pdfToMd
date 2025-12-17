#!/usr/bin/env python3
"""
Markdown to HTML converter with embedded images.
Converts Markdown files to self-contained HTML with base64-encoded images.
"""

import argparse
import base64
import mimetypes
import re
from pathlib import Path

import markdown


def image_to_base64(image_path):
    """
    Read an image file and convert it to a base64 data URI.

    Args:
        image_path: Path to the image file

    Returns:
        str: Data URI string (e.g., "data:image/png;base64,...")
    """
    image_path = Path(image_path)

    if not image_path.exists():
        print(f"Warning: Image not found: {image_path}")
        return None

    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if mime_type is None:
        # Default to png if unknown
        mime_type = "image/png"

    # Read and encode
    with open(image_path, "rb") as f:
        image_data = f.read()

    base64_data = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{base64_data}"


def embed_images(md_content, base_dir):
    """
    Find all image references in markdown and replace with base64 data URIs.

    Args:
        md_content: Markdown content string
        base_dir: Base directory for resolving relative image paths

    Returns:
        str: Markdown content with embedded images
    """
    base_dir = Path(base_dir)

    # Pattern to match markdown images: ![alt](path)
    image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)

        # Skip if already a data URI or URL
        if image_path.startswith(("data:", "http://", "https://")):
            return match.group(0)

        # Resolve relative path
        full_path = base_dir / image_path

        # Convert to base64
        data_uri = image_to_base64(full_path)

        if data_uri:
            return f"![{alt_text}]({data_uri})"
        else:
            # Keep original if conversion failed
            return match.group(0)

    return re.sub(image_pattern, replace_image, md_content)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1rem 0;
        }}
        h1, h2, h3 {{
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2rem 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
        }}
        pre {{
            background: #f4f4f4;
            padding: 1rem;
            overflow-x: auto;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


def convert_md_to_html(md_path, output_path=None):
    """
    Convert a Markdown file to self-contained HTML with embedded images.

    Args:
        md_path: Path to the Markdown file
        output_path: Output HTML path (default: same name with .html extension)

    Returns:
        Path: Path to the created HTML file
    """
    md_path = Path(md_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    # Set default output path
    if output_path is None:
        output_path = md_path.with_suffix(".html")
    else:
        output_path = Path(output_path)

    # Read markdown content
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Embed images as base64
    md_content = embed_images(md_content, md_path.parent)

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=["fenced_code", "tables"])

    # Wrap in HTML template
    title = md_path.stem.replace("_", " ").replace("-", " ").title()
    full_html = HTML_TEMPLATE.format(title=title, content=html_content)

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to self-contained HTML with embedded images"
    )
    parser.add_argument(
        "md_path",
        help="Path to the Markdown file to convert"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file path (default: same name with .html extension)",
        default=None
    )

    args = parser.parse_args()

    try:
        html_path = convert_md_to_html(args.md_path, args.output)
        print(f"HTML file created: {html_path}")
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
