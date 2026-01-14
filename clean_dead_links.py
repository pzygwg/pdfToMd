#!/usr/bin/env python3
"""
Remove image references from markdown files when the image file doesn't exist.
"""

import argparse
import re
from pathlib import Path


def clean_dead_links(md_path, dry_run=False):
    """
    Remove image references pointing to non-existent files.

    Args:
        md_path: Path to markdown file
        dry_run: If True, only show what would be removed

    Returns:
        int: Number of dead links removed
    """
    md_path = Path(md_path)

    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    md_dir = md_path.parent

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match markdown image syntax: ![alt](path)
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')

    dead_links = []

    for match in image_pattern.finditer(content):
        img_path = match.group(2)
        full_path = md_dir / img_path

        if not full_path.exists():
            dead_links.append((match.group(0), img_path))

    if dry_run:
        for link, path in dead_links:
            print(f"Would remove: {path}")
        print(f"\nDry run: {len(dead_links)} dead links found")
        return len(dead_links)

    # Remove dead links (and surrounding newlines to avoid empty gaps)
    new_content = content
    for link, path in dead_links:
        # Remove the image line and one trailing newline
        new_content = new_content.replace(f"\n{link}\n", "\n")
        new_content = new_content.replace(link, "")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Removed {len(dead_links)} dead image links")
    return len(dead_links)


def main():
    parser = argparse.ArgumentParser(
        description="Remove dead image links from markdown files"
    )
    parser.add_argument(
        "md_path",
        help="Path to markdown file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without modifying the file"
    )

    args = parser.parse_args()

    try:
        clean_dead_links(args.md_path, args.dry_run)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
