import os
import pandas as pd
import pdfplumber


# BASE_DIR = adresář projektu (tam kde máš manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_table_from_pdf(pdf_path, base_filename, output_path=None):
    """Vytáhne všechny tabulky z PDF a uloží je jako CSV.

    - tabulky mohou být na více stranách i ve více blocích
    - řádek hlavičky je ignorován
    - prázdné buňky jsou nahrazeny nulou
    - velikost PDF je omezená na 10 MB

    Parameters
    ----------
    pdf_path: str
        Cesta k PDF souboru.
    base_filename: str
        Základ názvu CSV, pokud není zadána explicitní cesta k výstupu.
    output_path: str | None
        Plná cesta k CSV souboru. Pokud není uvedena, uloží se do
        ``media/csv`` s použitím ``base_filename``.

    Returns
    -------
    str | None
        Cesta k vytvořenému CSV, nebo ``None`` při chybě.
    """

    try:
        if os.path.getsize(pdf_path) > 10 * 1024 * 1024:
            raise ValueError("PDF soubor přesahuje 10MB limit")

        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "snap_tolerance": 3,
                    }
                )
                for table in page_tables:
                    if not table:
                        continue
                    df = pd.DataFrame(table)
                    if len(df) == 0:
                        continue
                    df = df.iloc[1:]  # odstraníme hlavičku
                    df.columns = [f"col_{i}" for i in range(len(df.columns))]
                    df = df.replace(["", None], 0).fillna(0)
                    tables.append(df)

        if not tables:
            print(f"⚠️ Nebyly nalezeny tabulky v {pdf_path}")
            return None

        # Spojíme všechny tabulky z více stran do jedné
        df_final = pd.concat(tables, ignore_index=True)

        # Cesta kam uložíme CSV
        output_dir = os.path.join(BASE_DIR, "media", "csv")
        os.makedirs(output_dir, exist_ok=True)

        if output_path:
            csv_path = output_path
        else:
            csv_path = os.path.join(output_dir, f"{base_filename}.csv")

        df_final.to_csv(csv_path, index=False, header=False, encoding="utf-8-sig")

        print(f"✅ CSV vytvořeno: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Chyba při extrakci tabulky z {pdf_path}: {e}")
        return None
