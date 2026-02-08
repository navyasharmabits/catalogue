import csv
import re

# Files
INPUT_FILE = "input.csv"
OUTPUT_FILE = "clean_num.csv"
ERROR_LOG = "isbn_errors.txt"


def normalize_isbn(isbn):
    """Convert ISBN-10 to ISBN-13, validate ISBN-13"""

    if not isbn:
        return None, "Missing ISBN"

    # Clean input
    isbn = str(isbn).upper()
    isbn = isbn.replace("ISBN:", "").replace("ISBN", "")
    isbn = re.sub(r"[^0-9X]", "", isbn)

    # ---------- ISBN-10 → ISBN-13 ----------
    if re.fullmatch(r"\d{9}[\dX]", isbn):

        core = isbn[:-1]
        isbn12 = "978" + core

        total = 0
        for i, d in enumerate(isbn12):
            n = int(d)
            total += n * (1 if i % 2 == 0 else 3)

        check = (10 - (total % 10)) % 10

        return isbn12 + str(check), None


    # ---------- Validate ISBN-13 ----------
    if re.fullmatch(r"\d{13}", isbn):

        total = 0
        for i, d in enumerate(isbn):
            n = int(d)
            total += n * (1 if i % 2 == 0 else 3)

        if total % 10 == 0:
            return isbn, None
        else:
            return isbn, "Invalid ISBN-13 checksum"


    return isbn, "Invalid ISBN format"


# -------------------- Run Cleaning --------------------

clean_rows = []
errors = []

with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:

    reader = csv.DictReader(f)

    if "ISBN" not in reader.fieldnames:
        raise ValueError("CSV must contain ISBN column")

    row_num = 1

    for row in reader:
        row_num += 1

        isbn, err = normalize_isbn(row["ISBN"])

        if err:
            errors.append(f"Row {row_num}: {err}")
            continue   # Skip bad rows

        clean_rows.append({
            "ISBN": isbn
        })


# Write cleaned file
with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:

    writer = csv.DictWriter(f, fieldnames=["ISBN"])
    writer.writeheader()
    writer.writerows(clean_rows)


# Write error log
with open(ERROR_LOG, "w", encoding="utf-8") as f:

    if errors:
        f.write("\n".join(errors))
    else:
        f.write("No errors found\n")


# Show summary in notebook
print("Cleaning complete")
print("---------------")
print(f"Output file : {OUTPUT_FILE}")
print(f"Error log   : {ERROR_LOG}")
print(f"Valid ISBNs : {len(clean_rows)}")
print(f"Invalid     : {len(errors)}")
