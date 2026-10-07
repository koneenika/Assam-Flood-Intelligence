import pandas as pd
import json
from pathlib import Path

# ============================================================
# ASSAM FLOOD INTELLIGENCE
# RIVER DATA PREPARATION
# ============================================================

PROJECT_ROOT = Path(r"D:\PORTFOLIO PROJECT\Assam Flood")

REFERENCE_FILE = PROJECT_ROOT / "Output" / "river" / "river_gauge_reference.csv"
OBSERVATION_FILE = PROJECT_ROOT / "Output" / "river" / "river_water_level_observations.csv"
OUTPUT_DIR = PROJECT_ROOT / "Cache" / "dashboard_data" / "river"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CURRENT PROJECT DISTRICTS
# ============================================================

PROJECT_DISTRICTS = {
    "Biswanath",
    "Charaideo",
    "Darrang",
    "Golaghat",
    "Hojai",
    "Jorhat",
    "Nagaon",
    "Sivasagar",
    "Sonitpur",
}

# Lakhimpur is permanently excluded from this project.
EXCLUDED_DISTRICTS = {
    "Lakhimpur",
}


def clean_records(df):
    """Convert dataframe to JSON-safe records."""
    return json.loads(
        df.where(pd.notnull(df), None).to_json(orient="records")
    )


def is_lakhimpur(value):
    """
    Detect Lakhimpur safely even if the source contains
    variations such as 'Lakhimpur_Ranga_Nadi'.
    """
    if pd.isna(value):
        return False

    value = str(value).strip().lower()

    return value == "lakhimpur" or value.startswith("lakhimpur_")


print("=" * 70)
print("ASSAM FLOOD INTELLIGENCE")
print("RIVER DATA PREPARATION")
print("=" * 70)

print("\nProject districts:")
for district in sorted(PROJECT_DISTRICTS):
    print(f"  ✓ {district}")

print("\nExcluded:")
for district in sorted(EXCLUDED_DISTRICTS):
    print(f"  ✗ {district}")


# ============================================================
# 1. GAUGE REFERENCE
# ============================================================

print("\n" + "-" * 70)
print("GAUGE REFERENCE")
print("-" * 70)

reference = pd.read_csv(REFERENCE_FILE)

print(f"Source: {REFERENCE_FILE}")
print(f"Original rows: {len(reference)}")
print(f"Columns: {reference.columns.tolist()}")

# ------------------------------------------------------------
# Remove Lakhimpur stations
# ------------------------------------------------------------

before = len(reference)

reference = reference[
    ~reference["District"].apply(is_lakhimpur)
].copy()

removed = before - len(reference)

print(f"✓ Lakhimpur records removed: {removed}")
print(f"✓ Remaining gauge records: {len(reference)}")

# Save cleaned gauge reference
gauge_records = clean_records(reference)

with open(
    OUTPUT_DIR / "gauges.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        gauge_records,
        f,
        indent=2,
        ensure_ascii=False
    )

print("✓ Saved: gauges.json")


# ============================================================
# 2. WATER LEVEL OBSERVATIONS
# ============================================================

print("\n" + "-" * 70)
print("WATER LEVEL OBSERVATIONS")
print("-" * 70)

observations = pd.read_csv(OBSERVATION_FILE)

print(f"Source: {OBSERVATION_FILE}")
print(f"Original rows: {len(observations)}")
print(f"Columns: {observations.columns.tolist()}")

# ------------------------------------------------------------
# Remove any Lakhimpur observations if they ever appear
# ------------------------------------------------------------

before = len(observations)

observations = observations[
    ~observations["District"].apply(is_lakhimpur)
].copy()

removed = before - len(observations)

print(f"✓ Lakhimpur observations removed: {removed}")
print(f"✓ Remaining observations: {len(observations)}")

# Save cleaned observations
observation_records = clean_records(observations)

with open(
    OUTPUT_DIR / "observations.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        observation_records,
        f,
        indent=2,
        ensure_ascii=False
    )

print("✓ Saved: observations.json")


# ============================================================
# 3. VALIDATION
# ============================================================

print("\n" + "-" * 70)
print("VALIDATION")
print("-" * 70)

# Check that no Lakhimpur records remain
remaining_lakhimpur_reference = reference[
    reference["District"].apply(is_lakhimpur)
]

remaining_lakhimpur_observations = observations[
    observations["District"].apply(is_lakhimpur)
]

if len(remaining_lakhimpur_reference) == 0:
    print("✓ No Lakhimpur gauge records remain")
else:
    print("⚠ WARNING: Lakhimpur gauge records still present")

if len(remaining_lakhimpur_observations) == 0:
    print("✓ No Lakhimpur water-level observations remain")
else:
    print("⚠ WARNING: Lakhimpur observations still present")


# ============================================================
# 4. FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("RIVER DATA PREPARATION COMPLETE")
print("=" * 70)

print("\nFinal river dataset:")
print(f"  • Gauge/reference stations: {len(reference)}")
print(f"  • Water-level observations: {len(observations)}")

print("\nGauge districts retained:")

for district in reference["District"].unique():
    print(f"  • {district}")

print("\nOutput folder:")
print(OUTPUT_DIR)

print("\nFiles created:")
print("  ✓ gauges.json")
print("  ✓ observations.json")

print("\nLakhimpur:")
print("  ✗ Excluded from dashboard data")

print("\n" + "=" * 70)