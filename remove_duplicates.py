#!/usr/bin/env python3
"""
Remove duplicate images from a directory using MD5 hashing.
Keeps the first occurrence (lowest numbered) and deletes the rest.
"""

import argparse
import hashlib
from collections import defaultdict
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def get_file_hash(file_path):
    """Compute MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_duplicates(images_dir):
    """
    Find duplicate images in a directory.

    Returns:
        dict: hash -> list of file paths (sorted by name)
    """
    images_dir = Path(images_dir)
    hash_to_files = defaultdict(list)

    for file_path in images_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            file_hash = get_file_hash(file_path)
            hash_to_files[file_hash].append(file_path)

    # Sort files in each group by name (to keep lowest numbered)
    for file_hash in hash_to_files:
        hash_to_files[file_hash].sort(key=lambda p: p.name)

    return hash_to_files


def remove_duplicates(images_dir, dry_run=False):
    """
    Remove duplicate images, keeping the first occurrence.

    Args:
        images_dir: Path to directory containing images
        dry_run: If True, only show what would be deleted

    Returns:
        tuple: (files_deleted, bytes_freed)
    """
    images_dir = Path(images_dir)

    if not images_dir.exists():
        raise FileNotFoundError(f"Directory not found: {images_dir}")

    if not images_dir.is_dir():
        raise NotADirectoryError(f"Not a directory: {images_dir}")

    hash_to_files = find_duplicates(images_dir)

    files_deleted = 0
    bytes_freed = 0

    for file_hash, files in hash_to_files.items():
        if len(files) > 1:
            # Keep first file, delete the rest
            kept = files[0]
            to_delete = files[1:]

            if dry_run:
                print(f"Would keep: {kept.name}")
                for f in to_delete:
                    size = f.stat().st_size
                    print(f"  Would delete: {f.name} ({size:,} bytes)")
                    files_deleted += 1
                    bytes_freed += size
            else:
                for f in to_delete:
                    size = f.stat().st_size
                    f.unlink()
                    files_deleted += 1
                    bytes_freed += size

    return files_deleted, bytes_freed


def format_size(bytes_count):
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024
    return f"{bytes_count:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Remove duplicate images from a directory using MD5 hashing"
    )
    parser.add_argument(
        "images_dir",
        help="Directory containing images to deduplicate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )

    args = parser.parse_args()

    try:
        files_deleted, bytes_freed = remove_duplicates(args.images_dir, args.dry_run)

        if args.dry_run:
            print(f"\nDry run complete: {files_deleted} duplicates found ({format_size(bytes_freed)})")
        else:
            print(f"Removed {files_deleted} duplicates, freed {format_size(bytes_freed)}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
