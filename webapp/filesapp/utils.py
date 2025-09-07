import os
import pandas as pd
import pdfplumber

# BASE_DIR = adresář projektu (tam kde máš manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_table_from_pdf(pdf_path, base_filename):
    """
    Otevře PDF, vytáhne první tabulku a uloží ji jako CSV.
    Vrátí cestu k CSV souboru nebo None pokud selže.
    """
    try:
        tables = []

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)

        if not tables:
            print(f"⚠️ Nebyly nalezeny tabulky v {pdf_path}")
            return None

        # Spojíme všechny tabulky z více stránek do jedné
        df_final = pd.concat(tables, ignore_index=True)

        # Cesta kam uložíme CSV
        output_dir = os.path.join(BASE_DIR, "media", "csv")
        os.makedirs(output_dir, exist_ok=True)

        csv_path = os.path.join(output_dir, f"{base_filename}.csv")
        df_final.to_csv(csv_path, index=False, encoding="utf-8-sig")

        print(f"✅ CSV vytvořeno: {csv_path}")
        return csv_path

    except Exception as e:
        print(f"❌ Chyba při extrakci tabulky z {pdf_path}: {e}")
        return None
