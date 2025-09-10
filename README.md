# pdfex

Utility for extracting tables from PDF files and converting them to CSV.

## CLI usage

The repository provides a small command line tool built on top of
`pdfplumber`. It searches for tables based on the visual lines in the PDF,
merges tables found across all pages and stores the result in a single CSV
file. Table header rows are skipped and empty cells are filled with `0`.

```
python pdf_to_csv.py path/to/input.pdf [-o output.csv]
```

The tool enforces a 10&nbsp;MB limit on the source PDF. If no output path is
provided the CSV will be placed into `webapp/media/csv/` using the name of
the input PDF.

## Django integration

The included Django app uses the same extractor when users upload PDFs.
After each upload, the user receives a toast message and project
administrators are notified by e‑mail.  The development configuration uses
the console e‑mail backend and can be adjusted in
`webapp/core/settings.py`.
