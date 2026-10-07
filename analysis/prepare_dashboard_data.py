from pathlib import Path
import pandas as pd
import json
import re


# ============================================================
# ASSAM FLOOD INTELLIGENCE
# DASHBOARD DATA PREPARATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "Output"
CACHE_DIR = PROJECT_ROOT / "Cache" / "dashboard_data"

CACHE_DIR.mkdir(parents=True, exist_ok=True)


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
# HELPERS
# ============================================================

def normalize_text(value):
    if pd.isna(value):
        return ""

    value = str(value).lower().strip()

    value = re.sub(r"[^a-z0-9]", "", value)

    return value


def clean_columns(df):
    df = df.copy()

    df.columns = [
        str(col).strip().lower()
        for col in df.columns
    ]

    return df


def read_csv(path):

    if path is None or not path.exists():
        return None

    try:

        df = pd.read_csv(path)

        df = clean_columns(df)

        return df

    except Exception as e:

        print(f"ERROR reading {path.name}: {e}")

        return None


def find_file(district, keyword):

    district_key = normalize_text(district)

    files = list(
        OUTPUT_DIR.rglob("*.csv")
    )

    matches = []

    for file in files:

        file_key = normalize_text(file.stem)

        if (
            district_key in file_key
            and keyword in file_key
        ):

            matches.append(file)

    if matches:
        return matches[0]

    return None


def get_value(df, columns):

    if df is None or df.empty:
        return None

    for column in columns:

        if column in df.columns:

            value = df.iloc[0][column]

            if pd.notna(value):
                return value

    return None


# ============================================================
# MAIN DATA COLLECTION
# ============================================================

print("=" * 70)
print("ASSAM FLOOD INTELLIGENCE")
print("DASHBOARD DATA PREPARATION")
print("=" * 70)

print(f"\nOutput folder:")
print(OUTPUT_DIR)

print(f"\nDashboard cache:")
print(CACHE_DIR)


records = []


for district in DISTRICTS:

    print("\n" + "-" * 70)
    print(district)
    print("-" * 70)

    # --------------------------------------------------------
    # FIND FILES
    # --------------------------------------------------------

    flood_file = find_file(
        district,
        "floodintelligencesummary"
    )

    building_file = find_file(
        district,
        "buildingsummary"
    )

    road_file = find_file(
        district,
        "roadsummary"
    )

    rainfall_file = find_file(
        district,
        "dailyrainfall"
    )

    print(
        "Flood summary   :",
        flood_file.name if flood_file else "NOT FOUND"
    )

    print(
        "Building summary:",
        building_file.name if building_file else "NOT FOUND"
    )

    print(
        "Road summary    :",
        road_file.name if road_file else "NOT FOUND"
    )

    print(
        "Rainfall        :",
        rainfall_file.name if rainfall_file else "NOT FOUND"
    )

    # --------------------------------------------------------
    # READ DATA
    # --------------------------------------------------------

    flood_df = read_csv(flood_file)
    building_df = read_csv(building_file)
    road_df = read_csv(road_file)

    # --------------------------------------------------------
    # CREATE DISTRICT RECORD
    # --------------------------------------------------------

    record = {

        "district": district,

        # ====================================================
        # FLOOD EXTENT
        # ====================================================

        "district_area_km2": get_value(
            flood_df,
            [
                "district_area_km2"
            ]
        ),

        "flooded_area_km2": get_value(
            flood_df,
            [
                "flooded_area_km2"
            ]
        ),

        "flooded_area_percent": get_value(
            flood_df,
            [
                "flooded_area_percent"
            ]
        ),

        # ====================================================
        # CROPLAND
        # ====================================================

        "total_cropland_km2": get_value(
            flood_df,
            [
                "total_cropland_km2"
            ]
        ),

        "flooded_cropland_km2": get_value(
            flood_df,
            [
                "flooded_cropland_km2"
            ]
        ),

        "cropland_affected_percent": get_value(
            flood_df,
            [
                "cropland_affected_percent"
            ]
        ),

        # ====================================================
        # FOREST
        # ====================================================

        "total_forest_km2": get_value(
            flood_df,
            [
                "total_forest_km2"
            ]
        ),

        "flooded_forest_km2": get_value(
            flood_df,
            [
                "flooded_forest_km2"
            ]
        ),

        "forest_affected_percent": get_value(
            flood_df,
            [
                "forest_affected_percent"
            ]
        ),

        # ====================================================
        # RAINFALL
        # ====================================================

        "flood_period_rainfall_mm": get_value(
            flood_df,
            [
                "flood_period_rainfall_mm"
            ]
        ),

        "maximum_daily_rainfall_mm": get_value(
            flood_df,
            [
                "maximum_daily_rainfall_mm"
            ]
        ),

        "rainfall_days": get_value(
            flood_df,
            [
                "rainfall_days"
            ]
        ),

        # ====================================================
        # ELEVATION
        # ====================================================

        "mean_elevation_m": get_value(
            flood_df,
            [
                "mean_elevation_m"
            ]
        ),

        "minimum_elevation_m": get_value(
            flood_df,
            [
                "minimum_elevation_m"
            ]
        ),

        "maximum_elevation_m": get_value(
            flood_df,
            [
                "maximum_elevation_m"
            ]
        ),

        # ====================================================
        # SLOPE
        # ====================================================

        "mean_slope_degrees": get_value(
            flood_df,
            [
                "mean_slope_degrees"
            ]
        ),

        "minimum_slope_degrees": get_value(
            flood_df,
            [
                "minimum_slope_degrees"
            ]
        ),

        "maximum_slope_degrees": get_value(
            flood_df,
            [
                "maximum_slope_degrees"
            ]
        ),

        # ====================================================
        # BUILDINGS
        # ====================================================

        "total_osm_mapped_buildings": get_value(
            flood_df,
            [
                "total_osm_mapped_buildings"
            ]
        ),

        "flood_affected_buildings": get_value(
            flood_df,
            [
                "flood_affected_buildings"
            ]
        ),

        "buildings_affected_percent": get_value(
            flood_df,
            [
                "buildings_affected_percent"
            ]
        ),

        # ====================================================
        # ROADS
        # ====================================================

        "total_osm_mapped_road_length_km": get_value(
            flood_df,
            [
                "total_osm_mapped_road_length_km"
            ]
        ),

        "flood_affected_road_length_km": get_value(
            flood_df,
            [
                "flood_affected_road_length_km"
            ]
        ),

        "road_affected_percent": get_value(
            flood_df,
            [
                "road_affected_percent"
            ]
        ),

        "total_mapped_road_segments": get_value(
            flood_df,
            [
                "total_mapped_road_segments"
            ]
        ),

        "flood_affected_road_segments": get_value(
            flood_df,
            [
                "flood_affected_road_segments"
            ]
        ),
    }


    # ========================================================
    # FILL BUILDING DATA FROM SEPARATE SUMMARY
    # ========================================================

    if (
        record["total_osm_mapped_buildings"] is None
        and building_df is not None
    ):

        record["total_osm_mapped_buildings"] = get_value(
            building_df,
            [
                "total_osm_mapped_buildings",
                "total_mapped_buildings",
                "total_buildings",
                "buildings_total",
            ]
        )

    if (
        record["flood_affected_buildings"] is None
        and building_df is not None
    ):

        record["flood_affected_buildings"] = get_value(
            building_df,
            [
                "flood_affected_buildings",
                "affected_buildings",
                "flooded_buildings",
                "buildings_affected",
            ]
        )

    if (
        record["buildings_affected_percent"] is None
        and building_df is not None
    ):

        record["buildings_affected_percent"] = get_value(
            building_df,
            [
                "buildings_affected_percent",
                "flood_affected_buildings_percent",
                "affected_buildings_percent",
            ]
        )


    # ========================================================
    # FILL ROAD DATA FROM SEPARATE SUMMARY
    # ========================================================

    if (
        record["total_osm_mapped_road_length_km"] is None
        and road_df is not None
    ):

        record["total_osm_mapped_road_length_km"] = get_value(
            road_df,
            [
                "total_osm_mapped_road_length_km",
                "total_road_length_km",
                "total_roads_km",
                "total_mapped_road_length_km",
            ]
        )

    if (
        record["flood_affected_road_length_km"] is None
        and road_df is not None
    ):

        record["flood_affected_road_length_km"] = get_value(
            road_df,
            [
                "flood_affected_road_length_km",
                "affected_road_length_km",
                "flooded_road_length_km",
                "flooded_roads_km",
            ]
        )

    if (
        record["road_affected_percent"] is None
        and road_df is not None
    ):

        record["road_affected_percent"] = get_value(
            road_df,
            [
                "road_affected_percent",
                "flood_affected_road_percent",
                "affected_road_percent",
            ]
        )


    # ========================================================
    # CALCULATE MISSING PERCENTAGES
    # ========================================================

    if (
        record["buildings_affected_percent"] is None
        and record["flood_affected_buildings"] is not None
        and record["total_osm_mapped_buildings"] is not None
        and record["total_osm_mapped_buildings"] > 0
    ):

        record["buildings_affected_percent"] = (
            record["flood_affected_buildings"]
            / record["total_osm_mapped_buildings"]
            * 100
        )


    if (
        record["road_affected_percent"] is None
        and record["flood_affected_road_length_km"] is not None
        and record["total_osm_mapped_road_length_km"] is not None
        and record["total_osm_mapped_road_length_km"] > 0
    ):

        record["road_affected_percent"] = (
            record["flood_affected_road_length_km"]
            / record["total_osm_mapped_road_length_km"]
            * 100
        )


    records.append(record)


# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for column in df.columns:

    if column != "district":

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# ROUND
# ============================================================

numeric_columns = df.select_dtypes(
    include="number"
).columns

df[numeric_columns] = (
    df[numeric_columns]
    .round(3)
)


# ============================================================
# SAVE CSV
# ============================================================

csv_path = CACHE_DIR / "district_metrics.csv"

df.to_csv(
    csv_path,
    index=False
)


# ============================================================
# SAVE JSON
# ============================================================

json_path = CACHE_DIR / "district_metrics.json"

json_records = (
    df.where(
        pd.notna(df),
        None
    )
    .to_dict(
        orient="records"
    )
)

with open(
    json_path,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        json_records,
        f,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL DASHBOARD DATA")
print("=" * 70)

display_columns = [
    "district",
    "flooded_area_km2",
    "flooded_area_percent",
    "cropland_affected_percent",
    "forest_affected_percent",
    "flood_period_rainfall_mm",
    "maximum_daily_rainfall_mm",
    "mean_elevation_m",
    "mean_slope_degrees",
    "flood_affected_buildings",
    "buildings_affected_percent",
    "flood_affected_road_length_km",
    "road_affected_percent",
]

print(
    df[display_columns]
    .to_string(index=False)
)


print("\n" + "=" * 70)
print("DATA COMPLETENESS")
print("=" * 70)

for column in display_columns:

    if column == "district":
        continue

    missing = df[column].isna().sum()

    if missing == 0:

        print(
            f"✓ {column}"
        )

    else:

        print(
            f"⚠ {column}: {missing} missing"
        )


print("\n" + "=" * 70)
print("FILES CREATED")
print("=" * 70)

print(csv_path)
print(json_path)

print("\n✅ Dashboard data preparation complete.")