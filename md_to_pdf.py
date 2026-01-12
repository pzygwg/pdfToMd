#!/usr/bin/env python3
"""
Markdown to PDF converter with syntax highlighting and beautiful styling.
Inspired by Zed editor's markdown preview.
"""

import argparse
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from weasyprint import HTML, CSS
from pygments.formatters import HtmlFormatter
import os

# CSS styling - Compact light theme
CSS_STYLE = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-color: #ffffff;
    --text-color: #1f2937;
    --heading-color: #111827;
    --link-color: #2563eb;
    --code-bg: #f8fafc;
    --code-border: #e2e8f0;
    --table-border: #d1d5db;
    --table-header-bg: #f3f4f6;
    --blockquote-border: #3b82f6;
    --blockquote-bg: #f0f9ff;
}

* {
    box-sizing: border-box;
}

@page {
    size: A4;
    margin: 1cm 1.2cm;

    @bottom-center {
        content: counter(page);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 8pt;
        color: #9ca3af;
    }
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 9pt;
    line-height: 1.45;
    color: var(--text-color);
    background-color: var(--bg-color);
    max-width: 100%;
    margin: 0;
    padding: 0;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--heading-color);
    margin-top: 1em;
    margin-bottom: 0.3em;
    font-weight: 600;
    line-height: 1.2;
    page-break-after: avoid;
}

h1 {
    font-size: 16pt;
    font-weight: 700;
    border-bottom: 1.5px solid #d1d5db;
    padding-bottom: 0.2em;
    margin-top: 0;
}

h2 {
    font-size: 12pt;
    font-weight: 600;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0.15em;
}

h3 {
    font-size: 10pt;
    font-weight: 600;
}

h4 {
    font-size: 9pt;
    font-weight: 600;
}

/* Paragraphs */
p {
    margin: 0.4em 0;
    orphans: 3;
    widows: 3;
}

/* Links */
a {
    color: var(--link-color);
    text-decoration: none;
}

/* Code - Inline */
code {
    font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 0.85em;
    background-color: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 3px;
    padding: 0.1em 0.3em;
    color: #be185d;
}

/* Code - Block */
pre {
    font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 7.5pt;
    line-height: 1.4;
    background-color: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 5px;
    padding: 0.6em 0.8em;
    overflow-x: auto;
    margin: 0.5em 0;
    page-break-inside: avoid;
}

pre code {
    background: none;
    border: none;
    padding: 0;
    color: #1f2937;
    font-size: inherit;
}

/* Syntax highlighting - Light theme (IntelliJ/VS Code inspired) */
.codehilite {
    background-color: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 5px;
    padding: 0.6em 0.8em;
    margin: 0.5em 0;
    overflow-x: auto;
    page-break-inside: avoid;
}

.codehilite pre {
    margin: 0;
    padding: 0;
    background: none;
    border: none;
}

.codehilite code {
    color: #1f2937;
}

/* Pygments syntax colors - Light theme */
.codehilite .hll { background-color: #ffffcc }
.codehilite .c { color: #6b7280; font-style: italic } /* Comment */
.codehilite .k { color: #7c3aed; font-weight: 500 } /* Keyword */
.codehilite .o { color: #1f2937 } /* Operator */
.codehilite .p { color: #1f2937 } /* Punctuation */
.codehilite .cm { color: #6b7280; font-style: italic } /* Comment.Multiline */
.codehilite .cp { color: #b45309 } /* Comment.Preproc */
.codehilite .c1 { color: #6b7280; font-style: italic } /* Comment.Single */
.codehilite .cs { color: #6b7280; font-style: italic } /* Comment.Special */
.codehilite .gd { color: #dc2626 } /* Generic.Deleted */
.codehilite .ge { font-style: italic } /* Generic.Emph */
.codehilite .gi { color: #16a34a } /* Generic.Inserted */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #0891b2 } /* Generic.Subheading */
.codehilite .kc { color: #7c3aed; font-weight: 500 } /* Keyword.Constant */
.codehilite .kd { color: #7c3aed; font-weight: 500 } /* Keyword.Declaration */
.codehilite .kn { color: #7c3aed; font-weight: 500 } /* Keyword.Namespace */
.codehilite .kp { color: #7c3aed } /* Keyword.Pseudo */
.codehilite .kr { color: #7c3aed; font-weight: 500 } /* Keyword.Reserved */
.codehilite .kt { color: #0891b2; font-weight: 500 } /* Keyword.Type */
.codehilite .m { color: #0d9488 } /* Literal.Number */
.codehilite .s { color: #16a34a } /* Literal.String */
.codehilite .na { color: #b45309 } /* Name.Attribute */
.codehilite .nb { color: #0891b2 } /* Name.Builtin */
.codehilite .nc { color: #0891b2; font-weight: 500 } /* Name.Class */
.codehilite .no { color: #b45309 } /* Name.Constant */
.codehilite .nd { color: #b45309 } /* Name.Decorator */
.codehilite .ni { color: #1f2937 } /* Name.Entity */
.codehilite .ne { color: #dc2626 } /* Name.Exception */
.codehilite .nf { color: #2563eb } /* Name.Function */
.codehilite .nl { color: #1f2937 } /* Name.Label */
.codehilite .nn { color: #0891b2 } /* Name.Namespace */
.codehilite .nt { color: #7c3aed } /* Name.Tag */
.codehilite .nv { color: #1f2937 } /* Name.Variable */
.codehilite .ow { color: #7c3aed } /* Operator.Word */
.codehilite .w { color: #1f2937 } /* Text.Whitespace */
.codehilite .mf { color: #0d9488 } /* Literal.Number.Float */
.codehilite .mh { color: #0d9488 } /* Literal.Number.Hex */
.codehilite .mi { color: #0d9488 } /* Literal.Number.Integer */
.codehilite .mo { color: #0d9488 } /* Literal.Number.Oct */
.codehilite .sb { color: #16a34a } /* Literal.String.Backtick */
.codehilite .sc { color: #16a34a } /* Literal.String.Char */
.codehilite .sd { color: #16a34a } /* Literal.String.Doc */
.codehilite .s2 { color: #16a34a } /* Literal.String.Double */
.codehilite .se { color: #b45309 } /* Literal.String.Escape */
.codehilite .sh { color: #16a34a } /* Literal.String.Heredoc */
.codehilite .si { color: #b45309 } /* Literal.String.Interpol */
.codehilite .sx { color: #16a34a } /* Literal.String.Other */
.codehilite .sr { color: #dc2626 } /* Literal.String.Regex */
.codehilite .s1 { color: #16a34a } /* Literal.String.Single */
.codehilite .ss { color: #16a34a } /* Literal.String.Symbol */
.codehilite .bp { color: #0891b2 } /* Name.Builtin.Pseudo */
.codehilite .vc { color: #1f2937 } /* Name.Variable.Class */
.codehilite .vg { color: #1f2937 } /* Name.Variable.Global */
.codehilite .vi { color: #1f2937 } /* Name.Variable.Instance */
.codehilite .il { color: #0d9488 } /* Literal.Number.Integer.Long */

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.5em 0;
    font-size: 8pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid var(--table-border);
    padding: 0.3em 0.5em;
    text-align: left;
}

th {
    background-color: var(--table-header-bg);
    font-weight: 600;
}

tr:nth-child(even) {
    background-color: #f9fafb;
}

/* Blockquotes */
blockquote {
    border-left: 3px solid var(--blockquote-border);
    background-color: var(--blockquote-bg);
    margin: 0.5em 0;
    padding: 0.4em 0.8em;
    border-radius: 0 4px 4px 0;
    font-size: 8.5pt;
}

blockquote p {
    margin: 0.2em 0;
}

blockquote p:first-child {
    margin-top: 0;
}

blockquote p:last-child {
    margin-bottom: 0;
}

/* Lists */
ul, ol {
    margin: 0.4em 0;
    padding-left: 1.3em;
}

li {
    margin: 0.15em 0;
}

li > ul, li > ol {
    margin: 0.1em 0;
}

/* Horizontal rule */
hr {
    border: none;
    border-top: 1px solid #d1d5db;
    margin: 1em 0;
}

/* Strong and emphasis */
strong {
    font-weight: 600;
    color: var(--heading-color);
}

em {
    font-style: italic;
}

/* Images */
img {
    max-width: 100%;
    height: auto;
    border-radius: 4px;
}

/* Checkboxes (for task lists) */
input[type="checkbox"] {
    margin-right: 0.3em;
}

/* Definition lists */
dl {
    margin: 0.5em 0;
}

dt {
    font-weight: 600;
    margin-top: 0.3em;
}

dd {
    margin-left: 1.2em;
    margin-bottom: 0.3em;
}

/* Table of contents */
.toc {
    background-color: #f8f9fc;
    border: 1px solid #e2e8f0;
    border-radius: 5px;
    padding: 0.6em 1em;
    margin: 0.5em 0;
    font-size: 8pt;
}

.toc ul {
    list-style: none;
    padding-left: 0.8em;
}

.toc > ul {
    padding-left: 0;
}

.toc a {
    color: var(--text-color);
}

/* Print optimizations */
@media print {
    body {
        font-size: 8pt;
    }

    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }

    pre, blockquote, table, figure {
        page-break-inside: avoid;
    }

    a {
        color: var(--text-color);
    }
}
"""


def convert_md_to_pdf(input_file: str, output_file: str = None, include_toc: bool = False):
    """
    Convert a Markdown file to PDF with beautiful styling.

    Args:
        input_file: Path to the input Markdown file
        output_file: Path to the output PDF file (optional, defaults to same name as input)
        include_toc: Whether to include a table of contents
    """

    # Determine output file name
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.pdf"

    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Configure markdown extensions
    extensions = [
        'tables',
        'fenced_code',
        CodeHiliteExtension(
            linenums=False,
            css_class='codehilite',
            guess_lang=True,
            use_pygments=True
        ),
        'nl2br',
        'sane_lists',
        'smarty',
        'attr_list',
        'def_list',
        'abbr',
        'md_in_html',
    ]

    if include_toc:
        extensions.append(TocExtension(
            title='Table des matières',
            toc_depth=3
        ))

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(md_content)

    # Add TOC if requested
    if include_toc and hasattr(md, 'toc'):
        html_content = f'<div class="toc">{md.toc}</div>\n{html_content}'

    # Wrap in full HTML document
    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
{html_content}
</body>
</html>
"""

    # Convert to PDF
    html = HTML(string=full_html, base_url=os.path.dirname(os.path.abspath(input_file)))
    css = CSS(string=CSS_STYLE)

    html.write_pdf(output_file, stylesheets=[css])

    print(f"✓ PDF generated: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='Convert Markdown to PDF with beautiful styling and syntax highlighting.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python md_to_pdf.py document.md
  python md_to_pdf.py document.md -o output.pdf
  python md_to_pdf.py document.md --toc
        """
    )

    parser.add_argument(
        'input',
        help='Input Markdown file'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output PDF file (default: same name as input with .pdf extension)'
    )

    parser.add_argument(
        '--toc',
        action='store_true',
        help='Include table of contents'
    )

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}")
        return 1

    try:
        convert_md_to_pdf(args.input, args.output, args.toc)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
