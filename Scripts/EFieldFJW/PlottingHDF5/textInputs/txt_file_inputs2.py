import csv

def read_selected_headers_from_files(filenames, headers_to_extract):
    """Read specified header fields from multiple text/CSV files."""
    all_results = {}

    for filename in filenames:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            extracted_rows = []
            for row in reader:
                extracted = {h: row[h] for h in headers_to_extract if h in row}
                extracted_rows.append(extracted)
            all_results[filename] = extracted_rows

    return all_results


if __name__ == "__main__":
    f1 = "b_coils.txt"
    f2 = "e_coils.txt"
    f3 = "particles.txt"
    # add as many files as you want
    # ---- Configure inputs ----)
    filenames = [
        f1,
        f2,
        f3
    ]

    # Choose which header categories (columns) to extract
    # headers_to_extract = [* : *]
    headers_to_extract = ["PosX", "Amp", "Q", "Diameter", "Inner_r", "px", "py","pz","vx", "vy", "vz"]

    # ---- Process ----
    results = read_selected_headers_from_files(filenames, headers_to_extract)

    # ---- Output ----
    for fname, rows in results.items():
        print(f"\n=== File: {fname} ===")
        for i, row in enumerate(rows, start=1):
            print(f"--- Entry {i} ---")
            for key, value in row.items():
                print(f"{key}: {value}")