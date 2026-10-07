# import pandas as pd
# import json
# from pathlib import Path


# # ============================================================
# # ASSAM FLOOD INTELLIGENCE
# # MASTER DASHBOARD DATA PREPARATION
# # ============================================================

# PROJECT_ROOT = Path(r"D:\PORTFOLIO PROJECT\Assam Flood")

# OUTPUT_DIR = PROJECT_ROOT / "Output"
# CACHE_DIR = PROJECT_ROOT / "Cache" / "dashboard_data"

# CACHE_DIR.mkdir(parents=True, exist_ok=True)


# # ============================================================
# # CURRENT PROJECT SCOPE
# # ============================================================

# DISTRICTS = [
#     "Biswanath",
#     "Charaideo",
#     "Darrang",
#     "Golaghat",
#     "Hojai",
#     "Jorhat",
#     "Nagaon",
#     "Sivasagar",
#     "Sonitpur",
# ]


# # ============================================================
# # HELPERS
# # ============================================================

# def read_first_row(path):
#     """Read CSV and return the first row as a dictionary."""
#     df = pd.read_csv(path)

#     if df.empty:
#         raise ValueError(f"CSV is empty: {path}")

#     return df.iloc[0].to_dict()


# def get_value(row, column, default=None):
#     """Safely retrieve a value."""
#     value = row.get(column, default)

#     if pd.isna(value):
#         return default

#     return value


# def number(value):
#     """Convert numeric values to normal Python numbers."""
#     if value is None:
#         return None

#     try:
#         value = float(value)

#         if value.is_integer():
#             return int(value)

#         return round(value, 6)

#     except (TypeError, ValueError):
#         return value


# def find_column(row, candidates):
#     """Find the first matching column from candidate names."""
#     for column in candidates:
#         if column in row:
#             return column

#     return None


# def value_from_candidates(row, candidates, default=None):
#     """Get value using several possible column names."""
#     column = find_column(row, candidates)

#     if column is None:
#         return default

#     return get_value(row, column, default)


# # ============================================================
# # START
# # ============================================================

# print("=" * 75)
# print("ASSAM FLOOD INTELLIGENCE")
# print("MASTER DASHBOARD DATA PREPARATION")
# print("=" * 75)

# print("\nCurrent project districts:")

# for district in DISTRICTS:
#     print(f"  ✓ {district}")


# # ============================================================
# # PROCESS DISTRICTS
# # ============================================================

# records = []

# for district in DISTRICTS:

#     print("\n" + "-" * 75)
#     print(district)
#     print("-" * 75)

#     flood_file = OUTPUT_DIR / f"{district}_flood_intelligence_summary.csv"
#     building_file = OUTPUT_DIR / f"{district}_building_summary.csv"
#     road_file = OUTPUT_DIR / f"{district}_road_summary.csv"
#     rainfall_file = OUTPUT_DIR / f"{district}_daily_rainfall.csv"

#     # --------------------------------------------------------
#     # Check files
#     # --------------------------------------------------------

#     for file in [flood_file, building_file, road_file, rainfall_file]:
#         if not file.exists():
#             print(f"⚠ Missing: {file.name}")

#     if not flood_file.exists():
#         print("✗ Cannot process district without flood summary")
#         continue

#     # --------------------------------------------------------
#     # Read flood summary
#     # --------------------------------------------------------

#     flood = read_first_row(flood_file)

#     # --------------------------------------------------------
#     # Read building summary
#     # --------------------------------------------------------

#     building = {}

#     if building_file.exists():
#         building = read_first_row(building_file)

#     # --------------------------------------------------------
#     # Read road summary
#     # --------------------------------------------------------

#     road = {}

#     if road_file.exists():
#         road = read_first_row(road_file)

#     # ========================================================
#     # FLOOD
#     # ========================================================

#     district_area = number(
#         get_value(flood, "district_area_km2")
#     )

#     flooded_area = number(
#         get_value(flood, "flooded_area_km2")
#     )

#     flooded_area_percent = number(
#         get_value(flood, "flooded_area_percent")
#     )

#     # ========================================================
#     # CROPLAND
#     # ========================================================

#     total_cropland = number(
#         get_value(flood, "total_cropland_km2")
#     )

#     flooded_cropland = number(
#         get_value(flood, "flooded_cropland_km2")
#     )

#     cropland_percent = number(
#         get_value(flood, "cropland_affected_percent")
#     )

#     # ========================================================
#     # FOREST
#     # ========================================================

#     total_forest = number(
#         get_value(flood, "total_forest_km2")
#     )

#     flooded_forest = number(
#         get_value(flood, "flooded_forest_km2")
#     )

#     forest_percent = number(
#         get_value(flood, "forest_affected_percent")
#     )

#     # ========================================================
#     # RAINFALL
#     # ========================================================

#     rainfall_total = number(
#         get_value(flood, "flood_period_rainfall_mm")
#     )

#     maximum_daily_rainfall = number(
#         get_value(flood, "maximum_daily_rainfall_mm")
#     )

#     rainfall_days = number(
#         get_value(flood, "rainfall_days")
#     )

#     # ========================================================
#     # TOPOGRAPHY
#     # ========================================================

#     mean_elevation = number(
#         get_value(flood, "mean_elevation_m")
#     )

#     minimum_elevation = number(
#         get_value(flood, "minimum_elevation_m")
#     )

#     maximum_elevation = number(
#         get_value(flood, "maximum_elevation_m")
#     )

#     mean_slope = number(
#         get_value(flood, "mean_slope_degrees")
#     )

#     minimum_slope = number(
#         get_value(flood, "minimum_slope_degrees")
#     )

#     maximum_slope = number(
#         get_value(flood, "maximum_slope_degrees")
#     )

#     # ========================================================
#     # BUILDINGS
#     # ========================================================

#     total_buildings = value_from_candidates(
#         flood,
#         [
#             "total_osm_mapped_buildings",
#             "total_buildings",
#             "mapped_buildings",
#         ],
#         None,
#     )

#     affected_buildings = value_from_candidates(
#         flood,
#         [
#             "flood_affected_buildings",
#             "affected_buildings",
#             "flooded_buildings",
#         ],
#         None,
#     )

#     buildings_percent = value_from_candidates(
#         flood,
#         [
#             "buildings_affected_percent",
#             "building_affected_percent",
#             "affected_buildings_percent",
#         ],
#         None,
#     )

#     # If flood summary doesn't contain infrastructure,
#     # use the separate building summary.

#     if total_buildings is None:
#         total_buildings = value_from_candidates(
#             building,
#             [
#                 "total_osm_mapped_buildings",
#                 "total_buildings",
#                 "mapped_buildings",
#             ],
#             None,
#         )

#     if affected_buildings is None:
#         affected_buildings = value_from_candidates(
#             building,
#             [
#                 "flood_affected_buildings",
#                 "affected_buildings",
#                 "flooded_buildings",
#             ],
#             None,
#         )

#     if buildings_percent is None:
#         buildings_percent = value_from_candidates(
#             building,
#             [
#                 "buildings_affected_percent",
#                 "building_affected_percent",
#                 "affected_buildings_percent",
#             ],
#             None,
#         )

#     total_buildings = number(total_buildings)
#     affected_buildings = number(affected_buildings)
#     buildings_percent = number(buildings_percent)

#     # Calculate percentage if necessary

#     if (
#         buildings_percent is None
#         and total_buildings not in [None, 0]
#         and affected_buildings is not None
#     ):
#         buildings_percent = round(
#             (affected_buildings / total_buildings) * 100,
#             6,
#         )

#     # ========================================================
#     # ROADS
#     # ========================================================

#     total_road_length = value_from_candidates(
#         flood,
#         [
#             "total_osm_mapped_road_length_km",
#             "total_road_length_km",
#             "total_mapped_road_length_km",
#         ],
#         None,
#     )

#     affected_road_length = value_from_candidates(
#         flood,
#         [
#             "flood_affected_road_length_km",
#             "affected_road_length_km",
#             "flooded_road_length_km",
#         ],
#         None,
#     )

#     road_percent = value_from_candidates(
#         flood,
#         [
#             "road_affected_percent",
#             "roads_affected_percent",
#             "affected_road_percent",
#         ],
#         None,
#     )

#     # Use separate road summary if required

#     if total_road_length is None:
#         total_road_length = value_from_candidates(
#             road,
#             [
#                 "total_osm_mapped_road_length_km",
#                 "total_road_length_km",
#                 "total_mapped_road_length_km",
#             ],
#             None,
#         )

#     if affected_road_length is None:
#         affected_road_length = value_from_candidates(
#             road,
#             [
#                 "flood_affected_road_length_km",
#                 "affected_road_length_km",
#                 "flooded_road_length_km",
#             ],
#             None,
#         )

#     if road_percent is None:
#         road_percent = value_from_candidates(
#             road,
#             [
#                 "road_affected_percent",
#                 "roads_affected_percent",
#                 "affected_road_percent",
#             ],
#             None,
#         )

#     total_road_length = number(total_road_length)
#     affected_road_length = number(affected_road_length)
#     road_percent = number(road_percent)

#     if (
#         road_percent is None
#         and total_road_length not in [None, 0]
#         and affected_road_length is not None
#     ):
#         road_percent = round(
#             (affected_road_length / total_road_length) * 100,
#             6,
#         )

#     # ========================================================
#     # LAND COVER WITHIN FLOODED AREA
#     # ========================================================

#     cropland_in_flood_percent = None
#     forest_in_flood_percent = None
#     other_in_flood_percent = None

#     if flooded_area not in [None, 0]:

#         if flooded_cropland is not None:
#             cropland_in_flood_percent = round(
#                 (flooded_cropland / flooded_area) * 100,
#                 6,
#             )

#         if flooded_forest is not None:
#             forest_in_flood_percent = round(
#                 (flooded_forest / flooded_area) * 100,
#                 6,
#             )

#         if (
#             cropland_in_flood_percent is not None
#             and forest_in_flood_percent is not None
#         ):
#             other_in_flood_percent = round(
#                 100
#                 - cropland_in_flood_percent
#                 - forest_in_flood_percent,
#                 6,
#             )

#     # ========================================================
#     # RECORD
#     # ========================================================

#     record = {
#         "district": district,

#         "flood": {
#             "district_area_km2": district_area,
#             "flooded_area_km2": flooded_area,
#             "flooded_area_percent": flooded_area_percent,
#         },

#         "agriculture": {
#             "total_cropland_km2": total_cropland,
#             "flooded_cropland_km2": flooded_cropland,
#             "affected_percent": cropland_percent,
#         },

#         "forest": {
#             "total_forest_km2": total_forest,
#             "flooded_forest_km2": flooded_forest,
#             "affected_percent": forest_percent,
#         },

#         "buildings": {
#             "total_mapped": total_buildings,
#             "affected": affected_buildings,
#             "affected_percent": buildings_percent,
#         },

#         "roads": {
#             "total_length_km": total_road_length,
#             "affected_length_km": affected_road_length,
#             "affected_percent": road_percent,
#         },

#         "rainfall": {
#             "flood_period_total_mm": rainfall_total,
#             "maximum_daily_mm": maximum_daily_rainfall,
#             "rainfall_days": rainfall_days,
#         },

#         "topography": {
#             "mean_elevation_m": mean_elevation,
#             "minimum_elevation_m": minimum_elevation,
#             "maximum_elevation_m": maximum_elevation,
#             "mean_slope_degrees": mean_slope,
#             "minimum_slope_degrees": minimum_slope,
#             "maximum_slope_degrees": maximum_slope,
#         },

#         "flooded_area_land_cover": {
#             "cropland_percent": cropland_in_flood_percent,
#             "forest_percent": forest_in_flood_percent,
#             "other_percent": other_in_flood_percent,
#         },
#     }

#     records.append(record)

#     print("✓ Flood metrics loaded")
#     print("✓ Agriculture metrics loaded")
#     print("✓ Forest metrics loaded")
#     print("✓ Building metrics loaded")
#     print("✓ Road metrics loaded")
#     print("✓ Rainfall metrics loaded")
#     print("✓ Topography metrics loaded")


# # ============================================================
# # SAVE MASTER JSON
# # ============================================================

# json_path = CACHE_DIR / "master_dashboard_data.json"

# with open(json_path, "w", encoding="utf-8") as f:
#     json.dump(
#         records,
#         f,
#         indent=2,
#         ensure_ascii=False,
#     )


# # ============================================================
# # CREATE FLAT CSV
# # ============================================================

# flat_records = []

# for item in records:

#     flat_records.append({
#         "district": item["district"],

#         "district_area_km2":
#             item["flood"]["district_area_km2"],

#         "flooded_area_km2":
#             item["flood"]["flooded_area_km2"],

#         "flooded_area_percent":
#             item["flood"]["flooded_area_percent"],

#         "total_cropland_km2":
#             item["agriculture"]["total_cropland_km2"],

#         "flooded_cropland_km2":
#             item["agriculture"]["flooded_cropland_km2"],

#         "cropland_affected_percent":
#             item["agriculture"]["affected_percent"],

#         "total_forest_km2":
#             item["forest"]["total_forest_km2"],

#         "flooded_forest_km2":
#             item["forest"]["flooded_forest_km2"],

#         "forest_affected_percent":
#             item["forest"]["affected_percent"],

#         "total_buildings":
#             item["buildings"]["total_mapped"],

#         "affected_buildings":
#             item["buildings"]["affected"],

#         "buildings_affected_percent":
#             item["buildings"]["affected_percent"],

#         "total_road_length_km":
#             item["roads"]["total_length_km"],

#         "affected_road_length_km":
#             item["roads"]["affected_length_km"],

#         "road_affected_percent":
#             item["roads"]["affected_percent"],

#         "flood_period_rainfall_mm":
#             item["rainfall"]["flood_period_total_mm"],

#         "maximum_daily_rainfall_mm":
#             item["rainfall"]["maximum_daily_mm"],

#         "rainfall_days":
#             item["rainfall"]["rainfall_days"],

#         "mean_elevation_m":
#             item["topography"]["mean_elevation_m"],

#         "minimum_elevation_m":
#             item["topography"]["minimum_elevation_m"],

#         "maximum_elevation_m":
#             item["topography"]["maximum_elevation_m"],

#         "mean_slope_degrees":
#             item["topography"]["mean_slope_degrees"],

#         "minimum_slope_degrees":
#             item["topography"]["minimum_slope_degrees"],

#         "maximum_slope_degrees":
#             item["topography"]["maximum_slope_degrees"],

#         "cropland_in_flood_percent":
#             item["flooded_area_land_cover"]["cropland_percent"],

#         "forest_in_flood_percent":
#             item["flooded_area_land_cover"]["forest_percent"],

#         "other_in_flood_percent":
#             item["flooded_area_land_cover"]["other_percent"],
#     })


# csv_path = CACHE_DIR / "master_dashboard_data.csv"

# pd.DataFrame(flat_records).to_csv(
#     csv_path,
#     index=False,
# )


# # ============================================================
# # VALIDATION
# # ============================================================

# print("\n" + "=" * 75)
# print("MASTER DASHBOARD DATA PREPARATION COMPLETE")
# print("=" * 75)

# print(f"\nDistricts processed: {len(records)} / {len(DISTRICTS)}")

# print("\nDistricts included:")

# for record in records:
#     print(f"  ✓ {record['district']}")

# print("\nFiles created:")

# print(f"  ✓ {json_path}")
# print(f"  ✓ {csv_path}")

# print("\nDashboard data includes:")

# print("  ✓ Flood extent")
# print("  ✓ Flood percentage")
# print("  ✓ Cropland area and impact")
# print("  ✓ Forest area and impact")
# print("  ✓ Buildings")
# print("  ✓ Roads")
# print("  ✓ Rainfall")
# print("  ✓ Elevation")
# print("  ✓ Slope")
# print("  ✓ Land-cover breakdown")

# print("\nExcluded from current project:")
# print("  ✗ Lakhimpur")
# print("  ✗ Karbi Anglong")

# print("\n" + "=" * 75).








import pandas as pd
import json
from pathlib import Path


# ============================================================
# ASSAM FLOOD INTELLIGENCE
# MASTER DASHBOARD DATA PREPARATION
# ============================================================


# ============================================================
# SECTION 1 — PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(
    r"D:\PORTFOLIO PROJECT\Assam Flood"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "Output"
)

CACHE_DIR = (
    PROJECT_ROOT
    / "Cache"
    / "dashboard_data"
)

CACHE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SECTION 2 — CURRENT PROJECT SCOPE
# ============================================================

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
# OVERVIEW SOURCE FILES
# ============================================================

# Assam-wide rainfall:
#
# Created by:
# GEE/Assam_Rainfall.py
#
# This contains the Assam-wide daily rainfall
# during the flood period.

ASSAM_RAINFALL_FILE = (
    OUTPUT_DIR
    / "Assam_daily_rainfall.csv"
)


# Nine-district land-cover aggregation:
#
# Created by:
# GEE/Assam_Overview_Landcover.py
#
# IMPORTANT:
# That script reads the individual district
# flood-intelligence CSVs.
#
# It does NOT use:
# assam_flood_intelligence_master.csv

ASSAM_LANDCOVER_FILE = (
    OUTPUT_DIR
    / "Assam_overview_landcover.json"
)


# ============================================================
# HELPERS
# ============================================================

def read_first_row(path):
    """
    Read CSV and return the first row as a dictionary.
    """

    df = pd.read_csv(
        path
    )

    if df.empty:

        raise ValueError(
            f"CSV is empty: {path}"
        )

    return (
        df.iloc[0]
        .to_dict()
    )


def get_value(
    row,
    column,
    default=None
):
    """
    Safely retrieve a value.
    """

    value = row.get(
        column,
        default
    )

    if pd.isna(value):

        return default

    return value


def number(value):
    """
    Convert numeric values to normal
    Python numbers.
    """

    if value is None:

        return None

    try:

        value = float(
            value
        )

        if value.is_integer():

            return int(
                value
            )

        return round(
            value,
            6
        )

    except (
        TypeError,
        ValueError
    ):

        return value


def find_column(
    row,
    candidates
):
    """
    Find the first matching column
    from candidate names.
    """

    for column in candidates:

        if column in row:

            return column

    return None


def value_from_candidates(
    row,
    candidates,
    default=None
):
    """
    Get value using several possible
    column names.
    """

    column = find_column(
        row,
        candidates
    )

    if column is None:

        return default

    return get_value(
        row,
        column,
        default
    )


# ============================================================
# OVERVIEW — ASSAM-WIDE RAINFALL
# ============================================================

def prepare_assam_rainfall():

    print()
    print("=" * 75)
    print("OVERVIEW — ASSAM-WIDE RAINFALL")
    print("=" * 75)

    print()
    print(
        "Reading:",
        ASSAM_RAINFALL_FILE
    )

    if not ASSAM_RAINFALL_FILE.exists():

        raise FileNotFoundError(

            "\nAssam-wide rainfall file not found:\n"
            f"{ASSAM_RAINFALL_FILE}\n\n"

            "Run GEE/Assam_Rainfall.py first."
        )


    # --------------------------------------------------------
    # READ CSV
    # --------------------------------------------------------

    rainfall_df = pd.read_csv(
        ASSAM_RAINFALL_FILE
    )


    if rainfall_df.empty:

        raise ValueError(
            "Assam rainfall CSV is empty."
        )


    print(
        "Rows:",
        len(rainfall_df)
    )

    print(
        "Columns:",
        list(rainfall_df.columns)
    )


    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    rainfall_df.columns = [

        str(column).strip()

        for column
        in rainfall_df.columns

    ]


    # --------------------------------------------------------
    # FIND DATE COLUMN
    # --------------------------------------------------------

    date_column = None

    possible_date_columns = [

        "date",
        "Date",
        "DATE",
        "datetime",
        "Datetime",

    ]


    for column in possible_date_columns:

        if column in rainfall_df.columns:

            date_column = column

            break


    if date_column is None:

        raise ValueError(

            "\nCould not identify date column "
            "in Assam rainfall CSV.\n\n"

            f"Available columns:\n"
            f"{list(rainfall_df.columns)}"
        )


    # --------------------------------------------------------
    # FIND RAINFALL COLUMN
    # --------------------------------------------------------

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

        if column in rainfall_df.columns:

            rainfall_column = column

            break


    # --------------------------------------------------------
    # AUTOMATIC RAINFALL COLUMN DETECTION
    # --------------------------------------------------------

    if rainfall_column is None:

        for column in rainfall_df.columns:

            column_key = (

                str(column)
                .lower()
                .replace(
                    "_",
                    ""
                )
                .replace(
                    " ",
                    ""
                )

            )

            if (

                "rainfall"
                in column_key

                or

                "precipitation"
                in column_key

            ):

                rainfall_column = column

                break


    if rainfall_column is None:

        raise ValueError(

            "\nCould not identify rainfall column "
            "in Assam rainfall CSV.\n\n"

            f"Available columns:\n"
            f"{list(rainfall_df.columns)}"
        )


    # --------------------------------------------------------
    # PREPARE DATA
    # --------------------------------------------------------

    rainfall_df = rainfall_df[
        [
            date_column,
            rainfall_column
        ]
    ].copy()


    rainfall_df.columns = [

        "date",
        "rainfall_mm"

    ]


    rainfall_df[
        "date"
    ] = pd.to_datetime(

        rainfall_df[
            "date"
        ],

        errors="coerce"

    )


    rainfall_df[
        "rainfall_mm"
    ] = pd.to_numeric(

        rainfall_df[
            "rainfall_mm"
        ],

        errors="coerce"

    )


    rainfall_df = (

        rainfall_df

        .dropna(
            subset=[
                "date",
                "rainfall_mm"
            ]
        )

        .sort_values(
            "date"
        )

        .reset_index(
            drop=True
        )

    )


    if rainfall_df.empty:

        raise ValueError(
            "No valid Assam rainfall records remain."
        )


    # --------------------------------------------------------
    # FLOOD PERIOD
    # --------------------------------------------------------

    flood_start = (

        rainfall_df[
            "date"
        ]
        .min()
        .strftime(
            "%Y-%m-%d"
        )

    )


    flood_end = (

        rainfall_df[
            "date"
        ]
        .max()
        .strftime(
            "%Y-%m-%d"
        )

    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_rainfall = (

        rainfall_df[
            "rainfall_mm"
        ]
        .sum()

    )


    maximum_daily_rainfall = (

        rainfall_df[
            "rainfall_mm"
        ]
        .max()

    )


    rainfall_days = len(
        rainfall_df
    )


    # --------------------------------------------------------
    # DAILY RECORDS
    # --------------------------------------------------------

    daily_records = []


    for _, row in rainfall_df.iterrows():

        daily_records.append({

            "date":
                row[
                    "date"
                ].strftime(
                    "%Y-%m-%d"
                ),

            "rainfall_mm":
                round(
                    float(
                        row[
                            "rainfall_mm"
                        ]
                    ),
                    3
                ),

        })


    # --------------------------------------------------------
    # BUILD OVERVIEW RAINFALL OBJECT
    # --------------------------------------------------------

    rainfall_overview = {

        "scope": {

            "description":
                "Assam-wide rainfall during "
                "the flood period",

            "area":
                "Entire Assam",

        },


        "flood_period": {

            "start":
                flood_start,

            "end":
                flood_end,

            "days":
                rainfall_days,

        },


        "summary": {

            "accumulated_rainfall_mm":
                round(
                    float(
                        total_rainfall
                    ),
                    3
                ),

            "maximum_daily_rainfall_mm":
                round(
                    float(
                        maximum_daily_rainfall
                    ),
                    3
                ),

            "rainfall_days":
                rainfall_days,

        },


        "daily":
            daily_records,

    }


    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()

    print(
        "✓ Assam rainfall loaded"
    )

    print(
        "  Flood period:",
        flood_start,
        "to",
        flood_end
    )

    print(
        "  Days:",
        rainfall_days
    )

    print(
        "  Accumulated rainfall:",
        round(
            float(
                total_rainfall
            ),
            3
        ),
        "mm"
    )

    print(
        "  Maximum daily rainfall:",
        round(
            float(
                maximum_daily_rainfall
            ),
            3
        ),
        "mm"
    )


    return rainfall_overview


# ============================================================
# OVERVIEW — NINE-DISTRICT LAND COVER
# ============================================================

def prepare_assam_landcover():

    print()
    print("=" * 75)
    print("OVERVIEW — FLOOD-AFFECTED LAND COVER")
    print("=" * 75)

    print()
    print(
        "Reading:",
        ASSAM_LANDCOVER_FILE
    )

    if not ASSAM_LANDCOVER_FILE.exists():

        raise FileNotFoundError(

            "\nAssam overview land-cover file not found:\n"
            f"{ASSAM_LANDCOVER_FILE}\n\n"

            "Run GEE/Assam_Overview_Landcover.py first."
        )


    # --------------------------------------------------------
    # READ EXISTING JSON
    # --------------------------------------------------------

    with open(
        ASSAM_LANDCOVER_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        landcover = json.load(
            file
        )


    # --------------------------------------------------------
    # VALIDATE STRUCTURE
    # --------------------------------------------------------

    if not isinstance(
        landcover,
        dict
    ):

        raise ValueError(

            "Assam overview land-cover JSON "
            "must contain an object."
        )


    required_keys = [

        "scope",
        "total_flooded_area_km2",
        "landcover",

    ]


    missing_keys = [

        key

        for key
        in required_keys

        if key not in landcover

    ]


    if missing_keys:

        raise ValueError(

            "\nAssam overview land-cover JSON "
            "is missing required fields:\n"

            f"{missing_keys}"
        )


    # --------------------------------------------------------
    # VALIDATE DISTRICT SCOPE
    # --------------------------------------------------------

    scope = landcover.get(
        "scope",
        {}
    )


    source_districts = (

        scope.get(
            "districts",
            []
        )

    )


    if source_districts:

        source_set = set(
            source_districts
        )

        expected_set = set(
            DISTRICTS
        )

        if source_set != expected_set:

            raise ValueError(

                "\nLand-cover overview district "
                "scope does not match the "
                "current dashboard districts.\n\n"

                f"Expected:\n{DISTRICTS}\n\n"

                f"Found:\n{source_districts}"
            )


    # --------------------------------------------------------
    # VALIDATE LAND-COVER CATEGORIES
    # --------------------------------------------------------

    landcover_records = (
        landcover.get(
            "landcover",
            []
        )
    )


    if not isinstance(
        landcover_records,
        list
    ):

        raise ValueError(
            "Land-cover data must be a list."
        )


    # --------------------------------------------------------
    # NORMALIZE VALUES
    # --------------------------------------------------------

    normalized_landcover = []


    for item in landcover_records:

        normalized_landcover.append({

            "name":
                item.get(
                    "name"
                ),

            "area_km2":
                number(
                    item.get(
                        "area_km2"
                    )
                ),

            "percentage":
                number(
                    item.get(
                        "percentage"
                    )
                ),

        })


    # --------------------------------------------------------
    # BUILD OBJECT
    # --------------------------------------------------------

    landcover_overview = {

        "scope": {

            "description":
                "Flood-affected land cover "
                "across the 9 analyzed districts",

            "district_count":
                len(DISTRICTS),

            "districts":
                DISTRICTS,

        },


        "total_flooded_area_km2":
            number(
                landcover[
                    "total_flooded_area_km2"
                ]
            ),


        "landcover":
            normalized_landcover,

    }


    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print()

    print(
        "✓ Nine-district land cover loaded"
    )

    print(
        "  Districts:",
        len(DISTRICTS)
    )

    print(
        "  Total flooded area:",
        landcover_overview[
            "total_flooded_area_km2"
        ],
        "km²"
    )


    for item in normalized_landcover:

        print(

            "  "
            + str(
                item[
                    "name"
                ]
            )
            + ":",

            item[
                "area_km2"
            ],

            "km² |",

            item[
                "percentage"
            ],

            "%"

        )


    return landcover_overview


# ============================================================
# START
# ============================================================

print(
    "=" * 75
)

print(
    "ASSAM FLOOD INTELLIGENCE"
)

print(
    "MASTER DASHBOARD DATA PREPARATION"
)

print(
    "=" * 75
)


print(
    "\nProject root:"
)

print(
    PROJECT_ROOT
)


print(
    "\nCurrent project districts:"
)


for district in DISTRICTS:

    print(
        f"  ✓ {district}"
    )


# ============================================================
# PREPARE OVERVIEW DATA FIRST
# ============================================================

overview_rainfall = (
    prepare_assam_rainfall()
)


overview_landcover = (
    prepare_assam_landcover()
)


# ============================================================
# PROCESS DISTRICTS
# ============================================================

print()
print("=" * 75)
print("PROCESSING DISTRICT DATA")
print("=" * 75)


records = []


for district in DISTRICTS:

    print(
        "\n"
        + "-" * 75
    )

    print(
        district
    )

    print(
        "-" * 75
    )


    # --------------------------------------------------------
    # FILE PATHS
    # --------------------------------------------------------

    flood_file = (

        OUTPUT_DIR
        / f"{district}_flood_intelligence_summary.csv"

    )


    building_file = (

        OUTPUT_DIR
        / f"{district}_building_summary.csv"

    )


    road_file = (

        OUTPUT_DIR
        / f"{district}_road_summary.csv"

    )


    rainfall_file = (

        OUTPUT_DIR
        / f"{district}_daily_rainfall.csv"

    )


    # --------------------------------------------------------
    # CHECK FILES
    # --------------------------------------------------------

    for file in [

        flood_file,
        building_file,
        road_file,
        rainfall_file,

    ]:

        if not file.exists():

            print(
                f"⚠ Missing: {file.name}"
            )


    if not flood_file.exists():

        print(
            "✗ Cannot process district "
            "without flood summary"
        )

        continue


    # --------------------------------------------------------
    # READ FLOOD SUMMARY
    # --------------------------------------------------------

    flood = read_first_row(
        flood_file
    )


    # --------------------------------------------------------
    # READ BUILDING SUMMARY
    # --------------------------------------------------------

    building = {}


    if building_file.exists():

        building = read_first_row(
            building_file
        )


    # --------------------------------------------------------
    # READ ROAD SUMMARY
    # --------------------------------------------------------

    road = {}


    if road_file.exists():

        road = read_first_row(
            road_file
        )


    # ========================================================
    # FLOOD
    # ========================================================

    district_area = number(

        get_value(
            flood,
            "district_area_km2"
        )

    )


    flooded_area = number(

        get_value(
            flood,
            "flooded_area_km2"
        )

    )


    flooded_area_percent = number(

        get_value(
            flood,
            "flooded_area_percent"
        )

    )


    # ========================================================
    # CROPLAND
    # ========================================================

    total_cropland = number(

        get_value(
            flood,
            "total_cropland_km2"
        )

    )


    flooded_cropland = number(

        get_value(
            flood,
            "flooded_cropland_km2"
        )

    )


    cropland_percent = number(

        get_value(
            flood,
            "cropland_affected_percent"
        )

    )


    # ========================================================
    # FOREST
    # ========================================================

    total_forest = number(

        get_value(
            flood,
            "total_forest_km2"
        )

    )


    flooded_forest = number(

        get_value(
            flood,
            "flooded_forest_km2"
        )

    )


    forest_percent = number(

        get_value(
            flood,
            "forest_affected_percent"
        )

    )


    # ========================================================
    # RAINFALL
    # ========================================================

    rainfall_total = number(

        get_value(
            flood,
            "flood_period_rainfall_mm"
        )

    )


    maximum_daily_rainfall = number(

        get_value(
            flood,
            "maximum_daily_rainfall_mm"
        )

    )


    rainfall_days = number(

        get_value(
            flood,
            "rainfall_days"
        )

    )


    # ========================================================
    # TOPOGRAPHY
    # ========================================================

    mean_elevation = number(

        get_value(
            flood,
            "mean_elevation_m"
        )

    )


    minimum_elevation = number(

        get_value(
            flood,
            "minimum_elevation_m"
        )

    )


    maximum_elevation = number(

        get_value(
            flood,
            "maximum_elevation_m"
        )

    )


    mean_slope = number(

        get_value(
            flood,
            "mean_slope_degrees"
        )

    )


    minimum_slope = number(

        get_value(
            flood,
            "minimum_slope_degrees"
        )

    )


    maximum_slope = number(

        get_value(
            flood,
            "maximum_slope_degrees"
        )

    )


    # ========================================================
    # BUILDINGS
    # ========================================================

    total_buildings = value_from_candidates(

        flood,

        [

            "total_osm_mapped_buildings",
            "total_buildings",
            "mapped_buildings",

        ],

        None,

    )


    affected_buildings = value_from_candidates(

        flood,

        [

            "flood_affected_buildings",
            "affected_buildings",
            "flooded_buildings",

        ],

        None,

    )


    buildings_percent = value_from_candidates(

        flood,

        [

            "buildings_affected_percent",
            "building_affected_percent",
            "affected_buildings_percent",

        ],

        None,

    )


    # --------------------------------------------------------
    # BUILDING FALLBACK
    # --------------------------------------------------------

    if total_buildings is None:

        total_buildings = (
            value_from_candidates(

                building,

                [

                    "total_osm_mapped_buildings",
                    "total_buildings",
                    "mapped_buildings",

                ],

                None,

            )
        )


    if affected_buildings is None:

        affected_buildings = (
            value_from_candidates(

                building,

                [

                    "flood_affected_buildings",
                    "affected_buildings",
                    "flooded_buildings",

                ],

                None,

            )
        )


    if buildings_percent is None:

        buildings_percent = (
            value_from_candidates(

                building,

                [

                    "buildings_affected_percent",
                    "building_affected_percent",
                    "affected_buildings_percent",

                ],

                None,

            )
        )


    total_buildings = number(
        total_buildings
    )


    affected_buildings = number(
        affected_buildings
    )


    buildings_percent = number(
        buildings_percent
    )


    # --------------------------------------------------------
    # CALCULATE BUILDING PERCENTAGE IF REQUIRED
    # --------------------------------------------------------

    if (

        buildings_percent is None

        and

        total_buildings
        not in [None, 0]

        and

        affected_buildings
        is not None

    ):

        buildings_percent = round(

            (
                affected_buildings
                /
                total_buildings
            )
            * 100,

            6,

        )


    # ========================================================
    # ROADS
    # ========================================================

    total_road_length = (
        value_from_candidates(

            flood,

            [

                "total_osm_mapped_road_length_km",
                "total_road_length_km",
                "total_mapped_road_length_km",

            ],

            None,

        )
    )


    affected_road_length = (
        value_from_candidates(

            flood,

            [

                "flood_affected_road_length_km",
                "affected_road_length_km",
                "flooded_road_length_km",

            ],

            None,

        )
    )


    road_percent = (
        value_from_candidates(

            flood,

            [

                "road_affected_percent",
                "roads_affected_percent",
                "affected_road_percent",

            ],

            None,

        )
    )


    # --------------------------------------------------------
    # ROAD FALLBACK
    # --------------------------------------------------------

    if total_road_length is None:

        total_road_length = (
            value_from_candidates(

                road,

                [

                    "total_osm_mapped_road_length_km",
                    "total_road_length_km",
                    "total_mapped_road_length_km",

                ],

                None,

            )
        )


    if affected_road_length is None:

        affected_road_length = (
            value_from_candidates(

                road,

                [

                    "flood_affected_road_length_km",
                    "affected_road_length_km",
                    "flooded_road_length_km",

                ],

                None,

            )
        )


    if road_percent is None:

        road_percent = (
            value_from_candidates(

                road,

                [

                    "road_affected_percent",
                    "roads_affected_percent",
                    "affected_road_percent",

                ],

                None,

            )
        )


    total_road_length = number(
        total_road_length
    )


    affected_road_length = number(
        affected_road_length
    )


    road_percent = number(
        road_percent
    )


    # --------------------------------------------------------
    # CALCULATE ROAD PERCENTAGE IF REQUIRED
    # --------------------------------------------------------

    if (

        road_percent is None

        and

        total_road_length
        not in [None, 0]

        and

        affected_road_length
        is not None

    ):

        road_percent = round(

            (
                affected_road_length
                /
                total_road_length
            )
            * 100,

            6,

        )


    # ========================================================
    # LAND COVER WITHIN FLOODED AREA
    # ========================================================

    cropland_in_flood_percent = None

    forest_in_flood_percent = None

    other_in_flood_percent = None


    if flooded_area not in [None, 0]:

        if flooded_cropland is not None:

            cropland_in_flood_percent = round(

                (
                    flooded_cropland
                    /
                    flooded_area
                )
                * 100,

                6,

            )


        if flooded_forest is not None:

            forest_in_flood_percent = round(

                (
                    flooded_forest
                    /
                    flooded_area
                )
                * 100,

                6,

            )


        if (

            cropland_in_flood_percent
            is not None

            and

            forest_in_flood_percent
            is not None

        ):

            other_in_flood_percent = round(

                100

                - cropland_in_flood_percent

                - forest_in_flood_percent,

                6,

            )


    # ========================================================
    # DISTRICT RECORD
    # ========================================================

    record = {

        "district":
            district,


        "flood": {

            "district_area_km2":
                district_area,

            "flooded_area_km2":
                flooded_area,

            "flooded_area_percent":
                flooded_area_percent,

        },


        "agriculture": {

            "total_cropland_km2":
                total_cropland,

            "flooded_cropland_km2":
                flooded_cropland,

            "affected_percent":
                cropland_percent,

        },


        "forest": {

            "total_forest_km2":
                total_forest,

            "flooded_forest_km2":
                flooded_forest,

            "affected_percent":
                forest_percent,

        },


        "buildings": {

            "total_mapped":
                total_buildings,

            "affected":
                affected_buildings,

            "affected_percent":
                buildings_percent,

        },


        "roads": {

            "total_length_km":
                total_road_length,

            "affected_length_km":
                affected_road_length,

            "affected_percent":
                road_percent,

        },


        "rainfall": {

            "flood_period_total_mm":
                rainfall_total,

            "maximum_daily_mm":
                maximum_daily_rainfall,

            "rainfall_days":
                rainfall_days,

        },


        "topography": {

            "mean_elevation_m":
                mean_elevation,

            "minimum_elevation_m":
                minimum_elevation,

            "maximum_elevation_m":
                maximum_elevation,

            "mean_slope_degrees":
                mean_slope,

            "minimum_slope_degrees":
                minimum_slope,

            "maximum_slope_degrees":
                maximum_slope,

        },


        "flooded_area_land_cover": {

            "cropland_percent":
                cropland_in_flood_percent,

            "forest_percent":
                forest_in_flood_percent,

            "other_percent":
                other_in_flood_percent,

        },

    }


    records.append(
        record
    )


    print(
        "✓ Flood metrics loaded"
    )

    print(
        "✓ Agriculture metrics loaded"
    )

    print(
        "✓ Forest metrics loaded"
    )

    print(
        "✓ Building metrics loaded"
    )

    print(
        "✓ Road metrics loaded"
    )

    print(
        "✓ Rainfall metrics loaded"
    )

    print(
        "✓ Topography metrics loaded"
    )


# ============================================================
# VALIDATE DISTRICTS
# ============================================================

processed_districts = [

    record[
        "district"
    ]

    for record
    in records

]


missing_districts = [

    district

    for district
    in DISTRICTS

    if district
    not in processed_districts

]


if missing_districts:

    print()

    print(
        "⚠ WARNING:"
    )

    print(
        "The following districts "
        "could not be processed:"
    )


    for district in missing_districts:

        print(
            f"  ✗ {district}"
        )


# ============================================================
# BUILD MASTER DASHBOARD OBJECT
# ============================================================

master_dashboard = {

    # ========================================================
    # OVERVIEW
    # ========================================================

    "overview": {

        # ----------------------------------------------------
        # ASSAM-WIDE RAINFALL
        # ----------------------------------------------------

        "rainfall":
            overview_rainfall,


        # ----------------------------------------------------
        # NINE-DISTRICT LAND COVER
        # ----------------------------------------------------

        "landcover":
            overview_landcover,

    },


    # ========================================================
    # DISTRICT DATA
    # ========================================================

    "districts":
        records,

}


# ============================================================
# SAVE MASTER JSON
# ============================================================

json_path = (

    CACHE_DIR
    / "master_dashboard_data.json"

)


with open(

    json_path,

    "w",

    encoding="utf-8"

) as f:

    json.dump(

        master_dashboard,

        f,

        indent=2,

        ensure_ascii=False,

    )


# ============================================================
# CREATE FLAT CSV
# ============================================================

flat_records = []


for item in records:

    flat_records.append({

        "district":
            item[
                "district"
            ],


        "district_area_km2":
            item[
                "flood"
            ][
                "district_area_km2"
            ],


        "flooded_area_km2":
            item[
                "flood"
            ][
                "flooded_area_km2"
            ],


        "flooded_area_percent":
            item[
                "flood"
            ][
                "flooded_area_percent"
            ],


        "total_cropland_km2":
            item[
                "agriculture"
            ][
                "total_cropland_km2"
            ],


        "flooded_cropland_km2":
            item[
                "agriculture"
            ][
                "flooded_cropland_km2"
            ],


        "cropland_affected_percent":
            item[
                "agriculture"
            ][
                "affected_percent"
            ],


        "total_forest_km2":
            item[
                "forest"
            ][
                "total_forest_km2"
            ],


        "flooded_forest_km2":
            item[
                "forest"
            ][
                "flooded_forest_km2"
            ],


        "forest_affected_percent":
            item[
                "forest"
            ][
                "affected_percent"
            ],


        "total_buildings":
            item[
                "buildings"
            ][
                "total_mapped"
            ],


        "affected_buildings":
            item[
                "buildings"
            ][
                "affected"
            ],


        "buildings_affected_percent":
            item[
                "buildings"
            ][
                "affected_percent"
            ],


        "total_road_length_km":
            item[
                "roads"
            ][
                "total_length_km"
            ],


        "affected_road_length_km":
            item[
                "roads"
            ][
                "affected_length_km"
            ],


        "road_affected_percent":
            item[
                "roads"
            ][
                "affected_percent"
            ],


        "flood_period_rainfall_mm":
            item[
                "rainfall"
            ][
                "flood_period_total_mm"
            ],


        "maximum_daily_rainfall_mm":
            item[
                "rainfall"
            ][
                "maximum_daily_mm"
            ],


        "rainfall_days":
            item[
                "rainfall"
            ][
                "rainfall_days"
            ],


        "mean_elevation_m":
            item[
                "topography"
            ][
                "mean_elevation_m"
            ],


        "minimum_elevation_m":
            item[
                "topography"
            ][
                "minimum_elevation_m"
            ],


        "maximum_elevation_m":
            item[
                "topography"
            ][
                "maximum_elevation_m"
            ],


        "mean_slope_degrees":
            item[
                "topography"
            ][
                "mean_slope_degrees"
            ],


        "minimum_slope_degrees":
            item[
                "topography"
            ][
                "minimum_slope_degrees"
            ],


        "maximum_slope_degrees":
            item[
                "topography"
            ][
                "maximum_slope_degrees"
            ],


        "cropland_in_flood_percent":
            item[
                "flooded_area_land_cover"
            ][
                "cropland_percent"
            ],


        "forest_in_flood_percent":
            item[
                "flooded_area_land_cover"
            ][
                "forest_percent"
            ],


        "other_in_flood_percent":
            item[
                "flooded_area_land_cover"
            ][
                "other_percent"
            ],

    })


# ============================================================
# SAVE MASTER CSV
# ============================================================

csv_path = (

    CACHE_DIR
    / "master_dashboard_data.csv"

)


pd.DataFrame(
    flat_records
).to_csv(

    csv_path,

    index=False,

)


# ============================================================
# FINAL VALIDATION
# ============================================================

print()
print("=" * 75)
print(
    "MASTER DASHBOARD DATA PREPARATION COMPLETE"
)
print("=" * 75)


print()

print(
    "Districts processed:",
    len(records),
    "/",
    len(DISTRICTS)
)


print()

print(
    "Districts included:"
)


for record in records:

    print(
        f"  ✓ {record['district']}"
    )


print()

print(
    "Overview data included:"
)


print(
    "  ✓ Assam-wide rainfall"
)

print(
    "  ✓ Assam rainfall daily time series"
)

print(
    "  ✓ Assam rainfall summary"
)

print(
    "  ✓ Nine-district flooded land cover"
)

print(
    "  ✓ Cropland"
)

print(
    "  ✓ Forest"
)

print(
    "  ✓ Other"
)


print()

print(
    "District data included:"
)

print(
    "  ✓ Flood extent"
)

print(
    "  ✓ Flood percentage"
)

print(
    "  ✓ Cropland area and impact"
)

print(
    "  ✓ Forest area and impact"
)

print(
    "  ✓ Buildings"
)

print(
    "  ✓ Roads"
)

print(
    "  ✓ District rainfall"
)

print(
    "  ✓ Elevation"
)

print(
    "  ✓ Slope"
)

print(
    "  ✓ District land-cover breakdown"
)


print()

print(
    "Files created:"
)


print(
    f"  ✓ {json_path}"
)


print(
    f"  ✓ {csv_path}"
)


print()

print(
    "Excluded from current project:"
)

print(
    "  ✗ Lakhimpur"
)

print(
    "  ✗ Karbi Anglong"
)


print()

print("=" * 75)