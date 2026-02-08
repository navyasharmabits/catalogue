import csv
import re

INPUT_FILE = "input.csv"
OUTPUT_FILE = "cleaned_books.csv"
ERROR_LOG = "errors.txt"


def clean_text(text):
    """Trim spaces and normalize spacing"""
    if not text:
        return ""

    # Remove leading/trailing spaces
    text = text.strip()

    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    return text


def normalize_title(title):
    """Title Case for book titles"""
    return clean_text(title).title()


def normalize_author(author):
    """Title Case for author names"""
    return clean_text(author).title()


def normalize_publisher(pub):
    """Title Case for publisher"""
    return clean_text(pub).title()


def normalize_isbn(isbn):
    """Convert all ISBNs to valid ISBN-13 or flag error"""

    if not isbn:
        return "", "Missing ISBN"

    # Clean input
    isbn = str(isbn).upper()
    isbn = isbn.replace("ISBN:", "").replace("ISBN", "")
    isbn = re.sub(r"[^0-9X]", "", isbn)

    # ---------- ISBN-10 → ISBN-13 ----------
    if re.fullmatch(r"\d{9}[\dX]", isbn):

        core = isbn[:-1]              # remove old checksum
        isbn12 = "978" + core         # add prefix

        total = 0
        for i, d in enumerate(isbn12):
            n = int(d)
            total += n * (1 if i % 2 == 0 else 3)

        check = (10 - (total % 10)) % 10

        return isbn12 + str(check), None


    # ---------- Already ISBN-13 ----------
    if re.fullmatch(r"\d{13}", isbn):

        total = 0
        for i, d in enumerate(isbn):
            n = int(d)
            total += n * (1 if i % 2 == 0 else 3)

        if total % 10 == 0:
            return isbn, None
        else:
            return isbn, "Invalid ISBN-13 checksum"


    # ---------- Invalid ----------
    return isbn, "Invalid ISBN format"


def validate_year(year):
    """Check reasonable publication year"""
    if not year:
        return "", "Missing year"

    year = clean_text(year)

    if not year.isdigit():
        return year, "Year is not numeric"

    y = int(year)

    if y < 1450 or y > 2026:
        return year, "Unrealistic year"

    return year, None


def main():

    errors = []
    cleaned_rows = []

    with open(INPUT_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        required_cols = ["ISBN", "TITLE", "AUTHOR", "YEAR", "PUBLISHER"]

        for col in required_cols:
            if col not in reader.fieldnames:
                raise ValueError(f"Missing column: {col}")

        row_num = 1

        for row in reader:
            row_num += 1
            row_errors = []

            # Clean fields
            isbn, isbn_err = normalize_isbn(row["ISBN"])
            title = normalize_title(row["TITLE"])
            author = normalize_author(row["AUTHOR"])
            year, year_err = validate_year(row["YEAR"])
            publisher = normalize_publisher(row["PUBLISHER"])

            # Error collection
            if isbn_err:
                row_errors.append(isbn_err)

            if not title:
                row_errors.append("Missing title")

            if not author:
                row_errors.append("Missing author")

            if year_err:
                row_errors.append(year_err)

            if not publisher:
                row_errors.append("Missing publisher")

            # Save cleaned row
            cleaned_rows.append({
                "ISBN": isbn,
                "TITLE": title,
                "AUTHOR": author,
                "YEAR": year,
                "PUBLISHER": publisher
            })

            # Save errors
            if row_errors:
                errors.append(
                    f"Row {row_num}: {', '.join(row_errors)}"
                )

    # Write cleaned CSV
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ISBN", "TITLE", "AUTHOR", "YEAR", "PUBLISHER"]
        )

        writer.writeheader()
        writer.writerows(cleaned_rows)

    # Write error log
    with open(ERROR_LOG, "w", encoding="utf-8") as f:
        if errors:
            f.write("\n".join(errors))
        else:
            f.write("No errors found.\n")

    print("Cleaning complete.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Errors: {ERROR_LOG}")


if __name__ == "__main__":
    main()
