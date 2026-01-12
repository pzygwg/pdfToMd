# Remove Duplicates

Removes duplicate images from a directory using MD5 hashing. Useful after running `pdf_to_md.py` on PDFs with repetitive elements (logos, headers, footers).

## Usage

```bash
# Preview what will be deleted (recommended first)
python3 remove_duplicates.py <images_dir> --dry-run

# Actually delete duplicates
python3 remove_duplicates.py <images_dir>
```

## Example

```bash
# Check duplicates in SGBD_images folder
python3 remove_duplicates.py output/SGBD_images --dry-run

# Remove them
python3 remove_duplicates.py output/SGBD_images
```

## How it works

1. Computes MD5 hash for each image
2. Groups identical images together
3. Keeps the lowest-numbered file (e.g., `image_001.jpg`)
4. Deletes the rest

## Note

This only deletes image files. If you're using the markdown output, image references to deleted files will be broken. You can either:
- Manually fix them
- Re-run `pdf_to_md.py` with duplicates removed upstream
- Ignore broken refs (most viewers just show a placeholder)
