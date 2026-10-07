import geopandas as gpd
import rasterio
import numpy as np
from PIL import Image
from pathlib import Path
import json


# ============================================================
# ASSAM FLOOD INTELLIGENCE
# SPATIAL WEB DATA PREPARATION
# ============================================================

PROJECT_ROOT = Path(r"D:\PORTFOLIO PROJECT\Assam Flood")

OUTPUT_DIR = PROJECT_ROOT / "Output"
SPATIAL_DIR = PROJECT_ROOT / "Cache" / "dashboard_data" / "spatial"

SPATIAL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CURRENT PROJECT SCOPE
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
# HELPERS
# ============================================================

def save_geojson(gdf, output_path):
    """
    Save GeoDataFrame as GeoJSON in EPSG:4326.
    """
    gdf = gdf.to_crs(epsg=4326)

    gdf.to_file(
        output_path,
        driver="GeoJSON"
    )


def raster_to_png(input_path, output_path):
    """
    Convert single-band flood raster into a transparent PNG.

    Raster value 0 / nodata:
        transparent

    Flood pixels:
        visible

    The geographic bounds are preserved separately in metadata.
    """

    with rasterio.open(input_path) as src:

        data = src.read(1)

        bounds = src.bounds

        # ----------------------------------------------------
        # Flood mask
        # ----------------------------------------------------

        flood_mask = data > 0

        # ----------------------------------------------------
        # RGBA image
        # ----------------------------------------------------

        height, width = data.shape

        rgba = np.zeros(
            (height, width, 4),
            dtype=np.uint8
        )

        # Flood pixels
        #
        # Orange-red flood visualization.
        # Transparency allows the satellite basemap to remain visible.
        rgba[flood_mask, 0] = 255
        rgba[flood_mask, 1] = 90
        rgba[flood_mask, 2] = 40
        rgba[flood_mask, 3] = 190

        image = Image.fromarray(
            rgba,
            mode="RGBA"
        )

        image.save(
            output_path,
            optimize=True
        )

        return {
            "west": bounds.left,
            "south": bounds.bottom,
            "east": bounds.right,
            "north": bounds.top,
            "width": width,
            "height": height,
            "flood_pixels": int(flood_mask.sum()),
            "crs": str(src.crs),
        }


# ============================================================
# START
# ============================================================

print("=" * 75)
print("ASSAM FLOOD INTELLIGENCE")
print("SPATIAL WEB DATA PREPARATION")
print("=" * 75)

print("\nCurrent project districts:")

for district in DISTRICTS:
    print(f"  ✓ {district}")


# ============================================================
# PROCESS EACH DISTRICT
# ============================================================

district_metadata = []


for district in DISTRICTS:

    print("\n" + "-" * 75)
    print(district)
    print("-" * 75)

    district_dir = SPATIAL_DIR / district

    district_dir.mkdir(
        parents=True,
        exist_ok=True
    )


    # ========================================================
    # FILE PATHS
    # ========================================================

    building_file = (
        OUTPUT_DIR
        / "buildings"
        / f"{district}_affected_buildings.gpkg"
    )

    road_file = (
        OUTPUT_DIR
        / "roads"
        / f"{district}_roads.gpkg"
    )

    raster_file = (
        OUTPUT_DIR
        / "raster"
        / f"{district}_flood_exposure.tif"
    )


    # ========================================================
    # BUILDINGS
    # ========================================================

    print("\n[1/3] Buildings")

    if building_file.exists():

        buildings = gpd.read_file(
            building_file
        )

        print(f"  Features: {len(buildings)}")
        print(f"  Original CRS: {buildings.crs}")
        print(
            f"  Geometry: "
            f"{buildings.geom_type.unique().tolist()}"
        )

        buildings = buildings.to_crs(
            epsg=4326
        )

        building_output = (
            district_dir
            / "buildings.geojson"
        )

        buildings.to_file(
            building_output,
            driver="GeoJSON"
        )

        print("  ✓ Saved: buildings.geojson")

    else:

        print(
            f"  ⚠ Missing: "
            f"{building_file.name}"
        )


    # ========================================================
    # ROADS
    # ========================================================

    print("\n[2/3] Roads")

    if road_file.exists():

        # ----------------------------------------------------
        # Inspect available layers
        # ----------------------------------------------------

        layers = gpd.list_layers(
            road_file
        )

        print("  Available layers:")

        for layer in layers["name"]:
            print(f"    • {layer}")


        # ----------------------------------------------------
        # ALL ROADS
        # ----------------------------------------------------

        if "all_roads" in layers["name"].values:

            all_roads = gpd.read_file(
                road_file,
                layer="all_roads"
            )

            print(
                f"  All roads: "
                f"{len(all_roads)}"
            )

            all_roads = all_roads.to_crs(
                epsg=4326
            )

            roads_output = (
                district_dir
                / "roads.geojson"
            )

            all_roads.to_file(
                roads_output,
                driver="GeoJSON"
            )

            print(
                "  ✓ Saved: roads.geojson"
            )


        # ----------------------------------------------------
        # FLOOD-AFFECTED ROADS
        # ----------------------------------------------------

        if "flood_affected_roads" in layers["name"].values:

            affected_roads = gpd.read_file(
                road_file,
                layer="flood_affected_roads"
            )

            print(
                f"  Flood-affected roads: "
                f"{len(affected_roads)}"
            )

            affected_roads = affected_roads.to_crs(
                epsg=4326
            )

            affected_output = (
                district_dir
                / "affected_roads.geojson"
            )

            affected_roads.to_file(
                affected_output,
                driver="GeoJSON"
            )

            print(
                "  ✓ Saved: "
                "affected_roads.geojson"
            )


    else:

        print(
            f"  ⚠ Missing: "
            f"{road_file.name}"
        )


    # ========================================================
    # FLOOD RASTER
    # ========================================================

    print("\n[3/3] Flood extent")

    if raster_file.exists():

        flood_output = (
            district_dir
            / "flood_extent.png"
        )

        metadata = raster_to_png(
            raster_file,
            flood_output
        )

        print(
            f"  Raster size: "
            f"{metadata['width']} x "
            f"{metadata['height']}"
        )

        print(
            f"  Flood pixels: "
            f"{metadata['flood_pixels']}"
        )

        print(
            f"  CRS: "
            f"{metadata['crs']}"
        )

        print(
            "  ✓ Saved: "
            "flood_extent.png"
        )


        # ----------------------------------------------------
        # Save geographic bounds
        # ----------------------------------------------------

        bounds_output = (
            district_dir
            / "flood_extent_bounds.json"
        )

        with open(
            bounds_output,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=2
            )

        print(
            "  ✓ Saved: "
            "flood_extent_bounds.json"
        )

        district_metadata.append({
            "district": district,
            **metadata
        })


    else:

        print(
            f"  ⚠ Missing: "
            f"{raster_file.name}"
        )


# ============================================================
# SAVE DISTRICT SPATIAL INDEX
# ============================================================

index_file = (
    SPATIAL_DIR
    / "spatial_index.json"
)

with open(
    index_file,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        district_metadata,
        f,
        indent=2
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 75)
print("SPATIAL WEB DATA PREPARATION COMPLETE")
print("=" * 75)

print(
    f"\nDistricts processed: "
    f"{len(district_metadata)} / "
    f"{len(DISTRICTS)}"
)

print("\nOutput:")

print(
    f"  {SPATIAL_DIR}"
)

print("\nEach district may contain:")

print("  ✓ buildings.geojson")
print("  ✓ roads.geojson")
print("  ✓ affected_roads.geojson")
print("  ✓ flood_extent.png")
print("  ✓ flood_extent_bounds.json")

print("\nCreated:")

print("  ✓ spatial_index.json")

print("\nExcluded from current project:")

print("  ✗ Lakhimpur")
print("  ✗ Karbi Anglong")

print("\nOriginal Output files were not modified.")

print("\n" + "=" * 75)