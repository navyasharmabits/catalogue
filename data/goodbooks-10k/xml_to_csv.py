import xml.etree.ElementTree as ET
import pandas as pd
import glob

rows = []

for file in glob.glob("*.xml"):
    tree = ET.parse(file)
    root = tree.getroot()

    for book in root.findall(".//book"):
        rows.append({
            "title": book.findtext("title"),
            "author": book.findtext("author"),
            "year": book.findtext("year"),
            "publisher": book.findtext("publisher"),
            "isbn": book.findtext("isbn")
        })

df = pd.DataFrame(rows)
df.to_csv("books.csv", index=False)

print("CSV created:", df.shape)
