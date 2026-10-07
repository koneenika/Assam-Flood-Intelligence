# # ============================================================
# # INFRASTRUCTURE ANALYSIS
# # BUILDING AND ROAD FLOOD EXPOSURE
# # ============================================================

# import os
# import warnings

# import ee
# import pandas as pd
# import geopandas as gpd
# import matplotlib.pyplot as plt
# import rasterio
# import osmnx as ox

# from rasterio.features import shapes
# from shapely.geometry import shape
# from shapely.ops import unary_union

# from configuration import (
#     EE_PROJECT,
#     DISTRICT_ASSETS,
#     OUTPUT_DIR,
#     OSM_BUILDING_TAG
# )


# # ============================================================
# # SETTINGS
# # ============================================================

# # Change only this district for the next run
# DISTRICT = "Sivasagar"

# RUN_BUILDING_ANALYSIS = True
# RUN_ROAD_ANALYSIS = True


# # ============================================================
# # INITIALIZATION
# # ============================================================

# warnings.filterwarnings(
#     "ignore",
#     message="Geometry is in a geographic CRS"
# )

# ee.Initialize(
#     project=EE_PROJECT
# )

# print("Earth Engine initialized successfully.")


# # ============================================================
# # OUTPUT DIRECTORIES
# # ============================================================

# BUILDING_DIR = os.path.join(
#     OUTPUT_DIR,
#     "buildings"
# )

# ROAD_DIR = os.path.join(
#     OUTPUT_DIR,
#     "roads"
# )

# RASTER_DIR = os.path.join(
#     OUTPUT_DIR,
#     "raster"
# )

# os.makedirs(
#     BUILDING_DIR,
#     exist_ok=True
# )

# os.makedirs(
#     ROAD_DIR,
#     exist_ok=True
# )


# # ============================================================
# # HELPER FUNCTIONS
# # ============================================================

# def safe_percentage(numerator, denominator):

#     if denominator is None or denominator == 0:
#         return 0

#     return (
#         numerator / denominator
#     ) * 100


# def remove_existing_file(file_path):

#     if os.path.exists(file_path):
#         os.remove(file_path)

#         print(
#             "Removed existing file:",
#             file_path
#         )


# def create_flood_polygon(flood_raster_path):

#     with rasterio.open(
#         flood_raster_path
#     ) as src:

#         flood_array = src.read(1)

#         flood_transform = src.transform

#         flood_crs = src.crs

#     flood_mask = (
#         flood_array > 0
#     )

#     if not flood_mask.any():

#         return None, flood_crs

#     flood_shapes = shapes(
#         flood_array,
#         mask=flood_mask,
#         transform=flood_transform
#     )

#     flood_polygons = []

#     for geometry, value in flood_shapes:

#         if value > 0:

#             flood_polygons.append(
#                 shape(geometry)
#             )

#     if len(flood_polygons) == 0:

#         return None, flood_crs

#     flood_union = unary_union(
#         flood_polygons
#     )

#     flood_gdf = gpd.GeoDataFrame(
#         {
#             "flooded": [1]
#         },
#         geometry=[
#             flood_union
#         ],
#         crs=flood_crs
#     )

#     return flood_gdf, flood_crs


# def get_district_geometry(aoi_geometry):

#     district_geometry = shape(
#         aoi_geometry.getInfo()
#     )

#     return district_geometry


# # ============================================================
# # BUILDING EXPOSURE
# # ============================================================

# def calculate_building_exposure(
#     district,
#     flood_raster_path,
#     aoi_geometry
# ):

#     print()
#     print("=" * 60)
#     print("BUILDING EXPOSURE")
#     print("District:", district)
#     print("=" * 60)

#     flood_gdf, flood_crs = (
#         create_flood_polygon(
#             flood_raster_path
#         )
#     )

#     if flood_gdf is None:

#         print(
#             "No flooded pixels found."
#         )

#         return None

#     flood_gdf_wgs84 = (
#         flood_gdf.to_crs(
#             "EPSG:4326"
#         )
#     )

#     flood_polygon = (
#         flood_gdf_wgs84
#         .geometry
#         .iloc[0]
#     )

#     district_geometry = (
#         get_district_geometry(
#             aoi_geometry
#         )
#     )

#     print(
#         "Downloading OSM building footprints..."
#     )

#     try:

#         buildings = (
#             ox.features_from_polygon(
#                 district_geometry,
#                 tags=OSM_BUILDING_TAG
#             )
#         )

#     except Exception as error:

#         print(
#             "OSM building download failed:"
#         )

#         print(error)

#         return None

#     buildings = (
#         buildings[
#             buildings.geometry.notnull()
#         ]
#         .copy()
#     )

#     buildings = buildings[
#         buildings.geometry.geom_type.isin(
#             [
#                 "Polygon",
#                 "MultiPolygon"
#             ]
#         )
#     ].copy()

#     if buildings.crs is None:

#         buildings = buildings.set_crs(
#             "EPSG:4326"
#         )

#     else:

#         buildings = (
#             buildings.to_crs(
#                 "EPSG:4326"
#             )
#         )

#     total_buildings = len(
#         buildings
#     )

#     print(
#         "Total OSM-mapped buildings:",
#         total_buildings
#     )

#     flood_intersection_gdf = (
#         gpd.GeoDataFrame(
#             {
#                 "flood": [1]
#             },
#             geometry=[
#                 flood_polygon
#             ],
#             crs="EPSG:4326"
#         )
#     )

#     affected_buildings = gpd.sjoin(
#         buildings,
#         flood_intersection_gdf,
#         how="inner",
#         predicate="intersects"
#     )

#     affected_buildings = (
#         affected_buildings[
#             ~affected_buildings.index.duplicated(
#                 keep="first"
#             )
#         ]
#         .copy()
#     )

#     affected_count = len(
#         affected_buildings
#     )

#     affected_percentage = (
#         safe_percentage(
#             affected_count,
#             total_buildings
#         )
#     )

#     print(
#         "Flood-affected buildings:",
#         affected_count
#     )

#     print(
#         f"Buildings affected: "
#         f"{affected_percentage:.2f}%"
#     )

#     # --------------------------------------------------------
#     # SAVE AFFECTED BUILDINGS
#     # --------------------------------------------------------

#     building_gpkg_path = os.path.join(
#         BUILDING_DIR,
#         f"{district}_affected_buildings.gpkg"
#     )

#     remove_existing_file(
#         building_gpkg_path
#     )

#     export_columns = [
#         column
#         for column in [
#             "osmid",
#             "building",
#             "geometry"
#         ]
#         if column in affected_buildings.columns
#     ]

#     affected_export = (
#         affected_buildings[
#             export_columns
#         ]
#         .copy()
#     )

#     affected_export = (
#         affected_export
#         .drop(
#             columns=[
#                 "index_right"
#             ],
#             errors="ignore"
#         )
#     )

#     if len(affected_export) > 0:

#         affected_export.to_file(
#             building_gpkg_path,
#             driver="GPKG"
#         )

#     # --------------------------------------------------------
#     # SAVE BUILDING SUMMARY
#     # --------------------------------------------------------

#     building_summary_path = os.path.join(
#         OUTPUT_DIR,
#         f"{district}_building_summary.csv"
#     )

#     building_summary = pd.DataFrame(
#         [
#             {
#                 "district": district,
#                 "total_osm_mapped_buildings":
#                     total_buildings,
#                 "flood_affected_buildings":
#                     affected_count,
#                 "affected_buildings_percent":
#                     round(
#                         affected_percentage,
#                         2
#                     )
#             }
#         ]
#     )

#     building_summary.to_csv(
#         building_summary_path,
#         index=False
#     )

#     # --------------------------------------------------------
#     # BUILDING PREVIEW
#     # --------------------------------------------------------

#     building_preview_path = os.path.join(
#         BUILDING_DIR,
#         f"{district}_building_flood_preview.png"
#     )

#     fig, ax = plt.subplots(
#         figsize=(12, 12)
#     )

#     buildings.plot(
#         ax=ax,
#         linewidth=0.2,
#         alpha=0.35
#     )

#     if len(affected_buildings) > 0:

#         affected_buildings.plot(
#             ax=ax,
#             linewidth=0.5,
#             alpha=0.8
#         )

#     ax.set_title(
#         f"{district} — "
#         "OSM Buildings and Flood-Affected Buildings",
#         fontsize=14
#     )

#     ax.set_axis_off()

#     plt.tight_layout()

#     plt.savefig(
#         building_preview_path,
#         dpi=200,
#         bbox_inches="tight"
#     )

#     plt.close()

#     print(
#         "Building preview saved:",
#         building_preview_path
#     )

#     return {
#         "total_buildings": total_buildings,
#         "affected_buildings": affected_count,
#         "affected_percentage": affected_percentage
#     }


# # ============================================================
# # ROAD EXPOSURE
# # ============================================================

# def calculate_road_exposure(
#     district,
#     flood_raster_path,
#     aoi_geometry
# ):

#     print()
#     print("=" * 60)
#     print("ROAD NETWORK EXPOSURE")
#     print("District:", district)
#     print("=" * 60)

#     flood_gdf, flood_crs = (
#         create_flood_polygon(
#             flood_raster_path
#         )
#     )

#     if flood_gdf is None:

#         print(
#             "No flooded pixels found."
#         )

#         return None

#     district_geometry = (
#         get_district_geometry(
#             aoi_geometry
#         )
#     )

#     print(
#         "Downloading OSM road network..."
#     )

#     try:

#         road_graph = (
#             ox.graph_from_polygon(
#                 district_geometry,
#                 network_type="all",
#                 simplify=True
#             )
#         )

#         road_edges = (
#             ox.graph_to_gdfs(
#                 road_graph,
#                 nodes=False,
#                 edges=True
#             )
#         )

#     except Exception as error:

#         print(
#             "OSM road download failed:"
#         )

#         print(error)

#         return None

#     road_edges = (
#         road_edges[
#             road_edges.geometry.notnull()
#         ]
#         .copy()
#     )

#     if road_edges.crs is None:

#         road_edges = road_edges.set_crs(
#             "EPSG:4326"
#         )

#     else:

#         road_edges = (
#             road_edges.to_crs(
#                 "EPSG:4326"
#             )
#         )

#     total_segments = len(
#         road_edges
#     )

#     # --------------------------------------------------------
#     # PROJECT TO METRIC CRS
#     # --------------------------------------------------------

#     metric_crs = (
#         road_edges
#         .estimate_utm_crs()
#     )

#     road_edges_metric = (
#         road_edges.to_crs(
#             metric_crs
#         )
#     )

#     flood_gdf_metric = (
#         flood_gdf.to_crs(
#             metric_crs
#         )
#     )

#     flood_geometry = (
#         flood_gdf_metric
#         .geometry
#         .iloc[0]
#     )

#     # --------------------------------------------------------
#     # TOTAL ROAD LENGTH
#     # --------------------------------------------------------

#     road_edges_metric[
#         "road_length_m"
#     ] = (
#         road_edges_metric
#         .geometry
#         .length
#     )

#     total_road_length_km = (
#         road_edges_metric[
#             "road_length_m"
#         ]
#         .sum()
#         / 1000
#     )

#     # --------------------------------------------------------
#     # FLOOD INTERSECTION
#     # --------------------------------------------------------

#     road_edges_metric[
#         "flooded_geometry"
#     ] = (
#         road_edges_metric
#         .geometry
#         .intersection(
#             flood_geometry
#         )
#     )

#     road_edges_metric[
#         "flooded_length_m"
#     ] = (
#         road_edges_metric[
#             "flooded_geometry"
#         ]
#         .length
#     )

#     road_edges_metric[
#         "flooded_length_km"
#     ] = (
#         road_edges_metric[
#             "flooded_length_m"
#         ]
#         / 1000
#     )

#     road_edges_metric[
#         "flood_affected"
#     ] = (
#         road_edges_metric[
#             "flooded_length_m"
#         ]
#         > 0
#     )

#     affected_roads = (
#         road_edges_metric[
#             road_edges_metric[
#                 "flood_affected"
#             ]
#         ]
#         .copy()
#     )

#     affected_road_length_km = (
#         affected_roads[
#             "flooded_length_km"
#         ]
#         .sum()
#     )

#     affected_percentage = (
#         safe_percentage(
#             affected_road_length_km,
#             total_road_length_km
#         )
#     )

#     print(
#         "Total mapped road length:",
#         round(
#             total_road_length_km,
#             3
#         ),
#         "km"
#     )

#     print(
#         "Flood-affected road length:",
#         round(
#             affected_road_length_km,
#             3
#         ),
#         "km"
#     )

#     print(
#         f"Road network affected: "
#         f"{affected_percentage:.2f}%"
#     )

#     print(
#         "Flood-affected road segments:",
#         len(affected_roads)
#     )

#     # --------------------------------------------------------
#     # SAVE ROAD GEOPACKAGE
#     # --------------------------------------------------------

#     road_gpkg_path = os.path.join(
#         ROAD_DIR,
#         f"{district}_roads.gpkg"
#     )

#     remove_existing_file(
#         road_gpkg_path
#     )

#     roads_for_export = (
#         road_edges_metric
#         .drop(
#             columns=[
#                 "flooded_geometry"
#             ],
#             errors="ignore"
#         )
#         .to_crs(
#             "EPSG:4326"
#         )
#     )

#     affected_roads_export = (
#         affected_roads
#         .drop(
#             columns=[
#                 "flooded_geometry"
#             ],
#             errors="ignore"
#         )
#         .to_crs(
#             "EPSG:4326"
#         )
#     )

#     roads_for_export.to_file(
#         road_gpkg_path,
#         layer="all_roads",
#         driver="GPKG"
#     )

#     if len(affected_roads_export) > 0:

#         affected_roads_export.to_file(
#             road_gpkg_path,
#             layer="flood_affected_roads",
#             driver="GPKG"
#         )

#     # --------------------------------------------------------
#     # SAVE ROAD SUMMARY
#     # --------------------------------------------------------

#     road_summary_path = os.path.join(
#         OUTPUT_DIR,
#         f"{district}_road_summary.csv"
#     )

#     road_summary = pd.DataFrame(
#         [
#             {
#                 "district": district,
#                 "total_osm_mapped_road_length_km":
#                     round(
#                         total_road_length_km,
#                         3
#                     ),
#                 "flood_affected_road_length_km":
#                     round(
#                         affected_road_length_km,
#                         3
#                     ),
#                 "road_affected_percent":
#                     round(
#                         affected_percentage,
#                         2
#                     ),
#                 "total_mapped_road_segments":
#                     total_segments,
#                 "flood_affected_road_segments":
#                     len(affected_roads)
#             }
#         ]
#     )

#     road_summary.to_csv(
#         road_summary_path,
#         index=False
#     )

#     # --------------------------------------------------------
#     # ROAD PREVIEW
#     # --------------------------------------------------------

#     road_preview_path = os.path.join(
#         ROAD_DIR,
#         f"{district}_road_flood_preview.png"
#     )

#     fig, ax = plt.subplots(
#         figsize=(12, 12)
#     )

#     road_edges_metric.plot(
#         ax=ax,
#         linewidth=0.4,
#         alpha=0.5
#     )

#     if len(affected_roads) > 0:

#         affected_roads.plot(
#             ax=ax,
#             linewidth=1.5,
#             alpha=0.9
#         )

#     ax.set_title(
#         f"{district} — "
#         "OSM Road Network and Flood-Affected Roads",
#         fontsize=14
#     )

#     ax.set_axis_off()

#     plt.tight_layout()

#     plt.savefig(
#         road_preview_path,
#         dpi=200,
#         bbox_inches="tight"
#     )

#     plt.close()

#     print(
#         "Road preview saved:",
#         road_preview_path
#     )

#     return {
#         "total_road_length_km":
#             total_road_length_km,
#         "affected_road_length_km":
#             affected_road_length_km,
#         "affected_percentage":
#             affected_percentage,
#         "total_segments":
#             total_segments,
#         "affected_segments":
#             len(affected_roads)
#     }


# # ============================================================
# # MAIN EXECUTION
# # ============================================================

# print()
# print("=" * 70)
# print(
#     f"INFRASTRUCTURE ANALYSIS: {DISTRICT.upper()}"
# )
# print("=" * 70)


# # ------------------------------------------------------------
# # LOAD DISTRICT AOI
# # ------------------------------------------------------------

# if DISTRICT not in DISTRICT_ASSETS:

#     raise KeyError(
#         f"{DISTRICT} is not available "
#         "in DISTRICT_ASSETS."
#     )

# aoi = ee.FeatureCollection(
#     DISTRICT_ASSETS[DISTRICT]
# )

# aoi_geometry = (
#     aoi.geometry()
# )


# # ------------------------------------------------------------
# # EXISTING FLOOD RASTER
# # ------------------------------------------------------------

# flood_raster_path = os.path.join(
#     RASTER_DIR,
#     f"{DISTRICT}_flood_exposure.tif"
# )

# if not os.path.exists(
#     flood_raster_path
# ):

#     raise FileNotFoundError(
#         f"Existing flood raster not found:\n"
#         f"{flood_raster_path}"
#     )

# print()
# print(
#     "Using existing flood raster:"
# )

# print(
#     flood_raster_path
# )


# # ------------------------------------------------------------
# # BUILDING ANALYSIS
# # ------------------------------------------------------------

# building_results = None

# if RUN_BUILDING_ANALYSIS:

#     building_results = (
#         calculate_building_exposure(
#             DISTRICT,
#             flood_raster_path,
#             aoi_geometry
#         )
#     )


# # ------------------------------------------------------------
# # ROAD ANALYSIS
# # ------------------------------------------------------------

# road_results = None

# if RUN_ROAD_ANALYSIS:

#     road_results = (
#         calculate_road_exposure(
#             DISTRICT,
#             flood_raster_path,
#             aoi_geometry
#         )
#     )


# # ============================================================
# # COMPLETION
# # ============================================================

# print()
# print("=" * 70)
# print("INFRASTRUCTURE ANALYSIS COMPLETED")
# print("=" * 70)

# print()
# print("Building results:")
# print(building_results)

# print()
# print("Road results:")
# print(road_results)










# ============================================================
# INFRASTRUCTURE ANALYSIS
# BUILDING AND ROAD FLOOD EXPOSURE
# ============================================================

import os
import warnings

import ee
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio
import osmnx as ox

from rasterio.features import shapes
from shapely.geometry import shape
from shapely.ops import unary_union


from configuration import (
    EE_PROJECT,
    DISTRICT_ASSETS,
    OUTPUT_DIR,
    OSM_BUILDING_TAG
)


# ============================================================
# SETTINGS
# ============================================================

# Change only this district for the next run
DISTRICT = "Golaghat"

RUN_BUILDING_ANALYSIS = False
RUN_ROAD_ANALYSIS = True


# ============================================================
# INITIALIZATION
# ============================================================

warnings.filterwarnings(
    "ignore",
    message="Geometry is in a geographic CRS"
)

ee.Initialize(
    project=EE_PROJECT
)

print()
print("Earth Engine initialized successfully.")


# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

BUILDING_DIR = os.path.join(
    OUTPUT_DIR,
    "buildings"
)

ROAD_DIR = os.path.join(
    OUTPUT_DIR,
    "roads"
)

RASTER_DIR = os.path.join(
    OUTPUT_DIR,
    "raster"
)

os.makedirs(
    BUILDING_DIR,
    exist_ok=True
)

os.makedirs(
    ROAD_DIR,
    exist_ok=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_percentage(numerator, denominator):

    if denominator is None or denominator == 0:
        return 0

    return (
        numerator / denominator
    ) * 100


def remove_existing_file(file_path):

    if os.path.exists(file_path):

        os.remove(file_path)

        print(
            "Removed existing file:",
            file_path
        )


def create_flood_polygon(flood_raster_path):

    print()
    print("Creating flood polygon from raster...")

    with rasterio.open(
        flood_raster_path
    ) as src:

        flood_array = src.read(1)

        flood_transform = src.transform

        flood_crs = src.crs

    flood_mask = (
        flood_array > 0
    )

    if not flood_mask.any():

        print(
            "No flooded pixels found in raster."
        )

        return None, flood_crs

    flood_shapes = shapes(
        flood_array,
        mask=flood_mask,
        transform=flood_transform
    )

    flood_polygons = []

    for geometry, value in flood_shapes:

        if value > 0:

            flood_polygons.append(
                shape(geometry)
            )

    if len(flood_polygons) == 0:

        return None, flood_crs

    print(
        "Combining flood polygons..."
    )

    flood_union = unary_union(
        flood_polygons
    )

    # Repair invalid geometry if necessary
    if not flood_union.is_valid:

        print(
            "Repairing invalid flood geometry..."
        )

        flood_union = flood_union.buffer(0)

    flood_gdf = gpd.GeoDataFrame(
        {
            "flooded": [1]
        },
        geometry=[
            flood_union
        ],
        crs=flood_crs
    )

    print(
        "Flood polygon created successfully."
    )

    return flood_gdf, flood_crs


def get_district_geometry(aoi_geometry):

    district_geometry = shape(
        aoi_geometry.getInfo()
    )

    return district_geometry


def clean_columns_for_gpkg(gdf):

    """
    Convert list, dictionary, tuple, and set
    attributes into strings before saving to GPKG.
    """

    gdf = gdf.copy()

    for column in gdf.columns:

        if column == "geometry":
            continue

        if gdf[column].dtype == "object":

            gdf[column] = gdf[column].apply(
                lambda value: str(value)
                if isinstance(
                    value,
                    (list, dict, tuple, set)
                )
                else value
            )

    return gdf


# ============================================================
# BUILDING EXPOSURE
# ============================================================

def calculate_building_exposure(
    district,
    flood_raster_path,
    aoi_geometry
):

    print()
    print("=" * 60)
    print("BUILDING EXPOSURE")
    print("District:", district)
    print("=" * 60)

    # --------------------------------------------------------
    # CREATE FLOOD POLYGON
    # --------------------------------------------------------

    flood_gdf, flood_crs = (
        create_flood_polygon(
            flood_raster_path
        )
    )

    if flood_gdf is None:

        print(
            "No flooded pixels found."
        )

        return None

    flood_gdf_wgs84 = (
        flood_gdf.to_crs(
            "EPSG:4326"
        )
    )

    flood_polygon = (
        flood_gdf_wgs84
        .geometry
        .iloc[0]
    )

    district_geometry = (
        get_district_geometry(
            aoi_geometry
        )
    )

    # --------------------------------------------------------
    # DOWNLOAD OSM BUILDINGS
    # --------------------------------------------------------

    print()
    print(
        "Downloading OSM building footprints..."
    )

    try:

        buildings = (
            ox.features_from_polygon(
                district_geometry,
                tags=OSM_BUILDING_TAG
            )
        )

    except Exception as error:

        print()
        print(
            "OSM building download failed:"
        )

        print(error)

        return None

    # --------------------------------------------------------
    # CLEAN BUILDING DATA
    # --------------------------------------------------------

    buildings = (
        buildings[
            buildings.geometry.notnull()
        ]
        .copy()
    )

    buildings = buildings[
        buildings.geometry.geom_type.isin(
            [
                "Polygon",
                "MultiPolygon"
            ]
        )
    ].copy()

    if buildings.crs is None:

        buildings = buildings.set_crs(
            "EPSG:4326"
        )

    else:

        buildings = (
            buildings.to_crs(
                "EPSG:4326"
            )
        )

    # Repair invalid building geometries
    invalid_buildings = (
        ~buildings.geometry.is_valid
    )

    if invalid_buildings.any():

        print(
            "Repairing invalid building geometries..."
        )

        buildings.loc[
            invalid_buildings,
            "geometry"
        ] = (
            buildings.loc[
                invalid_buildings,
                "geometry"
            ]
            .buffer(0)
        )

    total_buildings = len(
        buildings
    )

    print()
    print(
        "Total OSM-mapped buildings:",
        total_buildings
    )

    # --------------------------------------------------------
    # FLOOD INTERSECTION
    # --------------------------------------------------------

    flood_intersection_gdf = (
        gpd.GeoDataFrame(
            {
                "flood": [1]
            },
            geometry=[
                flood_polygon
            ],
            crs="EPSG:4326"
        )
    )

    print()
    print(
        "Preparing spatial index for buildings..."
    )

    building_spatial_index = (
        buildings.sindex
    )

    print(
        "Filtering buildings using spatial index..."
    )

    # Find only buildings that may intersect
    # with the flood polygon
    candidate_indices = (
        building_spatial_index.query(
            flood_polygon,
            predicate="intersects"
        )
    )

    print(
        "Candidate buildings identified:",
        len(candidate_indices)
    )

    if len(candidate_indices) == 0:

        affected_buildings = (
            buildings.iloc[0:0]
            .copy()
        )

    else:

        candidate_buildings = (
            buildings.iloc[
                candidate_indices
            ]
            .copy()
        )

        print()
        print(
            "Performing final building intersection..."
        )

        affected_mask = (
            candidate_buildings.geometry.intersects(
                flood_polygon
            )
        )

        affected_buildings = (
            candidate_buildings[
                affected_mask
            ]
            .copy()
        )

        affected_buildings = (
            affected_buildings[
                ~affected_buildings.index.duplicated(
                    keep="first"
                )
            ]
            .copy()
        )

    affected_count = len(
        affected_buildings
    )

    affected_percentage = (
        safe_percentage(
            affected_count,
            total_buildings
        )
    )

    print()
    print(
        "Flood-affected buildings:",
        affected_count
    )

    print(
        f"Buildings affected: "
        f"{affected_percentage:.2f}%"
    )

    # --------------------------------------------------------
    # SAVE AFFECTED BUILDINGS
    # --------------------------------------------------------

    building_gpkg_path = os.path.join(
        BUILDING_DIR,
        f"{district}_affected_buildings.gpkg"
    )

    remove_existing_file(
        building_gpkg_path
    )

    export_columns = [
        column
        for column in [
            "osmid",
            "building",
            "geometry"
        ]
        if column in affected_buildings.columns
    ]

    affected_export = (
        affected_buildings[
            export_columns
        ]
        .copy()
    )

    affected_export = (
        affected_export
        .drop(
            columns=[
                "index_right"
            ],
            errors="ignore"
        )
    )

    affected_export = (
        clean_columns_for_gpkg(
            affected_export
        )
    )

    if len(affected_export) > 0:

        affected_export.to_file(
            building_gpkg_path,
            driver="GPKG"
        )

        print()
        print(
            "Affected buildings saved:",
            building_gpkg_path
        )

    else:

        print()
        print(
            "No affected buildings to save."
        )

    # --------------------------------------------------------
    # SAVE BUILDING SUMMARY
    # --------------------------------------------------------

    building_summary_path = os.path.join(
        OUTPUT_DIR,
        f"{district}_building_summary.csv"
    )

    building_summary = pd.DataFrame(
        [
            {
                "district": district,
                "total_osm_mapped_buildings":
                    total_buildings,
                "flood_affected_buildings":
                    affected_count,
                "affected_buildings_percent":
                    round(
                        affected_percentage,
                        2
                    )
            }
        ]
    )

    building_summary.to_csv(
        building_summary_path,
        index=False
    )

    print()
    print(
        "Building summary saved:",
        building_summary_path
    )

    # --------------------------------------------------------
    # BUILDING PREVIEW
    # --------------------------------------------------------

    print()
    print(
        "Creating building preview..."
    )

    building_preview_path = os.path.join(
        BUILDING_DIR,
        f"{district}_building_flood_preview.png"
    )

    fig, ax = plt.subplots(
        figsize=(12, 12)
    )

    # Plot only affected buildings.
    # This avoids rendering all buildings
    # in large districts.
    if len(affected_buildings) > 0:

        affected_buildings.plot(
            ax=ax,
            linewidth=0.4,
            alpha=0.8
        )

    # Plot flood boundary
    flood_intersection_gdf.boundary.plot(
        ax=ax,
        linewidth=1.2
    )

    ax.set_title(
        f"{district} — "
        "Flood-Affected OSM Buildings",
        fontsize=14
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(
        building_preview_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Building preview saved:",
        building_preview_path
    )

    return {
        "total_buildings": total_buildings,
        "affected_buildings": affected_count,
        "affected_percentage": affected_percentage
    }


# ============================================================
# ROAD EXPOSURE
# ============================================================

def calculate_road_exposure(
    district,
    flood_raster_path,
    aoi_geometry
):

    print()
    print("=" * 60)
    print("ROAD NETWORK EXPOSURE")
    print("District:", district)
    print("=" * 60)

    # --------------------------------------------------------
    # CREATE FLOOD POLYGON
    # --------------------------------------------------------

    flood_gdf, flood_crs = (
        create_flood_polygon(
            flood_raster_path
        )
    )

    if flood_gdf is None:

        print(
            "No flooded pixels found."
        )

        return None

    district_geometry = (
        get_district_geometry(
            aoi_geometry
        )
    )

    # --------------------------------------------------------
    # DOWNLOAD OSM ROAD NETWORK
    # --------------------------------------------------------

    print()
    print(
        "Downloading OSM road network..."
    )
    # # --------------------------------------------------------
    # # OSMNX ROAD DOWNLOAD SETTINGS
    # # --------------------------------------------------------

    # ox.settings.requests_timeout = 600

    # # Split large queries into smaller areas
    # # to reduce the size of each Overpass request.
    # ox.settings.max_query_area_size = 1e7

    # ox.settings.overpass_rate_limit = True

    # print()
    # print(
    #     "OSMnx road query subdivision enabled."
    # )

    # print(
    #     "Request timeout: 600 seconds."
    # )
    try:

        road_graph = (
            ox.graph_from_polygon(
                district_geometry,
                network_type="all",
                simplify=True
            )
        )

        road_edges = (
            ox.graph_to_gdfs(
                road_graph,
                nodes=False,
                edges=True
            )
        )

    except Exception as error:

        print()
        print(
            "OSM road download failed:"
        )

        print(error)

        return None

    # --------------------------------------------------------
    # CLEAN ROAD DATA
    # --------------------------------------------------------

    road_edges = (
        road_edges[
            road_edges.geometry.notnull()
        ]
        .copy()
    )

    if road_edges.crs is None:

        road_edges = road_edges.set_crs(
            "EPSG:4326"
        )

    else:

        road_edges = (
            road_edges.to_crs(
                "EPSG:4326"
            )
        )

    if len(road_edges) == 0:

        print(
            "No road segments found."
        )

        return None

    total_segments = len(
        road_edges
    )

    print()
    print(
        "Total mapped road segments:",
        total_segments
    )

    # --------------------------------------------------------
    # PROJECT TO METRIC CRS
    # --------------------------------------------------------

    metric_crs = (
        road_edges
        .estimate_utm_crs()
    )

    road_edges_metric = (
        road_edges.to_crs(
            metric_crs
        )
    )

    flood_gdf_metric = (
        flood_gdf.to_crs(
            metric_crs
        )
    )

    flood_geometry = (
        flood_gdf_metric
        .geometry
        .iloc[0]
    )

    # --------------------------------------------------------
    # TOTAL ROAD LENGTH
    # --------------------------------------------------------

    print()
    print(
        "Calculating total road length..."
    )

    road_edges_metric[
        "road_length_m"
    ] = (
        road_edges_metric
        .geometry
        .length
    )

    total_road_length_km = (
        road_edges_metric[
            "road_length_m"
        ]
        .sum()
        / 1000
    )

    # --------------------------------------------------------
    # FLOOD INTERSECTION
    # --------------------------------------------------------

    print()
    print(
        "Calculating road-flood intersection..."
    )

    road_edges_metric[
        "flooded_geometry"
    ] = (
        road_edges_metric
        .geometry
        .intersection(
            flood_geometry
        )
    )

    road_edges_metric[
        "flooded_length_m"
    ] = (
        road_edges_metric[
            "flooded_geometry"
        ]
        .length
    )

    road_edges_metric[
        "flooded_length_km"
    ] = (
        road_edges_metric[
            "flooded_length_m"
        ]
        / 1000
    )

    road_edges_metric[
        "flood_affected"
    ] = (
        road_edges_metric[
            "flooded_length_m"
        ]
        > 0
    )

    affected_roads = (
        road_edges_metric[
            road_edges_metric[
                "flood_affected"
            ]
        ]
        .copy()
    )

    affected_road_length_km = (
        affected_roads[
            "flooded_length_km"
        ]
        .sum()
    )

    affected_percentage = (
        safe_percentage(
            affected_road_length_km,
            total_road_length_km
        )
    )

    # --------------------------------------------------------
    # ROAD RESULTS
    # --------------------------------------------------------

    print()
    print(
        "Total mapped road length:",
        round(
            total_road_length_km,
            3
        ),
        "km"
    )

    print(
        "Flood-affected road length:",
        round(
            affected_road_length_km,
            3
        ),
        "km"
    )

    print(
        f"Road network affected: "
        f"{affected_percentage:.2f}%"
    )

    print(
        "Flood-affected road segments:",
        len(affected_roads)
    )

    # --------------------------------------------------------
    # SAVE ROAD GEOPACKAGE
    # --------------------------------------------------------

    road_gpkg_path = os.path.join(
        ROAD_DIR,
        f"{district}_roads.gpkg"
    )

    remove_existing_file(
        road_gpkg_path
    )

    # Remove helper geometry before export
    roads_for_export = (
        road_edges_metric
        .drop(
            columns=[
                "flooded_geometry"
            ],
            errors="ignore"
        )
        .to_crs(
            "EPSG:4326"
        )
    )

    affected_roads_export = (
        affected_roads
        .drop(
            columns=[
                "flooded_geometry"
            ],
            errors="ignore"
        )
        .to_crs(
            "EPSG:4326"
        )
    )

    # Convert list and dictionary attributes
    # into strings for GeoPackage compatibility
    roads_for_export = (
        clean_columns_for_gpkg(
            roads_for_export
        )
    )

    affected_roads_export = (
        clean_columns_for_gpkg(
            affected_roads_export
        )
    )

    print()
    print(
        "Saving all road segments..."
    )

    roads_for_export.to_file(
        road_gpkg_path,
        layer="all_roads",
        driver="GPKG"
    )

    if len(affected_roads_export) > 0:

        print(
            "Saving flood-affected road segments..."
        )

        affected_roads_export.to_file(
            road_gpkg_path,
            layer="flood_affected_roads",
            driver="GPKG"
        )

    print(
        "Road GeoPackage saved:",
        road_gpkg_path
    )

    # --------------------------------------------------------
    # SAVE ROAD SUMMARY
    # --------------------------------------------------------

    road_summary_path = os.path.join(
        OUTPUT_DIR,
        f"{district}_road_summary.csv"
    )

    road_summary = pd.DataFrame(
        [
            {
                "district": district,
                "total_osm_mapped_road_length_km":
                    round(
                        total_road_length_km,
                        3
                    ),
                "flood_affected_road_length_km":
                    round(
                        affected_road_length_km,
                        3
                    ),
                "road_affected_percent":
                    round(
                        affected_percentage,
                        2
                    ),
                "total_mapped_road_segments":
                    total_segments,
                "flood_affected_road_segments":
                    len(affected_roads)
            }
        ]
    )

    road_summary.to_csv(
        road_summary_path,
        index=False
    )

    print()
    print(
        "Road summary saved:",
        road_summary_path
    )

    # --------------------------------------------------------
    # ROAD PREVIEW
    # --------------------------------------------------------

    print()
    print(
        "Creating road preview..."
    )

    road_preview_path = os.path.join(
        ROAD_DIR,
        f"{district}_road_flood_preview.png"
    )

    fig, ax = plt.subplots(
        figsize=(12, 12)
    )

    # Plot all roads
    road_edges_metric.plot(
        ax=ax,
        linewidth=0.4,
        alpha=0.5
    )

    # Plot affected roads
    if len(affected_roads) > 0:

        affected_roads.plot(
            ax=ax,
            linewidth=1.5,
            alpha=0.9
        )

    ax.set_title(
        f"{district} — "
        "OSM Road Network and Flood-Affected Roads",
        fontsize=14
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.savefig(
        road_preview_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Road preview saved:",
        road_preview_path
    )

    return {
        "total_road_length_km":
            total_road_length_km,
        "affected_road_length_km":
            affected_road_length_km,
        "affected_percentage":
            affected_percentage,
        "total_segments":
            total_segments,
        "affected_segments":
            len(affected_roads)
    }


# ============================================================
# MAIN EXECUTION
# ============================================================

print()
print("=" * 70)
print(
    f"INFRASTRUCTURE ANALYSIS: {DISTRICT.upper()}"
)
print("=" * 70)


# ------------------------------------------------------------
# LOAD DISTRICT AOI
# ------------------------------------------------------------

if DISTRICT not in DISTRICT_ASSETS:

    raise KeyError(
        f"{DISTRICT} is not available "
        "in DISTRICT_ASSETS."
    )

aoi = ee.FeatureCollection(
    DISTRICT_ASSETS[DISTRICT]
)

aoi_geometry = (
    aoi.geometry()
)


# ------------------------------------------------------------
# EXISTING FLOOD RASTER
# ------------------------------------------------------------

flood_raster_path = os.path.join(
    RASTER_DIR,
    f"{DISTRICT}_flood_exposure.tif"
)

if not os.path.exists(
    flood_raster_path
):

    raise FileNotFoundError(
        f"Existing flood raster not found:\n"
        f"{flood_raster_path}"
    )

print()
print(
    "Using existing flood raster:"
)

print(
    flood_raster_path
)


# ------------------------------------------------------------
# BUILDING ANALYSIS
# ------------------------------------------------------------

building_results = None

if RUN_BUILDING_ANALYSIS:

    building_results = (
        calculate_building_exposure(
            DISTRICT,
            flood_raster_path,
            aoi_geometry
        )
    )


# ------------------------------------------------------------
# ROAD ANALYSIS
# ------------------------------------------------------------

road_results = None

if RUN_ROAD_ANALYSIS:

    road_results = (
        calculate_road_exposure(
            DISTRICT,
            flood_raster_path,
            aoi_geometry
        )
    )


# ============================================================
# COMPLETION
# ============================================================

print()
print("=" * 70)
print("INFRASTRUCTURE ANALYSIS COMPLETED")
print("=" * 70)

print()
print("Building results:")
print(building_results)

print()
print("Road results:")
print(road_results) 