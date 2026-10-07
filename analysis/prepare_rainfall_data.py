from pathlib import Path
import pandas as pd
import json
import re


# ============================================================
# ASSAM FLOOD INTELLIGENCE
# RAINFALL DATA PREPARATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "Output"

RAINFALL_DIR = (
    PROJECT_ROOT
    / "Cache"
    / "dashboard_data"
    / "rainfall"
)

RAINFALL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


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


# ============================================================
# FIND FILE
# ============================================================

def find_rainfall_file(district):

    expected = (
        OUTPUT_DIR
        / f"{district}_daily_rainfall.csv"
    )

    if expected.exists():
        return expected

    # Fallback search
    district_key = re.sub(
        r"[^a-z0-9]",
        "",
        district.lower()
    )

    for file in OUTPUT_DIR.rglob("*.csv"):

        name = re.sub(
            r"[^a-z0-9]",
            "",
            file.stem.lower()
        )

        if (
            district_key in name
            and "dailyrainfall" in name
        ):
            return file

    return None


# ============================================================
# MAIN
# ============================================================

print("=" * 70)
print("ASSAM FLOOD INTELLIGENCE")
print("RAINFALL DATA PREPARATION")
print("=" * 70)


for district in DISTRICTS:

    print("\n" + "-" * 70)
    print(district)
    print("-" * 70)

    file = find_rainfall_file(district)

    if file is None:

        print("❌ Rainfall file not found")

        continue

    print(
        f"Source: {file}"
    )

    df = pd.read_csv(file)

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {list(df.columns)}"
    )


    # ========================================================
    # CLEAN COLUMN NAMES
    # ========================================================

    df.columns = [
        str(col).strip()
        for col in df.columns
    ]


    # ========================================================
    # FIND DATE COLUMN
    # ========================================================

    date_column = None

    possible_date_columns = [
        "date",
        "Date",
        "DATE",
        "day",
        "Day",
        "datetime",
    ]

    for column in possible_date_columns:

        if column in df.columns:

            date_column = column

            break


    if date_column is None:

        print(
            "❌ Could not identify date column."
        )

        print(
            "Available columns:",
            list(df.columns)
        )

        continue


    # ========================================================
    # FIND RAINFALL COLUMN
    # ========================================================

    rainfall_column = None

    possible_rainfall_columns = [
        "rainfall_mm",
        "Rainfall_mm",
        "rainfall",
        "Rainfall",
        "daily_rainfall_mm",
        "Daily_Rainfall_mm",
        "total_rainfall_mm",
        "precipitation_mm",
        "precipitation",
    ]

    for column in possible_rainfall_columns:

        if column in df.columns:

            rainfall_column = column

            break


    if rainfall_column is None:

        # Try automatic detection
        for column in df.columns:

            column_key = (
                str(column)
                .lower()
                .replace("_", "")
                .replace(" ", "")
            )

            if (
                "rainfall" in column_key
                or "precipitation" in column_key
            ):

                rainfall_column = column

                break


    if rainfall_column is None:

        print(
            "❌ Could not identify rainfall column."
        )

        print(
            "Available columns:",
            list(df.columns)
        )

        continue


    # ========================================================
    # PREPARE DATA
    # ========================================================

    rainfall = df[
        [
            date_column,
            rainfall_column
        ]
    ].copy()


    rainfall.columns = [
        "date",
        "rainfall_mm"
    ]


    rainfall["date"] = pd.to_datetime(
        rainfall["date"],
        errors="coerce"
    )


    rainfall["rainfall_mm"] = pd.to_numeric(
        rainfall["rainfall_mm"],
        errors="coerce"
    )


    rainfall = rainfall.dropna(
        subset=[
            "date",
            "rainfall_mm"
        ]
    )


    rainfall = rainfall.sort_values(
        "date"
    )


    # ========================================================
    # FORMAT DATE FOR WEB
    # ========================================================

    rainfall["date"] = rainfall[
        "date"
    ].dt.strftime(
        "%Y-%m-%d"
    )


    # ========================================================
    # CONVERT TO JSON RECORDS
    # ========================================================

    records = []

    for _, row in rainfall.iterrows():

        records.append(
            {
                "date": row["date"],
                "rainfall_mm": round(
                    float(row["rainfall_mm"]),
                    3
                )
            }
        )


    # ========================================================
    # SAVE
    # ========================================================

    output_file = (
        RAINFALL_DIR
        / f"{district}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            records,
            f,
            indent=2,
            ensure_ascii=False
        )


    # ========================================================
    # REPORT
    # ========================================================

    total_rainfall = rainfall[
        "rainfall_mm"
    ].sum()

    max_rainfall = rainfall[
        "rainfall_mm"
    ].max()

    print(
        f"✓ Days: {len(rainfall)}"
    )

    print(
        f"✓ Total rainfall: "
        f"{total_rainfall:.2f} mm"
    )

    print(
        f"✓ Maximum daily rainfall: "
        f"{max_rainfall:.2f} mm"
    )

    print(
        f"✓ Saved: {output_file.name}"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("✅ RAINFALL DATA PREPARATION COMPLETE")
print("=" * 70)

print(
    f"\nOutput folder:\n{RAINFALL_DIR}"
)