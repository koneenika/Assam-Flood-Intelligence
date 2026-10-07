# ============================================================
# ASSAM FLOOD INTELLIGENCE
# OVERVIEW — FLOOD-AFFECTED LAND COVER
#
# PURPOSE
# -------
# Aggregate the EXISTING individual district flood-analysis
# CSV files for the 9 analyzed districts.
#
# IMPORTANT
# ---------
# This script DOES NOT rerun flood analysis.
#
# It reads ONLY:
#
#   Output/
#       Biswanath_flood_intelligence_summary.csv
#       Charaideo_flood_intelligence_summary.csv
#       Darrang_flood_intelligence_summary.csv
#       Golaghat_flood_intelligence_summary.csv
#       Hojai_flood_intelligence_summary.csv
#       Jorhat_flood_intelligence_summary.csv
#       Nagaon_flood_intelligence_summary.csv
#       Sivasagar_flood_intelligence_summary.csv
#       Sonitpur_flood_intelligence_summary.csv
#
# It DOES NOT use:
#
#   assam_flood_intelligence_master.csv
#
# OVERVIEW SCOPE
# --------------
# Nine analyzed districts only.
#
# OUTPUTS
# -------
# Output/
#   Assam_overview_landcover.csv
#   Assam_overview_landcover_by_district.csv
#   Assam_overview_landcover.json
#
# Output/graphs/
#   Assam_overview_flood_landcover.png
#
# ============================================================


# ============================================================
# SECTION 1 — IMPORTS
# ============================================================

import os
import json

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SECTION 2 — PROJECT PATHS
# ============================================================

# IMPORTANT:
# The actual project structure is:
#
# D:\PORTFOLIO PROJECT\Assam Flood\
#
# ├── GEE\
# │   ├── configuration.py
# │   ├── flood_analysis.py
# │   ├── Assam_Rainfall.py
# │   └── Assam_Overview_Landcover.py
# │
# └── Output\
#     ├── Biswanath_flood_intelligence_summary.csv
#     ├── Charaideo_flood_intelligence_summary.csv
#     └── ...
#
# Therefore we use the project path explicitly.
#
# This avoids Python accidentally resolving:
#
# D:\PORTFOLIO PROJECT\Assam Flood\GEE\Output
#
# which is NOT where the district CSVs are stored.


PROJECT_ROOT = (
    r"D:\PORTFOLIO PROJECT\Assam Flood"
)


OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "Output"
)


GRAPH_DIR = os.path.join(
    OUTPUT_DIR,
    "graphs"
)


# ============================================================
# SECTION 3 — CREATE OUTPUT DIRECTORIES
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


os.makedirs(
    GRAPH_DIR,
    exist_ok=True
)


# ============================================================
# SECTION 4 — VERIFY PATH
# ============================================================

print()
print("=" * 70)
print("ASSAM FLOOD INTELLIGENCE")
print("OVERVIEW — FLOOD-AFFECTED LAND COVER")
print("=" * 70)

print()

print(
    "Project root:",
    PROJECT_ROOT
)

print(
    "Output directory:",
    OUTPUT_DIR
)

print(
    "Output exists:",
    os.path.exists(OUTPUT_DIR)
)

print()

print(
    "IMPORTANT:"
)

print(
    "Reading individual district CSVs only."
)

print(
    "Master Assam summary will NOT be used."
)

print()


# ============================================================
# SECTION 5 — NINE ANALYZED DISTRICTS
# ============================================================

# These are the districts included in the overview.
#
# Lakhimpur is intentionally NOT included.
# Karbi Anglong is intentionally NOT included.
#
# The overview therefore represents the same nine districts
# that are being used for the analyzed district dashboard.

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
# SECTION 6 — SOURCE CSV COLUMNS
# ============================================================

FLOODED_AREA_COLUMN = (
    "flooded_area_km2"
)


FLOODED_CROPLAND_COLUMN = (
    "flooded_cropland_km2"
)


FLOODED_FOREST_COLUMN = (
    "flooded_forest_km2"
)


# ============================================================
# SECTION 7 — READ INDIVIDUAL DISTRICT CSVs
# ============================================================

district_records = []


for district in DISTRICTS:

    print()
    print("-" * 70)

    print(
        "District:",
        district
    )


    # --------------------------------------------------------
    # Construct the EXACT filename
    # --------------------------------------------------------

    filename = (
        f"{district}_"
        "flood_intelligence_summary.csv"
    )


    csv_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    print(
        "Reading:",
        csv_path
    )


    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not os.path.isfile(csv_path):

        raise FileNotFoundError(

            "\nIndividual district CSV not found:\n"
            f"{csv_path}\n\n"
            f"Expected file:\n"
            f"{filename}\n\n"
            "The script reads only the individual "
            "district summary CSVs."

        )


    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(
        csv_path
    )


    print(
        "Rows found:",
        len(df)
    )


    print(
        "Columns found:",
        list(df.columns)
    )


    # --------------------------------------------------------
    # Check required columns
    # --------------------------------------------------------

    required_columns = [

        FLOODED_AREA_COLUMN,

        FLOODED_CROPLAND_COLUMN,

        FLOODED_FOREST_COLUMN,

    ]


    missing_columns = [

        column

        for column in required_columns

        if column not in df.columns

    ]


    if missing_columns:

        raise ValueError(

            f"\nMissing required columns in "
            f"{district} CSV.\n\n"

            f"Missing:\n"
            f"{missing_columns}\n\n"

            f"Available columns:\n"
            f"{list(df.columns)}"

        )


    # --------------------------------------------------------
    # Check that the CSV contains data
    # --------------------------------------------------------

    if df.empty:

        raise ValueError(

            f"\nCSV is empty:\n"
            f"{csv_path}"

        )


    # --------------------------------------------------------
    # District summary CSV should contain the district-level
    # summary record.
    #
    # We use the first record because this is a district
    # summary file, not a pixel-level table.
    # --------------------------------------------------------

    row = df.iloc[0]


    # --------------------------------------------------------
    # Extract existing values
    # --------------------------------------------------------

    flooded_area = float(

        row[
            FLOODED_AREA_COLUMN
        ]

    )


    flooded_cropland = float(

        row[
            FLOODED_CROPLAND_COLUMN
        ]

    )


    flooded_forest = float(

        row[
            FLOODED_FOREST_COLUMN
        ]

    )


    # --------------------------------------------------------
    # Calculate OTHER
    #
    # No new spatial analysis.
    #
    # This is simply the remainder of the existing flooded
    # area after removing flooded cropland and flooded forest.
    # --------------------------------------------------------

    flooded_other = (

        flooded_area

        - flooded_cropland

        - flooded_forest

    )


    # --------------------------------------------------------
    # Numerical safety check
    # --------------------------------------------------------

    if flooded_other < 0:

        if abs(
            flooded_other
        ) < 0.000001:

            flooded_other = 0.0

        else:

            raise ValueError(

                f"\nInvalid land-cover values for "
                f"{district}.\n\n"

                f"Flooded area: "
                f"{flooded_area}\n"

                f"Flooded cropland: "
                f"{flooded_cropland}\n"

                f"Flooded forest: "
                f"{flooded_forest}\n"

                f"Calculated other: "
                f"{flooded_other}"

            )


    # --------------------------------------------------------
    # Store district record
    # --------------------------------------------------------

    district_records.append({

        "district":
            district,

        "flooded_area_km2":
            flooded_area,

        "flooded_cropland_km2":
            flooded_cropland,

        "flooded_forest_km2":
            flooded_forest,

        "flooded_other_km2":
            flooded_other,

    })


    # --------------------------------------------------------
    # Display district values
    # --------------------------------------------------------

    print()

    print(
        "Flooded area:",
        round(
            flooded_area,
            3
        ),
        "km²"
    )

    print(
        "Flooded cropland:",
        round(
            flooded_cropland,
            3
        ),
        "km²"
    )

    print(
        "Flooded forest:",
        round(
            flooded_forest,
            3
        ),
        "km²"
    )

    print(
        "Other flooded area:",
        round(
            flooded_other,
            3
        ),
        "km²"
    )


# ============================================================
# SECTION 8 — DISTRICT DATAFRAME
# ============================================================

district_df = pd.DataFrame(
    district_records
)


# ============================================================
# SECTION 9 — AGGREGATE NINE DISTRICTS
# ============================================================

total_flooded_area = (

    district_df[
        "flooded_area_km2"
    ].sum()

)


total_flooded_cropland = (

    district_df[
        "flooded_cropland_km2"
    ].sum()

)


total_flooded_forest = (

    district_df[
        "flooded_forest_km2"
    ].sum()

)


total_flooded_other = (

    district_df[
        "flooded_other_km2"
    ].sum()

)


# ============================================================
# SECTION 10 — VALIDATE TOTALS
# ============================================================

landcover_sum = (

    total_flooded_cropland

    + total_flooded_forest

    + total_flooded_other

)


validation_difference = (

    total_flooded_area

    - landcover_sum

)


print()
print("=" * 70)
print("LAND-COVER AGGREGATION")
print("=" * 70)

print()

print(
    "Total flooded area:",
    round(
        total_flooded_area,
        3
    ),
    "km²"
)

print(
    "Total flooded cropland:",
    round(
        total_flooded_cropland,
        3
    ),
    "km²"
)

print(
    "Total flooded forest:",
    round(
        total_flooded_forest,
        3
    ),
    "km²"
)

print(
    "Total other flooded area:",
    round(
        total_flooded_other,
        3
    ),
    "km²"
)

print()

print(
    "Land-cover total:",
    round(
        landcover_sum,
        3
    ),
    "km²"
)

print(
    "Validation difference:",
    round(
        validation_difference,
        10
    ),
    "km²"
)


# ------------------------------------------------------------
# Validation
# ------------------------------------------------------------

if abs(
    validation_difference
) > 0.000001:

    raise ValueError(

        "\nLand-cover totals do not match "
        "the total flooded area."

    )


# ============================================================
# SECTION 11 — CALCULATE PERCENTAGES
# ============================================================

if total_flooded_area <= 0:

    raise ValueError(

        "Total flooded area is zero or negative."

    )


cropland_percent = (

    total_flooded_cropland

    / total_flooded_area

    * 100

)


forest_percent = (

    total_flooded_forest

    / total_flooded_area

    * 100

)


other_percent = (

    total_flooded_other

    / total_flooded_area

    * 100

)


# ============================================================
# SECTION 12 — OVERVIEW DATAFRAME
# ============================================================

overview_df = pd.DataFrame({

    "land_cover": [

        "Cropland",

        "Forest",

        "Other",

    ],

    "affected_area_km2": [

        total_flooded_cropland,

        total_flooded_forest,

        total_flooded_other,

    ],

    "percentage": [

        cropland_percent,

        forest_percent,

        other_percent,

    ],

})


# ============================================================
# SECTION 13 — SAVE OVERVIEW CSV
# ============================================================

overview_csv_path = os.path.join(

    OUTPUT_DIR,

    "Assam_overview_landcover.csv"

)


overview_df.to_csv(

    overview_csv_path,

    index=False

)


print()
print(
    "Saved overview CSV:"
)

print(
    overview_csv_path
)


# ============================================================
# SECTION 14 — SAVE DISTRICT CONTRIBUTION CSV
# ============================================================

district_contribution_path = os.path.join(

    OUTPUT_DIR,

    "Assam_overview_landcover_by_district.csv"

)


district_df.to_csv(

    district_contribution_path,

    index=False

)


print()
print(
    "Saved district contribution CSV:"
)

print(
    district_contribution_path
)


# ============================================================
# SECTION 15 — SAVE JSON
# ============================================================

dashboard_json = {

    "scope": {

        "description":
            "Flood-affected land cover across "
            "the 9 analyzed districts",

        "district_count":
            len(DISTRICTS),

        "districts":
            DISTRICTS,

    },

    "total_flooded_area_km2":
        round(
            total_flooded_area,
            3
        ),

    "landcover": [

        {

            "name":
                "Cropland",

            "area_km2":
                round(
                    total_flooded_cropland,
                    3
                ),

            "percentage":
                round(
                    cropland_percent,
                    2
                ),

        },

        {

            "name":
                "Forest",

            "area_km2":
                round(
                    total_flooded_forest,
                    3
                ),

            "percentage":
                round(
                    forest_percent,
                    2
                ),

        },

        {

            "name":
                "Other",

            "area_km2":
                round(
                    total_flooded_other,
                    3
                ),

            "percentage":
                round(
                    other_percent,
                    2
                ),

        },

    ],

}


dashboard_json_path = os.path.join(

    OUTPUT_DIR,

    "Assam_overview_landcover.json"

)


with open(

    dashboard_json_path,

    "w",

    encoding="utf-8"

) as file:

    json.dump(

        dashboard_json,

        file,

        indent=4

    )


print()
print(
    "Saved dashboard JSON:"
)

print(
    dashboard_json_path
)


# ============================================================
# SECTION 16 — CREATE DONUT CHART
# ============================================================

labels = [

    "Cropland",

    "Forest",

    "Other",

]


values = [

    total_flooded_cropland,

    total_flooded_forest,

    total_flooded_other,

]


# ------------------------------------------------------------
# Create figure
# ------------------------------------------------------------

fig, ax = plt.subplots(

    figsize=(
        8,
        6
    )

)


# ------------------------------------------------------------
# Donut
# ------------------------------------------------------------

wedges, _ = ax.pie(

    values,

    startangle=90,

    counterclock=False,

    wedgeprops={

        "width": 0.32,

        "edgecolor": "white",

        "linewidth": 2,

    },

)


# ------------------------------------------------------------
# Centre number
# ------------------------------------------------------------

ax.text(

    0,

    0.05,

    f"{total_flooded_area:.1f}",

    ha="center",

    va="center",

    fontsize=28,

    fontweight="bold",

)


# ------------------------------------------------------------
# Centre unit
# ------------------------------------------------------------

ax.text(

    0,

    -0.18,

    "km² flooded",

    ha="center",

    va="center",

    fontsize=10,

)


# ------------------------------------------------------------
# Legend
# ------------------------------------------------------------

legend_labels = [

    (
        f"Cropland    "
        f"{cropland_percent:.2f}%"
    ),

    (
        f"Forest      "
        f"{forest_percent:.2f}%"
    ),

    (
        f"Other       "
        f"{other_percent:.2f}%"
    ),

]


ax.legend(

    wedges,

    legend_labels,

    loc="center left",

    bbox_to_anchor=(
        1.02,
        0.5
    ),

    frameon=False,

)


# ------------------------------------------------------------
# Title
# ------------------------------------------------------------

ax.set_title(

    "Flood-affected land cover\n"
    "Across 9 analyzed districts",

    fontsize=15,

    fontweight="bold",

    pad=20,

)


# ------------------------------------------------------------
# Equal aspect
# ------------------------------------------------------------

ax.set_aspect(
    "equal"
)


# ------------------------------------------------------------
# Save PNG
# ------------------------------------------------------------

graph_path = os.path.join(

    GRAPH_DIR,

    "Assam_overview_flood_landcover.png"

)


plt.tight_layout()


plt.savefig(

    graph_path,

    dpi=200,

    bbox_inches="tight"

)


plt.close()


# ============================================================
# SECTION 17 — FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("ASSAM OVERVIEW LAND-COVER ANALYSIS COMPLETE")
print("=" * 70)

print()

print(
    "Districts included:",
    len(DISTRICTS)
)

print(
    "Total flooded area:",
    round(
        total_flooded_area,
        3
    ),
    "km²"
)

print()

print(
    "Cropland:",
    round(
        total_flooded_cropland,
        3
    ),
    "km² |",
    round(
        cropland_percent,
        2
    ),
    "%"
)

print(
    "Forest:",
    round(
        total_flooded_forest,
        3
    ),
    "km² |",
    round(
        forest_percent,
        2
    ),
    "%"
)

print(
    "Other:",
    round(
        total_flooded_other,
        3
    ),
    "km² |",
    round(
        other_percent,
        2
    ),
    "%"
)

print()

print(
    "Overview CSV:",
    overview_csv_path
)

print(
    "District contribution CSV:",
    district_contribution_path
)

print(
    "Dashboard JSON:",
    dashboard_json_path
)

print(
    "Donut chart:",
    graph_path
)

print()

print("=" * 70)