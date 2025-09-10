#!/usr/bin/env python
"""Command line tool to extract tables from a PDF into a CSV file.

Uses pdfplumber to detect tables via visual lines and concatenates
all tables across pages. Header rows are ignored and missing values
are replaced with zeros.

Usage:
    python pdf_to_csv.py input.pdf [-o output.csv]
"""

import argparse
import os
from webapp.filesapp.utils import extract_table_from_pdf


def main():
    parser = argparse.ArgumentParser(description="Extract tables from PDF to CSV")
    parser.add_argument("pdf", help="Path to input PDF file")
    parser.add_argument(
        "-o", "--output", help="Optional path to output CSV file", default=None
    )
    args = parser.parse_args()

    pdf_path = args.pdf
    if not os.path.exists(pdf_path):
        raise SystemExit(f"Soubor {pdf_path} neexistuje")

    base_name = os.path.splitext(os.path.basename(args.output or pdf_path))[0]
    csv_path = extract_table_from_pdf(pdf_path, base_name, args.output)
    if csv_path:
        print(f"CSV uloženo do: {csv_path}")
    else:
        raise SystemExit("Nepodařilo se extrahovat tabulky")


if __name__ == "__main__":
    main()
