from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "Output"

DISTRICTS = [
    "Biswanath",
    "Charaideo",
    "Darrang",
    "Golaghat",
    "Hojai",
    "Jorhat",
    "Nagaon",
    "Sivasagar",
    "Sonitpur",
]

print("=" * 70)
print("FLOOD INTELLIGENCE CSV COLUMN INSPECTION")
print("=" * 70)

for district in DISTRICTS:

    file = OUTPUT_DIR / f"{district}_flood_intelligence_summary.csv"

    print(f"\n{'-' * 70}")
    print(district)
    print(f"File: {file}")

    if not file.exists():
        print("❌ FILE NOT FOUND")
        continue

    df = pd.read_csv(file)

    print("\nColumns:")

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:02d}. {column}")

    print("\nValues:")

    if len(df) > 0:
        print(df.iloc[0].to_dict())

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)