

import pandas as pd
import requests
import time
import os

def fetch_google_metadata(isbn):
    """Clean API Flow: Direct data retrieval without browser overhead."""
    isbn_clean = str(isbn).split('.')[0].strip()
    if not isbn_clean or isbn_clean == 'nan':
        return None
        
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"
    try:
        # High-contrast logic: 10s timeout to prevent system hangs
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                info = data["items"][0]["volumeInfo"]
                return {
                    "Title": info.get("title", "N/A"),
                    "Author": ", ".join(info.get("authors", ["Unknown"])),
                    "publisher": info.get("publisher", "N/A"),
                    "publication_date": info.get("publishedDate", "N/A")
                }
    except Exception:
        pass
    return None

def process_library_fast(input_csv, output_csv):
    # 1. Load the structural layer
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return
        
    df = pd.read_csv(input_csv)
    total_rows = len(df)
    
    # 2. Logic Orange: Identify the best search column
    search_col = 'isbn13' if 'isbn13' in df.columns else 'ISBN'
    
    print(f"Total rows: {total_rows}. Starting Enrichment using {search_col}...")

    # 3. Active Flow: Row-by-row mapping
    for index, row in df.iterrows():
        isbn = row[search_col]
        
        # Fetch fresh data
        metadata = fetch_google_metadata(isbn)
        
        if metadata:
            # High-precision mapping: Overwrites ONLY the targeted columns
            df.at[index, 'Title'] = metadata['Title']
            df.at[index, 'Author'] = metadata['Author']
            df.at[index, 'publisher'] = metadata['publisher']
            df.at[index, 'publication_date'] = metadata['publication_date']
            print(f"[OK] {index+1}/{total_rows}: {metadata['Title']}")
        else:
            print(f"[SKIP] {index+1}/{total_rows}: No data for {isbn}")

        # 4. Structural Integrity: Save progress every 25 rows
        if (index + 1) % 25 == 0:
            df.to_csv(output_csv, index=False)
            print(f"--- Progress: {((index+1)/total_rows)*100:.2f}% ---")
            
    # 5. Final Save
    df.to_csv(output_csv, index=False)
    print(f"\nGrid Enriched. System saved to {output_csv}")

# --- EXECUTION ---
process_library_fast("cleaned_books.csv", "library_enriched.csv")

