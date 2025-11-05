import pandas as pd

def create_field_particle_table():
    # Define headers
    columns = ["B Field", "E Field", "Particle"]

    # Data exactly as specified, with "-" instead of blanks
    data = [
        ["1e5", "1e-10", "-"],  # Row 1
        ["1.0", "0.75", "-"],   # Row 2
        ["-", "0.25", "-"],     # Row 3
        ["1.1", "1.1", "20"],   # Row 4
        ["-", "-", "10"],       # Row 5
        ["-", "-", "10"],       # Row 6
    ]

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    return df


if __name__ == "__main__":
    table = create_field_particle_table()

    print("\n=== 3×6 B–E–Particle Table ===\n")
    print(table.to_string(index=False))
