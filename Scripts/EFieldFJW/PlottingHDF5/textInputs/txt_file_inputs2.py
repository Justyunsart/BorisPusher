import csv


def read_selected_columns(filename, col_indices, row_indices):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)  # read header line
        selected_headers = [headers[i] for i in col_indices]

        rows = []
        for line_number, line in enumerate(reader, start=1):
            if line_number in row_indices:  # only keep selected entries
                selected_values = [line[i] for i in col_indices]
                rows.append(dict(zip(selected_headers, selected_values)))

    return selected_headers, rows


if __name__ == "__main__":
    filename = "b_coils.txt"

    # Choose columns (0-based): 2, 4, 5  → PosZ, Diameter, RotationAngle
    col_indices = [2, 4, 5]

    # Choose which rows (1-based): entry 1 or 2
    row_indices = [1, 2]

    selected_headers, rows = read_selected_columns(filename, col_indices, row_indices)

    print("Selected headers:", selected_headers)
    print()
    for i, row in enumerate(rows, start=1):
        print(f"--- Entry {row_indices[i - 1]} ---")
        for key, value in row.items():
            print(f"{key}: {value}")