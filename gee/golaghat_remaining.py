
import os
import glob
import warnings

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio

warnings.filterwarnings("ignore")


# ============================================================
# 1. SETTINGS
# ============================================================

DISTRICT = "Golaghat"

OUTPUT_ROOT = "Output"

BUILDING_OUTPUT_DIR = os.path.join(
    OUTPUT_ROOT,
    "buildings"
)

ROAD_OUTPUT_DIR = os.path.join(
    OUTPUT_ROOT,
    "roads"
)

os.makedirs(OUTPUT_ROOT, exist_ok=True)
os.makedirs(BUILDING_OUTPUT_DIR, exist_ok=True)
os.makedirs(ROAD_OUTPUT_DIR, exist_ok=True)


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def find_file(patterns, description):
    """
    Find an existing file inside Output and its subfolders.
    """

    for pattern in patterns:

        matches = glob.glob(
            os.path.join(
                OUTPUT_ROOT,
                "**",
                pattern
            ),
            recursive=True
        )

        if matches:
            return matches[0]

    raise FileNotFoundError(
        f"\nCould not find {description}.\n"
        f"Checked patterns: {patterns}"
    )


def safe_percentage(numerator, denominator):

    if denominator == 0:
        return 0.0

    return round(
        (numerator / denominator) * 100,
        2
    )


def convert_to_boolean(series):
    """
    Convert common flood classification formats
    into True/False values.
    """

    if series.dtype == bool:
        return series.fillna(False)

    if pd.api.types.is_numeric_dtype(series):

        return series.fillna(0) > 0

    return (
        series
        .astype(str)
        .str.lower()
        .isin([
            "true",
            "1",
            "yes",
            "flooded",
            "affected"
        ])
    )


def find_flood_column(gdf):

    possible_columns = [
        "flood_affected",
        "flooded",
        "affected",
        "is_flood_affected",
        "flood_exposed",
        "flood_value"
    ]

    for column in possible_columns:

        if column in gdf.columns:
            return column

    return None


def sample_raster_at_centroids(gdf, raster_path):

    """
    Sample the existing flood raster at the centroid
    of each feature.

    This is only used if the GeoPackage does not already
    contain a flood classification column.
    """

    with rasterio.open(raster_path) as src:

        gdf_raster = gdf.to_crs(src.crs)

        centroids = gdf_raster.geometry.centroid

        coordinates = [
            (point.x, point.y)
            for point in centroids
        ]

        sampled_values = list(
            src.sample(coordinates)
        )

        values = [
            float(value[0])
            for value in sampled_values
        ]

        if src.nodata is not None:

            values = [
                0 if value == src.nodata else value
                for value in values
            ]

        return pd.Series(
            values,
            index=gdf.index
        )


# ============================================================
# 3. FIND EXISTING FILES
# ============================================================

print("\n" + "=" * 60)
print(f"GENERATING OUTPUTS FOR {DISTRICT.upper()}")
print("=" * 60)


flood_raster_path = find_file(
    [
        f"{DISTRICT}_flood_exposure.tif",
        f"{DISTRICT}*flood*.tif"
    ],
    "flood raster"
)

print(
    f"\nFlood raster found:\n{flood_raster_path}"
)


building_gpkg_path = find_file(
    [
        f"{DISTRICT}_affected_buildings.gpkg",
        f"{DISTRICT}_building_exposure.gpkg",
        f"{DISTRICT}_buildings.gpkg",
        f"{DISTRICT}*building*.gpkg"
    ],
    "building GeoPackage"
)

print(
    f"\nBuilding GeoPackage found:\n{building_gpkg_path}"
)


road_gpkg_path = find_file(
    [
        f"{DISTRICT}_roads.gpkg",
        f"{DISTRICT}_road_exposure.gpkg",
        f"{DISTRICT}*road*.gpkg"
    ],
    "road GeoPackage"
)

print(
    f"\nRoad GeoPackage found:\n{road_gpkg_path}"
)


# ============================================================
# 4. BUILDING SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("BUILDING SUMMARY")
print("=" * 60)


buildings = gpd.read_file(
    building_gpkg_path
)

print(
    f"Total building features found: {len(buildings)}"
)

print(
    f"Building columns:\n{list(buildings.columns)}"
)


total_mapped_buildings = len(buildings)


building_flood_column = find_flood_column(
    buildings
)


if building_flood_column is not None:

    print(
        f"\nUsing existing flood column: "
        f"{building_flood_column}"
    )

    buildings["flood_affected"] = convert_to_boolean(
        buildings[building_flood_column]
    )

else:

    print(
        "\nNo flood classification column found."
    )

    print(
        "Sampling the existing flood raster at building centroids..."
    )

    sampled_values = sample_raster_at_centroids(
        buildings,
        flood_raster_path
    )

    buildings["flood_affected"] = (
        sampled_values > 0
    )


affected_buildings = buildings[
    buildings["flood_affected"] == True
].copy()


affected_buildings_count = len(
    affected_buildings
)


affected_buildings_percent = safe_percentage(
    affected_buildings_count,
    total_mapped_buildings
)


building_summary = pd.DataFrame(
    [
        {
            "district": DISTRICT,
            "total_osm_mapped_buildings": total_mapped_buildings,
            "flood_affected_buildings": affected_buildings_count,
            "affected_buildings_percent": affected_buildings_percent
        }
    ]
)


building_summary_path = os.path.join(
    OUTPUT_ROOT,
    f"{DISTRICT}_building_summary.csv"
)


building_summary.to_csv(
    building_summary_path,
    index=False
)


print(
    f"\nBuilding summary saved:\n"
    f"{building_summary_path}"
)

print("\nBuilding summary:")
print(building_summary)


# ============================================================
# 5. BUILDING PREVIEW
# ============================================================

print("\nGenerating building preview...")


building_preview_path = os.path.join(
    BUILDING_OUTPUT_DIR,
    f"{DISTRICT}_building_flood_preview.png"
)


fig, ax = plt.subplots(
    figsize=(12, 10)
)


# Plot all buildings in light grey
buildings.plot(
    ax=ax,
    color="lightgrey",
    edgecolor="none",
    markersize=0.5
)


# Plot affected buildings in red
if not affected_buildings.empty:

    affected_buildings.plot(
        ax=ax,
        color="red",
        edgecolor="none",
        markersize=0.7
    )


ax.set_title(
    f"{DISTRICT} Flood-Affected Buildings",
    fontsize=16
)

ax.set_axis_off()

plt.tight_layout()


plt.savefig(
    building_preview_path,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"Building preview saved:\n"
    f"{building_preview_path}"
)


# ============================================================
# 6. ROAD SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("ROAD SUMMARY")
print("=" * 60)


roads = gpd.read_file(
    road_gpkg_path
)


print(
    f"Total road features found: {len(roads)}"
)

print(
    f"Road columns:\n{list(roads.columns)}"
)


total_mapped_road_segments = len(roads)


road_flood_column = find_flood_column(
    roads
)


if road_flood_column is not None:

    print(
        f"\nUsing existing road flood column: "
        f"{road_flood_column}"
    )

    roads["flood_affected"] = convert_to_boolean(
        roads[road_flood_column]
    )

else:

    print(
        "\nNo road flood classification column found."
    )

    print(
        "Sampling the existing flood raster at road centroids..."
    )

    sampled_values = sample_raster_at_centroids(
        roads,
        flood_raster_path
    )

    roads["flood_affected"] = (
        sampled_values > 0
    )


affected_roads = roads[
    roads["flood_affected"] == True
].copy()


flood_affected_road_segments = len(
    affected_roads
)


# Project roads to a suitable metric CRS
roads_metric = roads.to_crs(
    roads.estimate_utm_crs()
)


roads_metric["road_length_km"] = (
    roads_metric.geometry.length / 1000
)


total_road_length_km = (
    roads_metric["road_length_km"].sum()
)


affected_roads_metric = roads_metric[
    roads_metric["flood_affected"] == True
]


affected_road_length_km = (
    affected_roads_metric["road_length_km"].sum()
)


road_affected_percent = safe_percentage(
    affected_road_length_km,
    total_road_length_km
)


road_summary = pd.DataFrame(
    [
        {
            "district": DISTRICT,
            "total_osm_mapped_road_length_km": round(
                total_road_length_km,
                3
            ),
            "flood_affected_road_length_km": round(
                affected_road_length_km,
                3
            ),
            "road_affected_percent": road_affected_percent,
            "total_mapped_road_segments": total_mapped_road_segments,
            "flood_affected_road_segments": flood_affected_road_segments
        }
    ]
)


road_summary_path = os.path.join(
    OUTPUT_ROOT,
    f"{DISTRICT}_road_summary.csv"
)


road_summary.to_csv(
    road_summary_path,
    index=False
)


print(
    f"\nRoad summary saved:\n"
    f"{road_summary_path}"
)

print("\nRoad summary:")
print(road_summary)


# ============================================================
# 7. ROAD PREVIEW
# ============================================================

print("\nGenerating road preview...")


road_preview_path = os.path.join(
    ROAD_OUTPUT_DIR,
    f"{DISTRICT}_road_flood_preview.png"
)


fig, ax = plt.subplots(
    figsize=(12, 10)
)


# Plot all roads
roads.plot(
    ax=ax,
    color="lightgrey",
    linewidth=0.4
)


# Plot flood-affected roads
if not affected_roads.empty:

    affected_roads.plot(
        ax=ax,
        color="red",
        linewidth=1.0
    )


ax.set_title(
    f"{DISTRICT} Flood-Affected Roads",
    fontsize=16
)

ax.set_axis_off()

plt.tight_layout()


plt.savefig(
    road_preview_path,
    dpi=300,
    bbox_inches="tight"
)


plt.close()


print(
    f"Road preview saved:\n"
    f"{road_preview_path}"
)


# ============================================================
# 8. FINAL REPORT
# ============================================================

print("\n" + "=" * 60)
print("OUTPUT GENERATION COMPLETE")
print("=" * 60)


print("\nGenerated files:")

print(
    f"\n1. Building CSV:\n"
    f"{building_summary_path}"
)

print(
    f"\n2. Building PNG:\n"
    f"{building_preview_path}"
)

print(
    f"\n3. Road CSV:\n"
    f"{road_summary_path}"
)

print(
    f"\n4. Road PNG:\n"
    f"{road_preview_path}"
)

print("\nNo new OSM or Overpass download was required.")