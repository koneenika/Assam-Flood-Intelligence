# ============================================================
# ASSAM FLOOD INTELLIGENCE
# ASSAM-WIDE RAINFALL ANALYSIS
# ============================================================


# ============================================================
# SECTION 1 — IMPORTS & CONFIGURATION
# ============================================================

import os

import ee

import pandas as pd

import matplotlib.pyplot as plt


from configuration import (
    EE_PROJECT,

    ASSAM_ASSET,

    OUTPUT_DIR,

    GPM_COLLECTION,

    S1_SEARCH_START,
    S1_SEARCH_END,

    FLOOD_START,
    FLOOD_END,

    EXPORT_RAINFALL_GRAPH,
)


# ============================================================
# SECTION 2 — INITIALIZE EARTH ENGINE
# ============================================================

print()
print("================================================")
print("ASSAM FLOOD INTELLIGENCE")
print("ASSAM-WIDE RAINFALL ANALYSIS")
print("================================================")

print()

print(
    "Earth Engine project:",
    EE_PROJECT
)

print(
    "Assam asset:",
    ASSAM_ASSET
)


ee.Initialize(
    project=EE_PROJECT
)


# ============================================================
# SECTION 3 — LOAD ASSAM STATE BOUNDARY
# ============================================================

print()
print("================================================")
print("LOADING ASSAM STATE BOUNDARY")
print("================================================")


assam = ee.FeatureCollection(
    ASSAM_ASSET
)


assam_geometry = (
    assam.geometry()
)


assam_feature_count = (
    assam.size().getInfo()
)


print(
    "Assam boundary features:",
    assam_feature_count
)


# ============================================================
# SECTION 4 — GPM RAINFALL COLLECTION
# ============================================================

print()
print("================================================")
print("GPM RAINFALL DATA")
print("================================================")


gpm = (
    ee.ImageCollection(
        GPM_COLLECTION
    )

    .filterBounds(
        assam_geometry
    )

    .filterDate(
        S1_SEARCH_START,
        S1_SEARCH_END
    )
)


gpm_count = (
    gpm.size().getInfo()
)


print(
    "GPM images available:",
    gpm_count
)


if gpm_count == 0:

    raise RuntimeError(
        "No GPM rainfall images were found "
        "for the Assam AOI."
    )


# ============================================================
# SECTION 5 — CONVERT GPM PRECIPITATION
# ============================================================

print()
print("Converting GPM precipitation...")


# GPM IMERG V07:
#
# precipitation = mm/hour
#
# Each image represents a 30-minute interval.
#
# Therefore:
#
# rainfall depth =
# precipitation × 0.5 hour
#
# Result:
# rainfall_mm = mm per 30-minute observation


def convert_gpm_to_mm(
    image
):

    rainfall_mm = (

        image

        .select(
            "precipitation"
        )

        .multiply(
            0.5
        )

        .rename(
            "rainfall_mm"
        )

    )


    return rainfall_mm.copyProperties(

        image,

        [
            "system:time_start"
        ]

    )


gpm_rainfall = (
    gpm.map(
        convert_gpm_to_mm
    )
)


print(
    "GPM rainfall collection prepared."
)


# ============================================================
# SECTION 6 — FLOOD-PERIOD DATE RANGE
# ============================================================

print()
print("================================================")
print("ASSAM FLOOD-PERIOD RAINFALL")
print("================================================")


print(
    "Flood start:",
    FLOOD_START
)

print(
    "Flood end:",
    FLOOD_END
)


start_date = ee.Date(
    FLOOD_START
)


end_date = ee.Date(
    FLOOD_END
)


number_of_days = (

    end_date

    .difference(
        start_date,
        "day"
    )

    .toInt()

)


day_offsets = ee.List.sequence(

    0,

    number_of_days.subtract(
        1
    )

)


print(
    "Number of flood-period days:",
    number_of_days.getInfo()
)


# ============================================================
# SECTION 7 — DAILY ASSAM RAINFALL
# ============================================================


def calculate_daily_rainfall(
    day_offset
):

    day_offset = ee.Number(
        day_offset
    )


    day_start = (

        start_date

        .advance(
            day_offset,
            "day"
        )

    )


    day_end = (

        day_start

        .advance(
            1,
            "day"
        )

    )


    # --------------------------------------------------------
    # Select all half-hourly GPM images for this day
    # --------------------------------------------------------

    daily_images = (

        gpm_rainfall

        .filterDate(
            day_start,
            day_end
        )

    )


    # --------------------------------------------------------
    # Sum the half-hourly rainfall
    # --------------------------------------------------------

    daily_rainfall = (

        daily_images

        .sum()

        .rename(
            "daily_rainfall"
        )

        .clip(
            assam_geometry
        )

    )


    # --------------------------------------------------------
    # Assam-wide spatial mean
    # --------------------------------------------------------
    #
    # This is the same approach used in the district
    # rainfall analysis.
    #
    # Instead of:
    #
    #     district_mean
    #
    # we are calculating:
    #
    #     assam_mean
    #
    # The value represents the mean rainfall depth
    # across the Assam AOI for that day.
    # --------------------------------------------------------

    assam_mean = (

        daily_rainfall

        .reduceRegion(

            reducer=ee.Reducer.mean(),

            geometry=assam_geometry,

            scale=11132,

            maxPixels=1e9,

            bestEffort=True

        )

        .get(
            "daily_rainfall"
        )

    )


    return ee.Feature(

        None,

        {

            "date":
                day_start.format(
                    "YYYY-MM-dd"
                ),

            "rainfall_mm":
                assam_mean

        }

    )


# ============================================================
# SECTION 8 — BUILD DAILY RAINFALL FEATURE COLLECTION
# ============================================================

print()
print(
    "Calculating daily Assam rainfall..."
)


daily_rainfall_fc = (

    ee.FeatureCollection(

        day_offsets.map(
            calculate_daily_rainfall
        )

    )

)


# ============================================================
# SECTION 9 — CONVERT TO PYTHON
# ============================================================

daily_features = (

    daily_rainfall_fc

    .getInfo()

    [
        "features"
    ]

)


daily_records = [

    feature[
        "properties"
    ]

    for feature
    in daily_features

]


# ------------------------------------------------------------
# Remove null rainfall values
# ------------------------------------------------------------

daily_records = [

    record

    for record
    in daily_records

    if record.get(
        "rainfall_mm"
    ) is not None

]


print(
    "Rainfall records:",
    len(daily_records)
)


# ============================================================
# SECTION 10 — RAINFALL SUMMARY
# ============================================================

if len(
    daily_records
) > 0:

    flood_period_rainfall = sum(

        record[
            "rainfall_mm"
        ]

        for record
        in daily_records

    )


    maximum_daily_rainfall = max(

        record[
            "rainfall_mm"
        ]

        for record
        in daily_records

    )


else:

    flood_period_rainfall = None

    maximum_daily_rainfall = None


print()
print(
    "================================================"
)

print(
    "ASSAM RAINFALL SUMMARY"
)

print(
    "================================================"
)


print()

print(
    "Flood-period accumulated rainfall:",
    round(
        flood_period_rainfall,
        3
    )
    if flood_period_rainfall
    is not None
    else "No data",
    "mm"
)


print(
    "Maximum daily rainfall:",
    round(
        maximum_daily_rainfall,
        3
    )
    if maximum_daily_rainfall
    is not None
    else "No data",
    "mm"
)


print(
    "Number of rainfall days:",
    len(
        daily_records
    )
)


# ============================================================
# SECTION 11 — PREPARE OUTPUT DIRECTORIES
# ============================================================

graph_dir = os.path.join(

    OUTPUT_DIR,

    "graphs"

)


os.makedirs(

    OUTPUT_DIR,

    exist_ok=True

)


os.makedirs(

    graph_dir,

    exist_ok=True

)


# ============================================================
# SECTION 12 — SAVE ASSAM RAINFALL CSV
# ============================================================

if len(
    daily_records
) > 0:

    rainfall_df = pd.DataFrame(
        daily_records
    )


    # --------------------------------------------------------
    # Convert date
    # --------------------------------------------------------

    rainfall_df[
        "date"
    ] = pd.to_datetime(

        rainfall_df[
            "date"
        ]

    )


    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    rainfall_df = (
        rainfall_df
        .sort_values(
            "date"
        )
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    rainfall_csv_path = os.path.join(

        OUTPUT_DIR,

        "Assam_daily_rainfall.csv"

    )


    rainfall_df.to_csv(

        rainfall_csv_path,

        index=False

    )


    print()
    print(
        "Saved:",
        rainfall_csv_path
    )


else:

    rainfall_df = pd.DataFrame()

    rainfall_csv_path = None


# ============================================================
# SECTION 13 — SAVE ASSAM RAINFALL GRAPH
# ============================================================

rainfall_graph_path = None


if (

    len(
        rainfall_df
    ) > 0

    and EXPORT_RAINFALL_GRAPH

):

    rainfall_graph_path = os.path.join(

        graph_dir,

        "Assam_daily_rainfall.png"

    )


    plt.figure(

        figsize=(
            12,
            5
        )

    )


    plt.plot(

        rainfall_df[
            "date"
        ],

        rainfall_df[
            "rainfall_mm"
        ],

        marker="o",

        linewidth=2

    )


    plt.xlabel(
        "Date"
    )


    plt.ylabel(
        "Daily rainfall (mm)"
    )


    plt.title(
        "Assam — Daily Rainfall During Flood Period"
    )


    plt.xticks(
        rotation=45
    )


    plt.grid(
        True,
        alpha=0.3
    )


    plt.tight_layout()


    plt.savefig(

        rainfall_graph_path,

        dpi=300,

        bbox_inches="tight"

    )


    plt.close()


    print(
        "Saved:",
        rainfall_graph_path
    )


# ============================================================
# SECTION 14 — FINAL SUMMARY
# ============================================================

print()
print(
    "================================================"
)

print(
    "ASSAM-WIDE RAINFALL ANALYSIS COMPLETE"
)

print(
    "================================================"
)


print()

print(
    "AOI: Entire Assam"
)


print(
    "Flood period:",
    FLOOD_START,
    "to",
    FLOOD_END
)


print(
    "Rainfall days:",
    len(
        daily_records
    )
)


print(
    "Accumulated rainfall:",
    round(
        flood_period_rainfall,
        3
    )
    if flood_period_rainfall
    is not None
    else "No data",
    "mm"
)


print(
    "Maximum daily rainfall:",
    round(
        maximum_daily_rainfall,
        3
    )
    if maximum_daily_rainfall
    is not None
    else "No data",
    "mm"
)


print()

print(
    "CSV:",
    rainfall_csv_path
)


print(
    "Graph:",
    rainfall_graph_path
)


print()
print(
    "================================================"
)