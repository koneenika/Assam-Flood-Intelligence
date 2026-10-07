# # # ============================================================
# # # ASSAM FLOOD INTELLIGENCE
# # # DISTRICT-LEVEL FLOOD ANALYSIS
# # # ============================================================

# # ============================================================
# # SECTION 1 — IMPORTS, CONFIGURATION & AOI
# # ============================================================

# import ee

# from collections import Counter

# from configuration import (
#     EE_PROJECT,
#     DISTRICT_ASSETS,
#     DISTRICT_NAMES,
#     TEST_DISTRICT,
#     OUTPUT_DIR,

#     S1_COLLECTION,
#     S1_SEARCH_START,
#     S1_SEARCH_END,

#     DEM_COLLECTION,
#     GPM_COLLECTION,

#     PRE_START,
#     PRE_END,
#     FLOOD_START,
#     FLOOD_END,
#     POST_START,
#     POST_END,

#     S1_POLARIZATION,
#     S1_INSTRUMENT_MODE,

#     FLOOD_DIFFERENCE_THRESHOLD,

#     JRC_WATER_COLLECTION,
#     PERMANENT_WATER_THRESHOLD,

#     WORLDCOVER_COLLECTION,
#     WORLD_COVER_CROPLAND,
#     WORLD_COVER_TREE_COVER,
# )


# # ------------------------------------------------------------
# # Initialize Earth Engine
# # ------------------------------------------------------------

# ee.Initialize(project=EE_PROJECT)

# print("Test district:", TEST_DISTRICT)


# # ------------------------------------------------------------
# # Load test district
# # ------------------------------------------------------------

# aoi = ee.FeatureCollection(
#     DISTRICT_ASSETS[TEST_DISTRICT]
# )

# aoi_geometry = aoi.geometry()

# print("Number of AOI features:", aoi.size().getInfo())


# # # ============================================================
# # # SECTION 2 — SENTINEL-1 DATA AVAILABILITY
# # # ============================================================

# # s1 = (
# #     ee.ImageCollection(S1_COLLECTION)
# #     .filterBounds(aoi_geometry)
# #     .filterDate(
# #         S1_SEARCH_START,
# #         S1_SEARCH_END
# #     )
# #     .filter(
# #         ee.Filter.eq(
# #             "instrumentMode",
# #             S1_INSTRUMENT_MODE
# #         )
# #     )
# #     .filter(
# #         ee.Filter.listContains(
# #             "transmitterReceiverPolarisation",
# #             S1_POLARIZATION
# #         )
# #     )
# # )


# # # ------------------------------------------------------------
# # # Create time-period collections
# # # ------------------------------------------------------------

# # s1_pre = s1.filterDate(
# #     PRE_START,
# #     PRE_END
# # )

# # s1_flood = s1.filterDate(
# #     FLOOD_START,
# #     FLOOD_END
# # )

# # s1_post = s1.filterDate(
# #     POST_START,
# #     POST_END
# # )


# # # print()
# # # print("Sentinel-1 image availability")
# # # print("--------------------------------")
# # # print("Search window:", s1.size().getInfo())
# # # print("Pre-flood images:", s1_pre.size().getInfo())
# # # print("Flood-period images:", s1_flood.size().getInfo())
# # # print("Post-flood images:", s1_post.size().getInfo())


# # # ============================================================
# # # SECTION 3 — FIND A CONSISTENT SENTINEL-1 ORBIT/PASS
# # # ============================================================

# # def get_orbit_keys(collection):

# #     passes = collection.aggregate_array(
# #         "orbitProperties_pass"
# #     ).getInfo()

# #     orbits = collection.aggregate_array(
# #         "relativeOrbitNumber_start"
# #     ).getInfo()

# #     return [
# #         f"{p}_{int(o)}"
# #         for p, o in zip(passes, orbits)
# #     ]


# # # ------------------------------------------------------------
# # # Get orbit/pass combinations
# # # ------------------------------------------------------------

# # pre_keys = get_orbit_keys(s1_pre)
# # flood_keys = get_orbit_keys(s1_flood)

# # pre_counts = Counter(pre_keys)
# # flood_counts = Counter(flood_keys)


# # # ------------------------------------------------------------
# # # Find combinations present in both periods
# # # ------------------------------------------------------------

# # common_keys = (
# #     set(pre_counts)
# #     .intersection(flood_counts)
# # )

# # if not common_keys:

# #     raise RuntimeError(
# #         "No common Sentinel-1 orbit/pass combination "
# #         "exists between the pre-flood and flood periods."
# #     )


# # # ------------------------------------------------------------
# # # Score each common orbit/pass
# # #
# # # We select the combination with the largest minimum
# # # number of images available in both periods.
# # # ------------------------------------------------------------

# # orbit_scores = {
# #     key: min(
# #         pre_counts[key],
# #         flood_counts[key]
# #     )
# #     for key in common_keys
# # }

# # selected_key = max(
# #     orbit_scores,
# #     key=orbit_scores.get
# # )

# # selected_pass, selected_orbit = (
# #     selected_key.rsplit("_", 1)
# # )

# # selected_orbit = int(selected_orbit)


# # print()
# # print("Selected Sentinel-1 acquisition geometry")
# # print("------------------------------------------")
# # print("Orbit pass:", selected_pass)
# # print("Relative orbit:", selected_orbit)
# # print("Pre-flood images:", pre_counts[selected_key])
# # print("Flood-period images:", flood_counts[selected_key])


# # # ============================================================
# # # SECTION 4 — CREATE CONSISTENT SENTINEL-1 COMPOSITES
# # # ============================================================

# # s1_pre_consistent = (
# #     s1_pre
# #     .filter(
# #         ee.Filter.eq(
# #             "orbitProperties_pass",
# #             selected_pass
# #         )
# #     )
# #     .filter(
# #         ee.Filter.eq(
# #             "relativeOrbitNumber_start",
# #             selected_orbit
# #         )
# #     )
# #     .select(S1_POLARIZATION)
# # )


# # s1_flood_consistent = (
# #     s1_flood
# #     .filter(
# #         ee.Filter.eq(
# #             "orbitProperties_pass",
# #             selected_pass
# #         )
# #     )
# #     .filter(
# #         ee.Filter.eq(
# #             "relativeOrbitNumber_start",
# #             selected_orbit
# #         )
# #     )
# #     .select(S1_POLARIZATION)
# # )


# # print()
# # print("Consistent Sentinel-1 collections")
# # print("-----------------------------------")
# # print(
# #     "Pre-flood images:",
# #     s1_pre_consistent.size().getInfo()
# # )

# # print(
# #     "Flood-period images:",
# #     s1_flood_consistent.size().getInfo()
# # )


# # # ------------------------------------------------------------
# # # Median composites
# # # ------------------------------------------------------------

# # pre_vv = (
# #     s1_pre_consistent
# #     .median()
# #     .clip(aoi_geometry)
# # )

# # flood_vv = (
# #     s1_flood_consistent
# #     .median()
# #     .clip(aoi_geometry)
# # )


# # print("Pre-flood VV composite created.")
# # print("Flood-period VV composite created.")


# # # ============================================================
# # # SECTION 5 — SENTINEL-1 FLOOD CHANGE DETECTION
# # # ============================================================

# # # Sentinel-1 GRD VV values in this collection are represented
# # # in decibels (dB).
# # #
# # # flood VV - pre-flood VV
# # #
# # # A negative value therefore represents a decrease in
# # # backscatter during the flood period.
# # #
# # # Example:
# # #     -2 dB  = decrease of approximately 2 dB
# # #
# # # The configured threshold identifies pixels with a decrease
# # # greater than the chosen threshold.


# # vv_change = (
# #     flood_vv
# #     .subtract(pre_vv)
# # )


# # # ------------------------------------------------------------
# # # Candidate flood pixels
# # # ------------------------------------------------------------

# # candidate_flood = (
# #     vv_change
# #     .lt(FLOOD_DIFFERENCE_THRESHOLD)
# # )


# # # ------------------------------------------------------------
# # # Permanent water mask
# # #
# # # JRC Global Surface Water occurrence >= threshold
# # # is treated as permanent water and excluded from the
# # # flood mask.
# # # ------------------------------------------------------------

# # permanent_water = (
# #     ee.Image(JRC_WATER_COLLECTION)
# #     .select("occurrence")
# #     .gte(PERMANENT_WATER_THRESHOLD)
# # )


# # # ------------------------------------------------------------
# # # Final flood mask
# # # ------------------------------------------------------------

# # flood_mask = (
# #     candidate_flood
# #     .And(permanent_water.Not())
# #     .selfMask()
# #     .clip(aoi_geometry)
# # )


# # print()
# # print("Flood mask created.")
# # print(
# #     "Flood difference threshold:",
# #     FLOOD_DIFFERENCE_THRESHOLD,
# #     "dB"
# # )

# # print(
# #     "Permanent water threshold:",
# #     PERMANENT_WATER_THRESHOLD,
# #     "%"
# # )


# # # ============================================================
# # # SECTION 6 — TOTAL FLOODED AREA
# # # ============================================================

# # # Pixel area in square metres
# # pixel_area = ee.Image.pixelArea()


# # # ------------------------------------------------------------
# # # Flooded area
# # # ------------------------------------------------------------

# # flood_area_image = (
# #     pixel_area
# #     .updateMask(flood_mask)
# # )


# # flood_area_result = (
# #     flood_area_image
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # flood_area_m2 = (
# #     flood_area_result.get("area")
# # )


# # flood_area_km2 = ee.Number(
# #     ee.Algorithms.If(
# #         flood_area_m2,
# #         flood_area_m2,
# #         0
# #     )
# # ).divide(1e6)


# # # ------------------------------------------------------------
# # # Total district area
# # # ------------------------------------------------------------

# # district_area_result = (
# #     pixel_area
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # district_area_m2 = (
# #     district_area_result.get("area")
# # )


# # district_area_km2 = (
# #     ee.Number(district_area_m2)
# #     .divide(1e6)
# # )


# # # ------------------------------------------------------------
# # # Flood percentage
# # # ------------------------------------------------------------

# # flood_percentage = (
# #     flood_area_km2
# #     .divide(district_area_km2)
# #     .multiply(100)
# # )


# # print()
# # print("TOTAL FLOOD ASSESSMENT")
# # print("----------------------")
# # print("District:", TEST_DISTRICT)

# # print(
# #     "District area (km²):",
# #     district_area_km2.getInfo()
# # )

# # print(
# #     "Flooded area (km²):",
# #     flood_area_km2.getInfo()
# # )

# # print(
# #     "Flooded area (%):",
# #     flood_percentage.getInfo()
# # )


# # # ============================================================
# # # SECTION 7 — ESA WORLDCOVER BASELINE LAND-COVER MASKS
# # # ============================================================

# # # WorldCover is being used here only as a baseline land-cover
# # # reference for cropland and tree-cover exposure.
# # #
# # # The supervised LULC classification will be developed later.
# # #
# # # WorldCover class:
# # #     10 = Tree cover
# # #     40 = Cropland


# # worldcover = (
# #     ee.ImageCollection(WORLDCOVER_COLLECTION)
# #     .first()
# #     .select("Map")
# #     .clip(aoi_geometry)
# # )


# # cropland_mask = (
# #     worldcover
# #     .eq(WORLD_COVER_CROPLAND)
# # )


# # forest_mask = (
# #     worldcover
# #     .eq(WORLD_COVER_TREE_COVER)
# # )


# # print()
# # print("ESA WorldCover baseline loaded.")
# # print(
# #     "Cropland class:",
# #     WORLD_COVER_CROPLAND
# # )

# # print(
# #     "Tree-cover / forest class:",
# #     WORLD_COVER_TREE_COVER
# # )


# # # ============================================================
# # # SECTION 8 — FLOOD-AFFECTED CROPLAND
# # # ============================================================

# # # ------------------------------------------------------------
# # # Intersect flood mask with cropland
# # # ------------------------------------------------------------

# # flooded_cropland = (
# #     flood_mask
# #     .And(cropland_mask)
# #     .selfMask()
# # )


# # # ------------------------------------------------------------
# # # Flood-affected cropland area
# # # ------------------------------------------------------------

# # flooded_cropland_area_image = (
# #     pixel_area
# #     .updateMask(flooded_cropland)
# # )


# # flooded_cropland_result = (
# #     flooded_cropland_area_image
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # flooded_cropland_m2 = (
# #     flooded_cropland_result.get("area")
# # )


# # flooded_cropland_km2 = ee.Number(
# #     ee.Algorithms.If(
# #         flooded_cropland_m2,
# #         flooded_cropland_m2,
# #         0
# #     )
# # ).divide(1e6)


# # # ------------------------------------------------------------
# # # Total cropland area
# # # ------------------------------------------------------------

# # cropland_area_image = (
# #     pixel_area
# #     .updateMask(cropland_mask)
# # )


# # cropland_area_result = (
# #     cropland_area_image
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # cropland_area_m2 = (
# #     cropland_area_result.get("area")
# # )


# # cropland_area_km2 = (
# #     ee.Number(cropland_area_m2)
# #     .divide(1e6)
# # )


# # # ------------------------------------------------------------
# # # Percentage of cropland affected
# # # ------------------------------------------------------------

# # cropland_affected_percentage = (
# #     flooded_cropland_km2
# #     .divide(cropland_area_km2)
# #     .multiply(100)
# # )


# # print()
# # print("FLOOD-AFFECTED CROPLAND")

# # print(
# #     "Total cropland (km²):",
# #     cropland_area_km2.getInfo()
# # )

# # print(
# #     "Flood-affected cropland (km²):",
# #     flooded_cropland_km2.getInfo()
# # )

# # print(
# #     "Cropland affected (%):",
# #     cropland_affected_percentage.getInfo()
# # )


# # # ============================================================
# # # SECTION 9 — FLOOD-AFFECTED FOREST
# # # ============================================================

# # # ------------------------------------------------------------
# # # Intersect flood mask with forest/tree-cover mask
# # # ------------------------------------------------------------

# # flooded_forest = (
# #     flood_mask
# #     .And(forest_mask)
# #     .selfMask()
# # )


# # # ------------------------------------------------------------
# # # Flood-affected forest area
# # # ------------------------------------------------------------

# # flooded_forest_area_image = (
# #     pixel_area
# #     .updateMask(flooded_forest)
# # )


# # flooded_forest_result = (
# #     flooded_forest_area_image
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # flooded_forest_m2 = (
# #     flooded_forest_result.get("area")
# # )


# # flooded_forest_km2 = ee.Number(
# #     ee.Algorithms.If(
# #         flooded_forest_m2,
# #         flooded_forest_m2,
# #         0
# #     )
# # ).divide(1e6)


# # # ------------------------------------------------------------
# # # Total forest/tree-cover area
# # # ------------------------------------------------------------

# # forest_area_image = (
# #     pixel_area
# #     .updateMask(forest_mask)
# # )


# # forest_area_result = (
# #     forest_area_image
# #     .reduceRegion(
# #         reducer=ee.Reducer.sum(),
# #         geometry=aoi_geometry,
# #         scale=10,
# #         maxPixels=1e8
# #     )
# # )


# # forest_area_m2 = (
# #     forest_area_result.get("area")
# # )


# # forest_area_km2 = (
# #     ee.Number(forest_area_m2)
# #     .divide(1e6)
# # )


# # # ------------------------------------------------------------
# # # Percentage of forest/tree cover affected
# # # ------------------------------------------------------------

# # forest_affected_percentage = (
# #     flooded_forest_km2
# #     .divide(forest_area_km2)
# #     .multiply(100)
# # )


# # print()
# # print("FLOOD-AFFECTED FOREST")


# # print(
# #     "Total forest/tree cover (km²):",
# #     forest_area_km2.getInfo()
# # )

# # print(
# #     "Flood-affected forest (km²):",
# #     flooded_forest_km2.getInfo()
# # )

# # print(
# #     "Forest affected (%):",
# #     forest_affected_percentage.getInfo()
# # )


# # # # ============================================================
# # # # SECTION 10 — DOWNLOAD FLOOD MAP TO LOCAL OUTPUT
# # # # ============================================================

# # # import os
# # # import urllib.request


# # # # ------------------------------------------------------------
# # # # Output directory
# # # # ------------------------------------------------------------

# # # raster_output_dir = os.path.join(
# # #     OUTPUT_DIR,
# # #     "raster"
# # # )

# # # os.makedirs(
# # #     raster_output_dir,
# # #     exist_ok=True
# # # )


# # # # ------------------------------------------------------------
# # # # Create ONE combined flood exposure raster
# # # #
# # # # 1 = Other flooded area
# # # # 2 = Flood-affected cropland
# # # # 3 = Flood-affected forest
# # # # ------------------------------------------------------------

# # # combined_flood_map = (
# # #     ee.Image(0)
# # #     .where(flood_mask, 1)
# # #     .where(flooded_cropland, 2)
# # #     .where(flooded_forest, 3)
# # #     .selfMask()
# # #     .clip(aoi_geometry)
# # # )


# # # # ------------------------------------------------------------
# # # # Download settings
# # # #
# # # # 30 m is used here ONLY for the visualization GeoTIFF.
# # # # The flood-area calculations above remain at 10 m.
# # # # ------------------------------------------------------------

# # # download_scale = 30


# # # # ------------------------------------------------------------
# # # # Local filename
# # # # ------------------------------------------------------------

# # # output_filename = (
# # #     f"{TEST_DISTRICT.replace(' ', '_')}_flood_exposure.tif"
# # # )

# # # output_path = os.path.join(
# # #     raster_output_dir,
# # #     output_filename
# # # )


# # # # ------------------------------------------------------------
# # # # Get AOI geometry
# # # # ------------------------------------------------------------

# # # region = aoi_geometry.getInfo()["coordinates"]


# # # # ------------------------------------------------------------
# # # # Generate direct download URL
# # # # ------------------------------------------------------------

# # # print()
# # # print("================================================")
# # # print("PREPARING FLOOD MAP DOWNLOAD")
# # # print("================================================")

# # # print("District:", TEST_DISTRICT)
# # # print("Download resolution:", download_scale, "m")
# # # print("Output:", output_path)


# # # download_url = combined_flood_map.getDownloadURL({
# # #     "scale": download_scale,
# # #     "region": region,
# # #     "format": "GEO_TIFF"
# # # })


# # # # ------------------------------------------------------------
# # # # Download directly to local Output folder
# # # # ------------------------------------------------------------

# # # print()
# # # print("Downloading...")

# # # urllib.request.urlretrieve(
# # #     download_url,
# # #     output_path
# # # )


# # # # ------------------------------------------------------------
# # # # Confirm download
# # # # ------------------------------------------------------------

# # # if not os.path.exists(output_path):

# # #     raise RuntimeError(
# # #         "GeoTIFF download failed."
# # #     )


# # # file_size_mb = (
# # #     os.path.getsize(output_path)
# # #     / (1024 * 1024)
# # # )



# # # print("FLOOD MAP DOWNLOADED SUCCESSFULLY")
# # # print("================================================")

# # # print("File:", output_path)

# # # print(
# # #     "File size:",
# # #     round(file_size_mb, 2),
# # #     "MB"
# # # )

# # # print()
# # # print("Raster classes:")
# # # print("1 = Other flooded area")
# # # print("2 = Flood-affected cropland")
# # # print("3 = Flood-affected forest")

# # # print()
# # # print("The 10 m GEE analysis remains unchanged.")
# # # print("This 30 m GeoTIFF is the visual validation product.")

# # # ================================================================
# # # SECTION 11 — RAINFALL ANALYSIS
# # # ================================================================

# # print("\n================================================")
# # print("SECTION 11 — RAINFALL ANALYSIS")
# # print("================================================")

# # # GPM IMERG V07
# # #
# # # The Earth Engine GPM IMERG V07 dataset is:
# # # - half-hourly
# # # - precipitation band is in mm/hour
# # #
# # # Therefore, each observation is converted to rainfall depth:
# # #
# # # rainfall depth (mm) = precipitation rate (mm/hour) × 0.5 hour

# # gpm = (
# #     ee.ImageCollection(GPM_COLLECTION)
# #     .filterBounds(aoi_geometry)
# #     .filterDate(S1_SEARCH_START, S1_SEARCH_END)
# # )

# # gpm_count = gpm.size().getInfo()

# # print("GPM images available:", gpm_count)


# # # ------------------------------------------------
# # # Convert precipitation rate to 30-minute rainfall
# # # ------------------------------------------------

# # def convert_gpm_to_mm(image):

# #     rainfall_mm = (
# #         image
# #         .select("precipitation")
# #         .multiply(0.5)
# #         .rename("rainfall_mm")
# #     )

# #     return rainfall_mm.copyProperties(
# #         image,
# #         ["system:time_start"]
# #     )


# # gpm_rainfall = gpm.map(convert_gpm_to_mm)


# # # ------------------------------------------------
# # # Flood-period dates
# # # ------------------------------------------------

# # start_date = ee.Date(FLOOD_START)
# # end_date = ee.Date(FLOOD_END)

# # number_of_days = end_date.difference(
# #     start_date,
# #     "day"
# # ).toInt()

# # day_offsets = ee.List.sequence(
# #     0,
# #     number_of_days.subtract(1)
# # )


# # # ------------------------------------------------
# # # Calculate district-mean rainfall for each day
# # # ------------------------------------------------

# # def calculate_daily_rainfall(day_offset):

# #     day_offset = ee.Number(day_offset)

# #     day_start = start_date.advance(
# #         day_offset,
# #         "day"
# #     )

# #     day_end = day_start.advance(
# #         1,
# #         "day"
# #     )

# #     daily_images = (
# #         gpm_rainfall
# #         .filterDate(day_start, day_end)
# #     )

# #     daily_rainfall = (
# #         daily_images
# #         .sum()
# #         .rename("daily_rainfall")
# #         .clip(aoi_geometry)
# #     )

# #     district_mean = daily_rainfall.reduceRegion(
# #         reducer=ee.Reducer.mean(),
# #         geometry=aoi_geometry,
# #         scale=11132,
# #         maxPixels=1e9,
# #         bestEffort=True
# #     ).get("daily_rainfall")

# #     return ee.Feature(
# #         None,
# #         {
# #             "date": day_start.format("YYYY-MM-dd"),
# #             "rainfall_mm": district_mean
# #         }
# #     )


# # daily_rainfall_fc = ee.FeatureCollection(
# #     day_offsets.map(calculate_daily_rainfall)
# # )


# # # ------------------------------------------------
# # # Convert Earth Engine rainfall table to Python
# # # ------------------------------------------------

# # daily_rainfall_features = (
# #     daily_rainfall_fc
# #     .getInfo()["features"]
# # )

# # daily_rainfall_records = [
# #     feature["properties"]
# #     for feature in daily_rainfall_features
# # ]


# # # Remove days where no rainfall value was returned

# # daily_rainfall_records = [
# #     record
# #     for record in daily_rainfall_records
# #     if record.get("rainfall_mm") is not None
# # ]


# # print(
# #     "Flood-period rainfall days:",
# #     len(daily_rainfall_records)
# # )

# # print(
# #     "Daily rainfall records:",
# #     len(daily_rainfall_records)
# # )


# # # ------------------------------------------------
# # # Flood-period accumulated rainfall
# # # ------------------------------------------------

# # if len(daily_rainfall_records) > 0:

# #     flood_period_rainfall = sum(
# #         record["rainfall_mm"]
# #         for record in daily_rainfall_records
# #     )

# #     maximum_daily_rainfall = max(
# #         record["rainfall_mm"]
# #         for record in daily_rainfall_records
# #     )

# # else:

# #     flood_period_rainfall = None
# #     maximum_daily_rainfall = None


# # print(
# #     "Flood-period accumulated rainfall (mm):",
# #     flood_period_rainfall
# # )

# # print(
# #     "Maximum daily rainfall (district mean, mm):",
# #     maximum_daily_rainfall
# # )


# # # ================================================================
# # # SECTION 12 — ELEVATION ANALYSIS
# # # ================================================================

# # print("\n================================================")
# # print("SECTION 12 — ELEVATION ANALYSIS")
# # print("================================================")


# # # ------------------------------------------------
# # # Load Copernicus DEM GLO-30
# # # ------------------------------------------------

# # dem_collection = (
# #     ee.ImageCollection(DEM_COLLECTION)
# #     .filterBounds(aoi_geometry)
# # )


# # # ------------------------------------------------
# # # IMPORTANT:
# # # Earth Engine recommends setting the native
# # # projection after mosaicking this DEM collection.
# # # This is required for correct terrain calculations.
# # # ------------------------------------------------

# # native_projection = (
# #     dem_collection
# #     .first()
# #     .projection()
# # )

# # dem = (
# #     dem_collection
# #     .mosaic()
# #     .setDefaultProjection(native_projection)
# #     .select("DEM")
# #     .clip(aoi_geometry)
# # )


# # # ------------------------------------------------
# # # Elevation statistics
# # # ------------------------------------------------

# # elevation_stats = dem.reduceRegion(
# #     reducer=ee.Reducer.mean()
# #         .combine(
# #             reducer2=ee.Reducer.min(),
# #             sharedInputs=True
# #         )
# #         .combine(
# #             reducer2=ee.Reducer.max(),
# #             sharedInputs=True
# #         ),
# #     geometry=aoi_geometry,
# #     scale=30,
# #     maxPixels=1e9,
# #     bestEffort=True
# # ).getInfo()


# # mean_elevation = elevation_stats.get(
# #     "DEM_mean"
# # )

# # min_elevation = elevation_stats.get(
# #     "DEM_min"
# # )

# # max_elevation = elevation_stats.get(
# #     "DEM_max"
# # )


# # print(
# #     "Mean elevation (m):",
# #     mean_elevation
# # )

# # print(
# #     "Minimum elevation (m):",
# #     min_elevation
# # )

# # print(
# #     "Maximum elevation (m):",
# #     max_elevation
# # )


# # # ================================================================
# # # SECTION 13 — SLOPE ANALYSIS
# # # ================================================================

# # print("\n================================================")
# # print("SECTION 13 — SLOPE ANALYSIS")
# # print("================================================")


# # # ------------------------------------------------
# # # Calculate slope from the correctly projected DEM
# # # ------------------------------------------------

# # slope = (
# #     ee.Terrain
# #     .slope(dem)
# #     .rename("slope")
# # )


# # # ------------------------------------------------
# # # Keep only valid DEM pixels
# # # ------------------------------------------------

# # slope = (
# #     slope
# #     .updateMask(dem.mask())
# #     .clip(aoi_geometry)
# # )


# # # ------------------------------------------------
# # # Slope statistics
# # # ------------------------------------------------

# # slope_stats = slope.reduceRegion(
# #     reducer=ee.Reducer.mean()
# #         .combine(
# #             reducer2=ee.Reducer.min(),
# #             sharedInputs=True
# #         )
# #         .combine(
# #             reducer2=ee.Reducer.max(),
# #             sharedInputs=True
# #         ),
# #     geometry=aoi_geometry,
# #     scale=30,
# #     maxPixels=1e9,
# #     bestEffort=True
# # ).getInfo()


# # mean_slope = slope_stats.get(
# #     "slope_mean"
# # )

# # min_slope = slope_stats.get(
# #     "slope_min"
# # )

# # max_slope = slope_stats.get(
# #     "slope_max"
# # )


# # print(
# #     "Mean slope (degrees):",
# #     mean_slope
# # )

# # print(
# #     "Minimum slope (degrees):",
# #     min_slope
# # )

# # print(
# #     "Maximum slope (degrees):",
# #     max_slope
# # )


# # # ------------------------------------------------
# # # Safety check
# # # ------------------------------------------------

# # if (
# #     mean_slope is None
# #     or min_slope is None
# #     or max_slope is None
# # ):

# #     print("\nWARNING: Slope statistics are still None.")

# #     print(
# #         "The DEM contains no valid pixels for the requested AOI."
# #     )

# #     raise RuntimeError(
# #         "Slope calculation returned None."
# #     )


# # # # ================================================================
# # # # SECTION 14 — EXPORT RASTERS AND RAINFALL OUTPUTS
# # # # ================================================================

# # # print("\n================================================")
# # # print("SECTION 14 — EXPORT OUTPUTS")
# # # print("================================================")

# # # import os
# # # import urllib.request
# # # import pandas as pd
# # # import matplotlib.pyplot as plt


# # # # ------------------------------------------------
# # # # Create output folders
# # # # ------------------------------------------------

# # # raster_dir = os.path.join(
# # #     OUTPUT_DIR,
# # #     "raster"
# # # )

# # # graph_dir = os.path.join(
# # #     OUTPUT_DIR,
# # #     "graphs"
# # # )

# # # os.makedirs(
# # #     raster_dir,
# # #     exist_ok=True
# # # )

# # # os.makedirs(
# # #     graph_dir,
# # #     exist_ok=True
# # # )


# # # # ================================================================
# # # # PREPARE ELEVATION FOR EXPORT
# # # # ================================================================

# # # # Keep only valid DEM pixels.
# # # # Do NOT use unmask(0), because pixels outside
# # # # the district must remain NoData.

# # # elevation_export = (
# # #     dem
# # #     .updateMask(dem.mask())
# # #     .clip(aoi_geometry)
# # #     .toFloat()
# # #     .rename("elevation")
# # # )


# # # # ================================================================
# # # # PREPARE SLOPE FOR EXPORT
# # # # ================================================================

# # # # IMPORTANT:
# # # # Keep slope as a floating-point raster.
# # # #
# # # # Slope values are continuous values such as:
# # # # 0.0, 0.42, 1.87, 7.35, 18.6, 32.4, etc.
# # # #
# # # # We do NOT convert slope to integer.
# # # # We also do NOT unmask it with zero.

# # # slope_export = (
# # #     slope
# # #     .updateMask(dem.mask())
# # #     .clip(aoi_geometry)
# # #     .toFloat()
# # #     .rename("slope")
# # # )


# # # # ------------------------------------------------
# # # # Export region
# # # # ------------------------------------------------

# # # region = aoi_geometry.getInfo()


# # # # ================================================================
# # # # EXPORT ELEVATION TIFF
# # # # ================================================================

# # # elevation_filename = (
# # #     f"{TEST_DISTRICT}_elevation.tif"
# # # )

# # # elevation_path = os.path.join(
# # #     raster_dir,
# # #     elevation_filename
# # # )

# # # print(
# # #     f"\nPreparing: {elevation_filename}"
# # # )


# # # elevation_url = elevation_export.getDownloadURL({
# # #     "scale": 30,
# # #     "region": region,
# # #     "format": "GEO_TIFF",
# # #     "filePerBand": False
# # # })


# # # print(
# # #     f"Downloading: {elevation_filename}"
# # # )


# # # urllib.request.urlretrieve(
# # #     elevation_url,
# # #     elevation_path
# # # )


# # # print(
# # #     f"Saved: {elevation_path}"
# # # )


# # # if os.path.exists(elevation_path):

# # #     size_mb = (
# # #         os.path.getsize(elevation_path)
# # #         / (1024 * 1024)
# # #     )

# # #     print(
# # #         f"Size: {size_mb:.2f} MB"
# # #     )


# # # # ================================================================
# # # # EXPORT SLOPE TIFF
# # # # ================================================================

# # # slope_filename = (
# # #     f"{TEST_DISTRICT}_slope.tif"
# # # )

# # # slope_path = os.path.join(
# # #     raster_dir,
# # #     slope_filename
# # # )

# # # print(
# # #     f"\nPreparing: {slope_filename}"
# # # )


# # # # Explicitly export slope as FLOAT32.
# # # #
# # # # This preserves decimal slope values and prevents
# # # # accidental integer conversion.

# # # slope_url = slope_export.getDownloadURL({
# # #     "scale": 30,
# # #     "region": region,
# # #     "format": "GEO_TIFF",
# # #     "filePerBand": False
# # # })


# # # print(
# # #     f"Downloading: {slope_filename}"
# # # )


# # # urllib.request.urlretrieve(
# # #     slope_url,
# # #     slope_path
# # # )


# # # print(
# # #     f"Saved: {slope_path}"
# # # )


# # # if os.path.exists(slope_path):

# # #     size_mb = (
# # #         os.path.getsize(slope_path)
# # #         / (1024 * 1024)
# # #     )

# # #     print(
# # #         f"Size: {size_mb:.2f} MB"
# # #     )


# # # # ================================================================
# # # # RAINFALL CSV + PNG
# # # # ================================================================

# # # print(
# # #     "\nPreparing rainfall outputs..."
# # # )


# # # if len(daily_rainfall_records) > 0:

# # #     rainfall_df = pd.DataFrame(
# # #         daily_rainfall_records
# # #     )


# # #     # ------------------------------------------------
# # #     # Convert date
# # #     # ------------------------------------------------

# # #     rainfall_df["date"] = pd.to_datetime(
# # #         rainfall_df["date"]
# # #     )


# # #     # ------------------------------------------------
# # #     # Sort chronologically
# # #     # ------------------------------------------------

# # #     rainfall_df = rainfall_df.sort_values(
# # #         "date"
# # #     )


# # #     # ============================================================
# # #     # SAVE CSV
# # #     # ============================================================

# # #     rainfall_csv_filename = (
# # #         f"{TEST_DISTRICT}_daily_rainfall.csv"
# # #     )

# # #     rainfall_csv_path = os.path.join(
# # #         OUTPUT_DIR,
# # #         rainfall_csv_filename
# # #     )


# # #     rainfall_df.to_csv(
# # #         rainfall_csv_path,
# # #         index=False
# # #     )


# # #     print(
# # #         f"Saved: {rainfall_csv_path}"
# # #     )


# # #     # ============================================================
# # #     # SAVE PNG
# # #     # ============================================================

# # #     rainfall_graph_filename = (
# # #         f"{TEST_DISTRICT}_daily_rainfall.png"
# # #     )

# # #     rainfall_graph_path = os.path.join(
# # #         graph_dir,
# # #         rainfall_graph_filename
# # #     )


# # #     plt.figure(
# # #         figsize=(12, 5)
# # #     )


# # #     plt.plot(
# # #         rainfall_df["date"],
# # #         rainfall_df["rainfall_mm"],
# # #         marker="o",
# # #         linewidth=2
# # #     )


# # #     plt.xlabel(
# # #         "Date"
# # #     )


# # #     plt.ylabel(
# # #         "Daily rainfall (mm)"
# # #     )


# # #     plt.title(
# # #         f"{TEST_DISTRICT} — Daily Rainfall During Flood Period"
# # #     )


# # #     plt.xticks(
# # #         rotation=45
# # #     )


# # #     plt.grid(
# # #         True,
# # #         alpha=0.3
# # #     )


# # #     plt.tight_layout()


# # #     plt.savefig(
# # #         rainfall_graph_path,
# # #         dpi=300,
# # #         bbox_inches="tight"
# # #     )


# # #     plt.close()


# # #     print(
# # #         f"Saved: {rainfall_graph_path}"
# # #     )


# # # else:

# # #     rainfall_graph_path = None
# # #     rainfall_csv_path = None

# # #     print(
# # #         "No rainfall records available for graph or CSV."
# # #     )


# # # # ================================================================
# # # # SECTION 15 — DISTRICT SUMMARY
# # # # ================================================================

# # # print("\n================================================")
# # # print("SECTION 15 — DISTRICT SUMMARY")
# # # print("================================================")


# # # print(
# # #     f"\nDistrict: {TEST_DISTRICT}"
# # # )


# # # # ------------------------------------------------
# # # # RAINFALL
# # # # ------------------------------------------------

# # # print(
# # #     "\nRAINFALL"
# # # )


# # # print(
# # #     "Flood-period accumulated rainfall (mm):",
# # #     flood_period_rainfall
# # # )


# # # print(
# # #     "Maximum daily rainfall (mm):",
# # #     maximum_daily_rainfall
# # # )


# # # print(
# # #     "Number of rainfall days:",
# # #     len(daily_rainfall_records)
# # # )


# # # # ------------------------------------------------
# # # # ELEVATION
# # # # ------------------------------------------------

# # # print(
# # #     "\nELEVATION"
# # # )


# # # print(
# # #     "Minimum elevation (m):",
# # #     min_elevation
# # # )


# # # print(
# # #     "Mean elevation (m):",
# # #     mean_elevation
# # # )


# # # print(
# # #     "Maximum elevation (m):",
# # #     max_elevation
# # # )


# # # # ------------------------------------------------
# # # # SLOPE
# # # # ------------------------------------------------

# # # print(
# # #     "\nSLOPE"
# # # )


# # # print(
# # #     "Minimum slope (degrees):",
# # #     min_slope
# # # )


# # # print(
# # #     "Mean slope (degrees):",
# # #     mean_slope
# # # )


# # # print(
# # #     "Maximum slope (degrees):",
# # #     max_slope
# # # )


# # # # ------------------------------------------------
# # # # OUTPUT FILES
# # # # ------------------------------------------------

# # # print(
# # #     "\nOUTPUT FILES"
# # # )


# # # print(
# # #     "Elevation:",
# # #     elevation_path
# # # )


# # # print(
# # #     "Slope:",
# # #     slope_path
# # # )


# # # if rainfall_csv_path is not None:

# # #     print(
# # #         "Rainfall CSV:",
# # #         rainfall_csv_path
# # #     )


# # # if rainfall_graph_path is not None:

# # #     print(
# # #         "Rainfall PNG:",
# # #         rainfall_graph_path
# # #     )
# # # # ================================================================
# # # # SECTION 16 — BUILDING EXPOSURE ANALYSIS
# # # # ================================================================

# # # print("\n================================================")
# # # print("SECTION 16 — BUILDING EXPOSURE ANALYSIS")
# # # print("================================================")


# # # # ------------------------------------------------
# # # # IMPORTS REQUIRED FOR BUILDING ANALYSIS
# # # # ------------------------------------------------

# # # import os
# # # import pandas as pd
# # # import geopandas as gpd
# # # import osmnx as ox
# # # import rasterio
# # # from rasterio.features import shapes
# # # from shapely.geometry import shape
# # # from shapely.ops import unary_union


# # # # ------------------------------------------------
# # # # Define output directories again
# # # #
# # # # Sections 11–15 are currently commented out,
# # # # so we define raster_dir here independently.
# # # # ------------------------------------------------

# # # raster_dir = os.path.join(
# # #     OUTPUT_DIR,
# # #     "raster"
# # # )

# # # building_dir = os.path.join(
# # #     OUTPUT_DIR,
# # #     "buildings"
# # # )

# # # os.makedirs(
# # #     building_dir,
# # #     exist_ok=True
# # # )


# # # # ================================================================
# # # # 16.1 — LOAD EXISTING FLOOD EXPOSURE RASTER
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.1 — LOADING FLOOD EXPOSURE RASTER")
# # # print("================================================")


# # # # This is the flood raster we already successfully created.
# # # #
# # # # Classes:
# # # # 1 = Other flooded area
# # # # 2 = Flood-affected cropland
# # # # 3 = Flood-affected forest
# # # #
# # # # Therefore:
# # # # every pixel with value > 0 = flood extent

# # # flood_raster_path = os.path.join(
# # #     raster_dir,
# # #     f"{TEST_DISTRICT}_flood_exposure.tif"
# # # )


# # # print(
# # #     "Flood raster:",
# # #     flood_raster_path
# # # )


# # # if not os.path.exists(flood_raster_path):

# # #     raise FileNotFoundError(
# # #         f"\nFlood exposure raster not found:\n"
# # #         f"{flood_raster_path}"
# # #     )


# # # # ================================================================
# # # # 16.2 — CONVERT FLOOD RASTER TO POLYGON
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.2 — CREATING FLOOD POLYGON")
# # # print("================================================")


# # # with rasterio.open(
# # #     flood_raster_path
# # # ) as src:

# # #     flood_array = src.read(1)

# # #     flood_transform = src.transform

# # #     flood_crs = src.crs


# # # # ------------------------------------------------
# # # # Create binary flood mask
# # # # ------------------------------------------------

# # # flood_binary = (
# # #     flood_array > 0
# # # )


# # # # ------------------------------------------------
# # # # Convert flooded pixels into polygons
# # # # ------------------------------------------------

# # # flood_shapes = shapes(
# # #     flood_array,
# # #     mask=flood_binary,
# # #     transform=flood_transform
# # # )


# # # flood_polygons = []


# # # for geom, value in flood_shapes:

# # #     if value > 0:

# # #         flood_polygons.append(
# # #             shape(geom)
# # #         )


# # # if len(flood_polygons) == 0:

# # #     raise RuntimeError(
# # #         "No flooded pixels were found in the "
# # #         "flood exposure raster."
# # #     )


# # # print(
# # #     "Flood polygons created:",
# # #     len(flood_polygons)
# # # )


# # # # ------------------------------------------------
# # # # Dissolve all flood polygons
# # # # ------------------------------------------------

# # # print(
# # #     "Dissolving flood polygons..."
# # # )


# # # flood_polygon = unary_union(
# # #     flood_polygons
# # # )


# # # print(
# # #     "Flood polygon created successfully."
# # # )


# # # # ------------------------------------------------
# # # # Create flood GeoDataFrame
# # # # ------------------------------------------------

# # # flood_gdf = gpd.GeoDataFrame(
# # #     {
# # #         "class": ["Flood extent"]
# # #     },
# # #     geometry=[
# # #         flood_polygon
# # #     ],
# # #     crs=flood_crs
# # # )


# # # # ------------------------------------------------
# # # # Convert flood polygon to WGS84
# # # # ------------------------------------------------
# # # #
# # # # OSMnx expects geographic coordinates.
# # # # ------------------------------------------------

# # # flood_gdf_wgs84 = (
# # #     flood_gdf
# # #     .to_crs("EPSG:4326")
# # # )


# # # flood_polygon_wgs84 = (
# # #     flood_gdf_wgs84
# # #     .geometry
# # #     .iloc[0]
# # # )


# # # # ================================================================
# # # # 16.3 — PREPARE DISTRICT AOI
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.3 — PREPARING DISTRICT AOI")
# # # print("================================================")


# # # # aoi_geometry already comes from Section 1.

# # # aoi_geojson = (
# # #     aoi_geometry
# # #     .getInfo()
# # # )


# # # aoi_polygon = shape(
# # #     aoi_geojson
# # # )


# # # print(
# # #     "District:",
# # #     TEST_DISTRICT
# # # )


# # # # ================================================================
# # # # 16.4 — DOWNLOAD OSM BUILDING FOOTPRINTS
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.4 — DOWNLOADING OSM BUILDINGS")
# # # print("================================================")


# # # # Same basic building-tag approach used
# # # # in the Kenya flood workflow.

# # # tags = {
# # #     "building": True
# # # }


# # # print(
# # #     "Querying OpenStreetMap..."
# # # )


# # # buildings = ox.features_from_polygon(
# # #     aoi_polygon,
# # #     tags=tags
# # # )


# # # print(
# # #     "OSM features returned:",
# # #     len(buildings)
# # # )


# # # # ================================================================
# # # # 16.5 — KEEP BUILDING POLYGONS ONLY
# # # # ================================================================


# # # buildings = (
# # #     buildings[
# # #         buildings.geometry.notnull()
# # #     ]
# # #     .copy()
# # # )


# # # buildings = buildings[
# # #     buildings.geometry.geom_type.isin(
# # #         [
# # #             "Polygon",
# # #             "MultiPolygon"
# # #         ]
# # #     )
# # # ].copy()


# # # print(
# # #     "Valid building polygons:",
# # #     len(buildings)
# # # )


# # # # ------------------------------------------------
# # # # Make sure CRS is WGS84
# # # # ------------------------------------------------

# # # if buildings.crs is None:

# # #     buildings = buildings.set_crs(
# # #         "EPSG:4326"
# # #     )

# # # else:

# # #     buildings = buildings.to_crs(
# # #         "EPSG:4326"
# # #     )


# # # # ================================================================
# # # # 16.6 — TOTAL BUILDINGS
# # # # ================================================================

# # # total_buildings = len(
# # #     buildings
# # # )


# # # print(
# # #     "\nTotal OSM-mapped buildings in district:",
# # #     total_buildings
# # # )


# # # # ================================================================
# # # # 16.7 — FLOOD-AFFECTED BUILDINGS
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.7 — IDENTIFYING FLOOD-AFFECTED BUILDINGS")
# # # print("================================================")


# # # # Create flood GeoDataFrame for spatial join.

# # # flood_intersection_gdf = gpd.GeoDataFrame(
# # #     {
# # #         "flood": [1]
# # #     },
# # #     geometry=[
# # #         flood_polygon_wgs84
# # #     ],
# # #     crs="EPSG:4326"
# # # )


# # # # ------------------------------------------------
# # # # Spatial intersection
# # # #
# # # # A building is classified as flood-affected
# # # # when its footprint intersects the mapped
# # # # flood extent.
# # # #
# # # # NO BUFFER IS USED.
# # # # ------------------------------------------------

# # # affected_buildings = gpd.sjoin(
# # #     buildings,
# # #     flood_intersection_gdf,
# # #     how="inner",
# # #     predicate="intersects"
# # # )


# # # # ------------------------------------------------
# # # # Remove duplicate building records
# # # # ------------------------------------------------

# # # affected_buildings = (
# # #     affected_buildings[
# # #         ~affected_buildings.index.duplicated(
# # #             keep="first"
# # #         )
# # #     ]
# # #     .copy()
# # # )


# # # affected_building_count = len(
# # #     affected_buildings
# # # )


# # # print(
# # #     "Flood-affected buildings:",
# # #     affected_building_count
# # # )


# # # # ================================================================
# # # # 16.8 — BUILDING AFFECTED PERCENTAGE
# # # # ================================================================

# # # if total_buildings > 0:

# # #     affected_building_percentage = (
# # #         affected_building_count
# # #         / total_buildings
# # #         * 100
# # #     )

# # # else:

# # #     affected_building_percentage = 0


# # # print(
# # #     "Buildings affected (%):",
# # #     f"{affected_building_percentage:.2f}%"
# # # )


# # # # ================================================================
# # # # 16.9 — SAVE AFFECTED BUILDING FOOTPRINTS
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.9 — SAVING AFFECTED BUILDINGS")
# # # print("================================================")


# # # affected_buildings_path = os.path.join(
# # #     building_dir,
# # #     f"{TEST_DISTRICT}_affected_buildings.gpkg"
# # # )


# # # # Keep useful OSM attributes.

# # # useful_columns = [
# # #     column
# # #     for column in [
# # #         "osmid",
# # #         "building",
# # #         "geometry"
# # #     ]
# # #     if column in affected_buildings.columns
# # # ]


# # # affected_buildings_export = (
# # #     affected_buildings[
# # #         useful_columns
# # #     ]
# # #     .copy()
# # # )


# # # # Remove spatial join helper if present.

# # # if "index_right" in (
# # #     affected_buildings_export.columns
# # # ):

# # #     affected_buildings_export = (
# # #         affected_buildings_export
# # #         .drop(
# # #             columns=["index_right"]
# # #         )
# # #     )


# # # affected_buildings_export.to_file(
# # #     affected_buildings_path,
# # #     driver="GPKG"
# # # )


# # # print(
# # #     "Affected building footprints saved:"
# # # )

# # # print(
# # #     affected_buildings_path
# # # )


# # # # ================================================================
# # # # 16.10 — SAVE BUILDING SUMMARY CSV
# # # # ================================================================

# # # print("\n================================================")
# # # print("16.10 — SAVING BUILDING SUMMARY")
# # # print("================================================")


# # # building_summary = pd.DataFrame(
# # #     [
# # #         {
# # #             "district": TEST_DISTRICT,
# # #             "total_osm_mapped_buildings":
# # #                 total_buildings,
# # #             "flood_affected_buildings":
# # #                 affected_building_count,
# # #             "affected_buildings_percent":
# # #                 round(
# # #                     affected_building_percentage,
# # #                     2
# # #                 )
# # #         }
# # #     ]
# # # )


# # # building_summary_path = os.path.join(
# # #     OUTPUT_DIR,
# # #     f"{TEST_DISTRICT}_building_summary.csv"
# # # )


# # # building_summary.to_csv(
# # #     building_summary_path,
# # #     index=False
# # # )


# # # print(
# # #     "Building summary saved:"
# # # )

# # # print(
# # #     building_summary_path
# # # )


# # # # ================================================================
# # # # SECTION 17 — BUILDING ANALYSIS SUMMARY
# # # # ================================================================

# # # print("\n================================================")
# # # print("SECTION 17 — BUILDING ANALYSIS SUMMARY")
# # # print("================================================")


# # # print(
# # #     f"\nDistrict: {TEST_DISTRICT}"
# # # )


# # # print(
# # #     "\nBUILDINGS"
# # # )


# # # print(
# # #     "Total OSM-mapped buildings:",
# # #     total_buildings
# # # )


# # # print(
# # #     "Flood-affected buildings:",
# # #     affected_building_count
# # # )


# # # print(
# # #     "Buildings affected (%):",
# # #     f"{affected_building_percentage:.2f}%"
# # # )


# # # print(
# # #     "\nOUTPUT FILES"
# # # )


# # # print(
# # #     "Affected building footprints:",
# # #     affected_buildings_path
# # # )


# # # print(
# # #     "Building summary CSV:",
# # #     building_summary_path
# # # )

# # # # ============================================================
# # # # SECTION 18 — RIVER WATER-LEVEL DATA
# # # # ============================================================

# # # import os
# # # import pandas as pd


# # # # ------------------------------------------------------------
# # # # 18.1 OUTPUT DIRECTORY
# # # # ------------------------------------------------------------

# # # RIVER_DIR = os.path.join(
# # #     OUTPUT_DIR,
# # #     "river"
# # # )

# # # os.makedirs(
# # #     RIVER_DIR,
# # #     exist_ok=True
# # # )


# # # # ------------------------------------------------------------
# # # # 18.2 OFFICIAL GAUGE STATIONS RELEVANT TO OUR 11 DISTRICTS
# # # #
# # # # Danger Level and HFL are reference values from the
# # # # Government of Assam Water Resources Department.
# # # #
# # # # Actual observed water levels will be stored separately.
# # # # ------------------------------------------------------------

# # # RIVER_GAUGES = {

# # #     "Jorhat": {
# # #         "gauge": "Neamatighat",
# # #         "river": "Brahmaputra",
# # #         "danger_level_m": 85.04,
# # #         "hfl_m": 87.37,
# # #         "hfl_date": "11-07-1991"
# # #     },

# # #     "Sonitpur": {
# # #         "gauge": "Tezpur",
# # #         "river": "Brahmaputra",
# # #         "danger_level_m": 65.23,
# # #         "hfl_m": 66.59,
# # #         "hfl_date": "27-08-1988"
# # #     },

# # #     "Sonitpur_Jia_Bharali": {
# # #         "gauge": "NT Road Xing",
# # #         "river": "Jia Bharali",
# # #         "danger_level_m": 77.00,
# # #         "hfl_m": 78.50,
# # #         "hfl_date": "26-07-2007"
# # #     },

# # #     "Lakhimpur": {
# # #         "gauge": "Badatighat",
# # #         "river": "Subansiri",
# # #         "danger_level_m": 82.53,
# # #         "hfl_m": 86.84,
# # #         "hfl_date": "1972"
# # #     },

# # #     "Lakhimpur_Ranga_Nadi": {
# # #         "gauge": "Railway Bridge Cross",
# # #         "river": "Ranga Nadi",
# # #         "danger_level_m": 95.02,
# # #         "hfl_m": 96.84,
# # #         "hfl_date": "04-06-2008"
# # #     },

# # #     "Nagaon": {
# # #         "gauge": "Kampur",
# # #         "river": "Kopili",
# # #         "danger_level_m": 60.50,
# # #         "hfl_m": 61.86,
# # #         "hfl_date": "1973"
# # #     },

# # #     "Golaghat": {
# # #         "gauge": "Golaghat",
# # #         "river": "Dhansiri (South)",
# # #         "danger_level_m": 89.50,
# # #         "hfl_m": 91.30,
# # #         "hfl_date": "11-10-1986"
# # #     },

# # #     "Sivasagar": {
# # #         "gauge": "Sivasagar",
# # #         "river": "Dikhow",
# # #         "danger_level_m": 92.40,
# # #         "hfl_m": 95.62,
# # #         "hfl_date": "1974"
# # #     },

# # #     "Sivasagar_Desang": {
# # #         "gauge": "Nanglamoraghat",
# # #         "river": "Desang",
# # #         "danger_level_m": 94.46,
# # #         "hfl_m": 96.49,
# # #         "hfl_date": "06-09-1998"
# # #     }
# # # }


# # # # ------------------------------------------------------------
# # # # 18.3 CREATE GAUGE REFERENCE TABLE
# # # # ------------------------------------------------------------

# # # gauge_rows = []

# # # for district, info in RIVER_GAUGES.items():

# # #     gauge_rows.append({

# # #         "District": district,

# # #         "Gauge_Station":
# # #             info["gauge"],

# # #         "River":
# # #             info["river"],

# # #         "Danger_Level_m":
# # #             info["danger_level_m"],

# # #         "HFL_m":
# # #             info["hfl_m"],

# # #         "HFL_Date":
# # #             info["hfl_date"]
# # #     })


# # # gauge_df = pd.DataFrame(
# # #     gauge_rows
# # # )


# # # # ------------------------------------------------------------
# # # # 18.4 SAVE GAUGE REFERENCE DATA
# # # # ------------------------------------------------------------

# # # gauge_file = os.path.join(
# # #     RIVER_DIR,
# # #     "river_gauge_reference.csv"
# # # )

# # # gauge_df.to_csv(
# # #     gauge_file,
# # #     index=False
# # # )


# # # # ------------------------------------------------------------
# # # # 18.5 OBSERVED WATER-LEVEL DATA
# # # #
# # # # IMPORTANT:
# # # # These are ACTUAL reported observations.
# # # #
# # # # We only enter observations that have been verified.
# # # #
# # # # Source:
# # # # CWC-reported flood observations during July 2026.
# # # # ------------------------------------------------------------

# # # observations = [

# # #     {
# # #         "Date": "2026-07-20",
# # #         "Time": "18:00",
# # #         "Gauge_Station": "Neamatighat",
# # #         "River": "Brahmaputra",
# # #         "District": "Jorhat",
# # #         "Water_Level_m": 85.63,
# # #         "Trend": "Rising",
# # #         "Source": "CWC-reported observation"
# # #     },

# # #     {
# # #         "Date": "2026-07-24",
# # #         "Time": "09:00",
# # #         "Gauge_Station": "Sivasagar",
# # #         "River": "Dikhow",
# # #         "District": "Sivasagar",
# # #         "Water_Level_m": 94.26,
# # #         "Trend": "Falling",
# # #         "Source": "CWC-reported observation"
# # #     }
# # # ]


# # # observation_df = pd.DataFrame(
# # #     observations
# # # )


# # # # ------------------------------------------------------------
# # # # 18.6 ADD DANGER LEVEL + HFL TO OBSERVATIONS
# # # # ------------------------------------------------------------

# # # danger_lookup = {}

# # # hfl_lookup = {}

# # # for key, info in RIVER_GAUGES.items():

# # #     danger_lookup[info["gauge"]] = (
# # #         info["danger_level_m"]
# # #     )

# # #     hfl_lookup[info["gauge"]] = (
# # #         info["hfl_m"]
# # #     )


# # # observation_df["Danger_Level_m"] = (
# # #     observation_df["Gauge_Station"]
# # #     .map(danger_lookup)
# # # )


# # # observation_df["HFL_m"] = (
# # #     observation_df["Gauge_Station"]
# # #     .map(hfl_lookup)
# # # )


# # # # ------------------------------------------------------------
# # # # 18.7 CALCULATE DIFFERENCE FROM DANGER LEVEL
# # # # ------------------------------------------------------------

# # # observation_df["Difference_From_Danger_m"] = (
# # #     observation_df["Water_Level_m"]
# # #     -
# # #     observation_df["Danger_Level_m"]
# # # )


# # # # ------------------------------------------------------------
# # # # 18.8 CALCULATE DISTANCE BELOW / ABOVE HFL
# # # # ------------------------------------------------------------

# # # observation_df["Difference_From_HFL_m"] = (
# # #     observation_df["Water_Level_m"]
# # #     -
# # #     observation_df["HFL_m"]
# # # )


# # # # ------------------------------------------------------------
# # # # 18.9 FLOOD STATUS
# # # # ------------------------------------------------------------

# # # def classify_water_level(row):

# # #     level = row["Water_Level_m"]
# # #     danger = row["Danger_Level_m"]
# # #     hfl = row["HFL_m"]

# # #     if level >= hfl:

# # #         return "At / Above HFL"

# # #     elif level >= danger:

# # #         return "Above Danger Level"

# # #     else:

# # #         return "Below Danger Level"


# # # observation_df["Flood_Status"] = (
# # #     observation_df.apply(
# # #         classify_water_level,
# # #         axis=1
# # #     )
# # # )


# # # # ------------------------------------------------------------
# # # # 18.10 SAVE OBSERVATIONS
# # # # ------------------------------------------------------------

# # # observation_file = os.path.join(
# # #     RIVER_DIR,
# # #     "river_water_level_observations.csv"
# # # )

# # # observation_df.to_csv(
# # #     observation_file,
# # #     index=False
# # # )


# # # # ------------------------------------------------------------
# # # # 18.11 PRINT RESULTS
# # # # ------------------------------------------------------------

# # # print("\n" + "=" * 65)
# # # print("SECTION 18 — RIVER WATER-LEVEL DATA")
# # # print("=" * 65)


# # # print("\nOfficial gauge stations:")
# # # print(
# # #     gauge_df.to_string(
# # #         index=False
# # #     )
# # # )


# # # print("\n" + "-" * 65)
# # # print("VERIFIED WATER-LEVEL OBSERVATIONS")
# # # print("-" * 65)


# # # if len(observation_df) > 0:

# # #     print(
# # #         observation_df[
# # #             [
# # #                 "Date",
# # #                 "Time",
# # #                 "Gauge_Station",
# # #                 "River",
# # #                 "District",
# # #                 "Water_Level_m",
# # #                 "Danger_Level_m",
# # #                 "Difference_From_Danger_m",
# # #                 "Trend",
# # #                 "Flood_Status"
# # #             ]
# # #         ].to_string(
# # #             index=False
# # #         )
# # #     )

# # # else:

# # #     print(
# # #         "No verified observations available."
# # #     )


# # # print("\n")
# # # print(
# # #     f"Gauge reference saved to:\n"
# # #     f"{gauge_file}"
# # # )

# # # print(
# # #     f"\nWater-level observations saved to:\n"
# # #     f"{observation_file}"
# # # )


# # # # ------------------------------------------------------------
# # # # 18.12 DISTRICT COVERAGE CHECK
# # # # ------------------------------------------------------------

# # # print("\n" + "-" * 65)
# # # print("DISTRICT GAUGE COVERAGE")
# # # print("-" * 65)


# # # for district in DISTRICT_NAMES:

# # #     matching = gauge_df[
# # #         gauge_df["District"]
# # #         .astype(str)
# # #         .str.startswith(district)
# # #     ]

# # #     if len(matching) > 0:

# # #         print(
# # #             f"{district}: "
# # #             f"{len(matching)} gauge station(s)"
# # #         )

# # #     else:

# # #         print(
# # #             f"{district}: "
# # #             f"No listed gauge station"
# # #         )


# # # print("\n" + "=" * 65)
# # # print("SECTION 18 COMPLETE")
# # # print("=" * 65)


# # # ================================================================
# # # SECTION 19 — FINAL DISTRICT FLOOD INTELLIGENCE SUMMARY
# # # ================================================================

# # print("\n================================================")
# # print("SECTION 19 — FINAL DISTRICT FLOOD INTELLIGENCE SUMMARY")
# # print("================================================")

# # import os
# # import pandas as pd


# # # ================================================================
# # # 19.1 — FLOOD SUMMARY
# # # ================================================================
# # #
# # # IMPORTANT:
# # # These values come directly from Sections 6, 8 and 9.
# # #
# # # NO FLOOD AREA IS RECALCULATED HERE.
# # # The 10 m GEE calculations remain the authoritative source.
# # # ================================================================

# # print("\nFLOOD SUMMARY")
# # print("------------------------------")

# # district_area_value = district_area_km2.getInfo()
# # flooded_area_value = flood_area_km2.getInfo()

# # cropland_area_value = cropland_area_km2.getInfo()
# # flooded_cropland_value = flooded_cropland_km2.getInfo()
# # cropland_affected_value = cropland_affected_percentage.getInfo()

# # forest_area_value = forest_area_km2.getInfo()
# # flooded_forest_value = flooded_forest_km2.getInfo()
# # forest_affected_value = forest_affected_percentage.getInfo()


# # print(
# #     "District:",
# #     TEST_DISTRICT
# # )

# # print(
# #     "District area (km²):",
# #     round(district_area_value, 3)
# # )

# # print(
# #     "Flooded area (km²):",
# #     round(flooded_area_value, 3)
# # )

# # print(
# #     "Flooded area (%):",
# #     round(
# #         (flooded_area_value / district_area_value) * 100,
# #         3
# #     )
# # )

# # print(
# #     "Total cropland (km²):",
# #     round(cropland_area_value, 3)
# # )

# # print(
# #     "Flood-affected cropland (km²):",
# #     round(flooded_cropland_value, 3)
# # )

# # print(
# #     "Cropland affected (%):",
# #     round(cropland_affected_value, 3)
# # )

# # print(
# #     "Total forest/tree cover (km²):",
# #     round(forest_area_value, 3)
# # )

# # print(
# #     "Flood-affected forest (km²):",
# #     round(flooded_forest_value, 3)
# # )

# # print(
# #     "Forest affected (%):",
# #     round(forest_affected_value, 3)
# # )


# # # ================================================================
# # # 19.2 — RAINFALL SUMMARY
# # # ================================================================
# # #
# # # Values come directly from Section 11.
# # # NO rainfall is recalculated here.
# # # ================================================================

# # print("\nRAINFALL SUMMARY")
# # print("------------------------------")

# # if flood_period_rainfall is not None:

# #     print(
# #         "Flood-period accumulated rainfall (mm):",
# #         round(
# #             flood_period_rainfall,
# #             2
# #         )
# #     )

# # else:

# #     print(
# #         "Flood-period accumulated rainfall (mm):",
# #         "No data"
# #     )


# # if maximum_daily_rainfall is not None:

# #     print(
# #         "Maximum daily rainfall (mm):",
# #         round(
# #             maximum_daily_rainfall,
# #             2
# #         )
# #     )

# # else:

# #     print(
# #         "Maximum daily rainfall (mm):",
# #         "No data"
# #     )


# # # ================================================================
# # # 19.3 — ELEVATION SUMMARY
# # # ================================================================
# # #
# # # Values come directly from Section 12.
# # # ================================================================

# # print("\nELEVATION SUMMARY")
# # print("------------------------------")

# # print(
# #     "Mean elevation (m):",
# #     round(
# #         mean_elevation,
# #         2
# #     )
# # )

# # print(
# #     "Minimum elevation (m):",
# #     round(
# #         min_elevation,
# #         2
# #     )
# # )

# # print(
# #     "Maximum elevation (m):",
# #     round(
# #         max_elevation,
# #         2
# #     )
# # )


# # # ================================================================
# # # 19.4 — SLOPE SUMMARY
# # # ================================================================
# # #
# # # Values come directly from Section 13.
# # # ================================================================

# # print("\nSLOPE SUMMARY")
# # print("------------------------------")

# # print(
# #     "Mean slope (degrees):",
# #     round(
# #         mean_slope,
# #         2
# #     )
# # )

# # print(
# #     "Minimum slope (degrees):",
# #     round(
# #         min_slope,
# #         2
# #     )
# # )

# # print(
# #     "Maximum slope (degrees):",
# #     round(
# #         max_slope,
# #         2
# #     )
# # )


# # # ================================================================
# # # 19.5 — BUILDING SUMMARY
# # # ================================================================
# # #
# # # IMPORTANT:
# # # We DO NOT rerun Sections 16–17.
# # #
# # # We only read the building summary CSV that was already created.
# # # If the file does not exist, the building section is reported
# # # as unavailable rather than being recalculated.
# # # ================================================================

# # print("\nBUILDING SUMMARY")
# # print("------------------------------")

# # building_summary_path = os.path.join(
# #     OUTPUT_DIR,
# #     f"{TEST_DISTRICT}_building_summary.csv"
# # )


# # if os.path.exists(building_summary_path):

# #     building_df = pd.read_csv(
# #         building_summary_path
# #     )

# #     if len(building_df) > 0:

# #         building_row = building_df.iloc[0]

# #         total_buildings_value = int(
# #             building_row[
# #                 "total_osm_mapped_buildings"
# #             ]
# #         )

# #         affected_buildings_value = int(
# #             building_row[
# #                 "flood_affected_buildings"
# #             ]
# #         )

# #         affected_buildings_percentage_value = float(
# #             building_row[
# #                 "affected_buildings_percent"
# #             ]
# #         )

# #         print(
# #             "Total OSM-mapped buildings:",
# #             total_buildings_value
# #         )

# #         print(
# #             "Flood-affected buildings:",
# #             affected_buildings_value
# #         )

# #         print(
# #             "Buildings affected (%):",
# #             f"{affected_buildings_percentage_value:.2f}%"
# #         )

# #     else:

# #         print(
# #             "Building summary file is empty."
# #         )

# # else:

# #     total_buildings_value = None
# #     affected_buildings_value = None
# #     affected_buildings_percentage_value = None

# #     print(
# #         "Building analysis has not been run yet."
# #     )

# #     print(
# #         "Run Sections 16–17 once to create the building outputs."
# #     )


# # # ================================================================
# # # 19.6 — CREATE FINAL SUMMARY TABLE
# # # ================================================================

# # summary_data = {
# #     "district": TEST_DISTRICT,

# #     "district_area_km2":
# #         district_area_value,

# #     "flooded_area_km2":
# #         flooded_area_value,

# #     "flooded_area_percent":
# #         (flooded_area_value / district_area_value) * 100,

# #     "total_cropland_km2":
# #         cropland_area_value,

# #     "flooded_cropland_km2":
# #         flooded_cropland_value,

# #     "cropland_affected_percent":
# #         cropland_affected_value,

# #     "total_forest_km2":
# #         forest_area_value,

# #     "flooded_forest_km2":
# #         flooded_forest_value,

# #     "forest_affected_percent":
# #         forest_affected_value,

# #     "flood_period_rainfall_mm":
# #         flood_period_rainfall,

# #     "maximum_daily_rainfall_mm":
# #         maximum_daily_rainfall,

# #     "mean_elevation_m":
# #         mean_elevation,

# #     "minimum_elevation_m":
# #         min_elevation,

# #     "maximum_elevation_m":
# #         max_elevation,

# #     "mean_slope_degrees":
# #         mean_slope,

# #     "minimum_slope_degrees":
# #         min_slope,

# #     "maximum_slope_degrees":
# #         max_slope,

# #     "total_osm_mapped_buildings":
# #         total_buildings_value,

# #     "flood_affected_buildings":
# #         affected_buildings_value,

# #     "buildings_affected_percent":
# #         affected_buildings_percentage_value,
# # }


# # summary_df = pd.DataFrame(
# #     [summary_data]
# # )


# # # ================================================================
# # # 19.7 — SAVE FINAL DISTRICT SUMMARY
# # # ================================================================

# # final_summary_path = os.path.join(
# #     OUTPUT_DIR,
# #     f"{TEST_DISTRICT}_flood_intelligence_summary.csv"
# # )


# # summary_df.to_csv(
# #     final_summary_path,
# #     index=False
# # )


# # print("\n================================================")
# # print("FINAL SUMMARY SAVED")
# # print("================================================")

# # print(
# #     "File:",
# #     final_summary_path
# # )

# # print("\nDistrict summary:")
# # print(
# #     summary_df.to_string(
# #         index=False
# #     )
# # )

# # print("\n================================================")
# # print("SECTION 19 COMPLETE")
# # print("================================================")


# # ================================================================
# # ================================================================
# # SECTION 20 — ROAD NETWORK & FLOOD-AFFECTED ROAD ANALYSIS
# # ================================================================

# print("\n================================================")
# print("SECTION 20 — ROAD NETWORK & FLOOD-AFFECTED ROADS")
# print("================================================")


# # ------------------------------------------------
# # 20.1 — IMPORTS
# # ------------------------------------------------

# import os
# import pandas as pd
# import geopandas as gpd
# import osmnx as ox
# import rasterio

# from rasterio.features import shapes
# from shapely.geometry import shape
# from shapely.ops import unary_union


# # ================================================================
# # 20.2 — OUTPUT PATHS
# # ================================================================

# road_output_dir = os.path.join(
#     OUTPUT_DIR,
#     "roads"
# )

# os.makedirs(
#     road_output_dir,
#     exist_ok=True
# )


# flood_raster_path = os.path.join(
#     OUTPUT_DIR,
#     "raster",
#     f"{TEST_DISTRICT}_flood_exposure.tif"
# )


# road_gpkg_path = os.path.join(
#     road_output_dir,
#     f"{TEST_DISTRICT}_roads.gpkg"
# )


# road_summary_path = os.path.join(
#     OUTPUT_DIR,
#     f"{TEST_DISTRICT}_road_summary.csv"
# )


# road_preview_path = os.path.join(
#     road_output_dir,
#     f"{TEST_DISTRICT}_road_flood_preview.png"
# )


# # ================================================================
# # 20.3 — CHECK FLOOD RASTER
# # ================================================================

# print("\nChecking flood raster...")


# if not os.path.exists(flood_raster_path):

#     print(
#         "\nERROR: Flood exposure raster not found."
#     )

#     print(
#         flood_raster_path
#     )

#     print(
#         "\nPlease run Section 10 first."
#     )

#     raise FileNotFoundError(
#         flood_raster_path
#     )


# print(
#     "Flood raster found:"
# )

# print(
#     flood_raster_path
# )


# # ================================================================
# # 20.4 — LOAD DISTRICT BOUNDARY
# # ================================================================

# print(
#     "\nLoading district boundary..."
# )


# # ------------------------------------------------
# # Convert Earth Engine geometry to Shapely geometry
# # ------------------------------------------------

# district_geometry = shape(
#     aoi_geometry.getInfo()
# )


# # ------------------------------------------------
# # Create GeoDataFrame
# # IMPORTANT:
# # geometry is explicitly supplied using geometry=
# # ------------------------------------------------

# district_gdf = gpd.GeoDataFrame(
#     {
#         "district": [TEST_DISTRICT]
#     },
#     geometry=[district_geometry],
#     crs="EPSG:4326"
# )


# print(
#     "District boundary loaded:"
# )

# print(
#     TEST_DISTRICT
# )


# # ================================================================
# # 20.5 — DOWNLOAD OSM ROAD NETWORK
# # ================================================================

# print(
#     "\nDownloading OSM road network..."
# )

# print(
#     "This may take a little while..."
# )


# try:

#     road_graph = ox.graph_from_polygon(
#         district_geometry,
#         network_type="drive",
#         simplify=True
#     )

# except Exception as e:

#     print(
#         "\nERROR while downloading OSM road network:"
#     )

#     print(e)

#     raise


# print(
#     "OSM road network downloaded successfully."
# )


# # ================================================================
# # 20.6 — CONVERT ROAD GRAPH TO GEODATAFRAME
# # ================================================================

# print(
#     "\nConverting road network to GeoDataFrame..."
# )


# road_nodes, road_edges = ox.graph_to_gdfs(
#     road_graph,
#     nodes=True,
#     edges=True
# )


# road_edges = road_edges.reset_index()


# # ------------------------------------------------
# # Keep only valid road geometries
# # ------------------------------------------------

# road_edges = road_edges[
#     road_edges.geometry.notnull()
# ].copy()


# # ------------------------------------------------
# # Remove duplicate geometries
# # ------------------------------------------------

# road_edges = road_edges.drop_duplicates(
#     subset="geometry"
# )


# print(
#     "Mapped OSM road segments:",
#     len(road_edges)
# )


# # ================================================================
# # 20.7 — PROJECT TO LOCAL METRIC CRS
# # ================================================================

# print(
#     "\nProjecting data to local metric CRS..."
# )


# metric_crs = district_gdf.estimate_utm_crs()


# print(
#     "Metric CRS:",
#     metric_crs
# )


# road_edges = road_edges.to_crs(
#     metric_crs
# )


# district_metric = district_gdf.to_crs(
#     metric_crs
# )


# # ================================================================
# # 20.8 — CLIP ROADS TO DISTRICT
# # ================================================================

# print(
#     "\nClipping roads to district boundary..."
# )


# road_edges = gpd.clip(
#     road_edges,
#     district_metric
# )


# road_edges = road_edges[
#     road_edges.geometry.notnull()
# ].copy()


# # ------------------------------------------------
# # Remove empty geometries
# # ------------------------------------------------

# road_edges = road_edges[
#     ~road_edges.geometry.is_empty
# ].copy()


# print(
#     "Road segments after clipping:",
#     len(road_edges)
# )


# # ================================================================
# # 20.9 — CALCULATE TOTAL ROAD LENGTH
# # ================================================================

# print(
#     "\nCalculating total mapped road length..."
# )


# road_edges["length_m"] = (
#     road_edges.geometry.length
# )


# road_edges["length_km"] = (
#     road_edges["length_m"] / 1000
# )


# total_road_length_km = (
#     road_edges["length_km"].sum()
# )


# print(
#     "Total OSM-mapped road length:",
#     round(
#         total_road_length_km,
#         3
#     ),
#     "km"
# )


# # ================================================================
# # 20.10 — READ EXISTING FLOOD RASTER
# # ================================================================

# print(
#     "\nReading existing flood exposure raster..."
# )


# with rasterio.open(
#     flood_raster_path
# ) as src:

#     flood_array = src.read(1)

#     raster_transform = src.transform

#     raster_crs = src.crs


# print(
#     "Flood raster CRS:",
#     raster_crs
# )


# # ================================================================
# # 20.11 — CREATE FLOOD MASK
# # ================================================================

# print(
#     "\nCreating flood mask..."
# )


# # ------------------------------------------------
# # Existing flood exposure raster classes:
# #
# # 0 = No flood
# # 1 = Other flooded area
# # 2 = Flood-affected cropland
# # 3 = Flood-affected forest
# #
# # Therefore:
# #
# # value >= 1 = flooded
# # ------------------------------------------------

# flood_mask = (
#     flood_array >= 1
# )


# flood_pixel_count = int(
#     flood_mask.sum()
# )


# print(
#     "Flooded raster pixels:",
#     flood_pixel_count
# )


# if flood_pixel_count == 0:

#     print(
#         "\nNo flooded pixels were found."
#     )

#     print(
#         "Road analysis cannot continue."
#     )

#     raise ValueError(
#         "Flood raster contains no flooded pixels."
#     )


# # ================================================================
# # 20.12 — VECTORIZE FLOOD MASK
# # ================================================================

# print(
#     "\nConverting flood mask to polygon..."
# )


# flood_shapes = shapes(
#     flood_mask.astype("uint8"),
#     mask=flood_mask,
#     transform=raster_transform
# )


# flood_polygons = []


# for geom, value in flood_shapes:

#     if value == 1:

#         flood_polygons.append(
#             shape(geom)
#         )


# print(
#     "Flood polygons created:",
#     len(flood_polygons)
# )


# if len(flood_polygons) == 0:

#     print(
#         "\nNo flood polygons were created."
#     )

#     raise ValueError(
#         "Flood raster could not be converted to polygons."
#     )


# # ------------------------------------------------
# # Merge all flood polygons
# # ------------------------------------------------

# flood_union = unary_union(
#     flood_polygons
# )


# # ------------------------------------------------
# # Create GeoDataFrame
# # ------------------------------------------------

# flood_gdf = gpd.GeoDataFrame(
#     {
#         "flooded": [1]
#     },
#     geometry=[flood_union],
#     crs=raster_crs
# )


# # ================================================================
# # 20.13 — PROJECT FLOOD POLYGON TO ROAD CRS
# # ================================================================

# flood_gdf = flood_gdf.to_crs(
#     metric_crs
# )


# flood_geometry = (
#     flood_gdf.geometry.iloc[0]
# )


# print(
#     "Flood polygon projected to road CRS."
# )


# # ================================================================
# # 20.14 — CALCULATE FLOOD-AFFECTED ROAD PORTIONS
# # ================================================================

# print(
#     "\nCalculating flood-affected road segments..."
# )


# # ------------------------------------------------
# # Intersect every road with flood extent
# # ------------------------------------------------

# road_edges["flooded_geometry"] = (
#     road_edges.geometry.intersection(
#         flood_geometry
#     )
# )


# # ------------------------------------------------
# # Calculate length of the portion of each road
# # that falls inside the flood extent
# # ------------------------------------------------

# road_edges["flooded_length_m"] = (
#     road_edges[
#         "flooded_geometry"
#     ].length
# )


# road_edges["flooded_length_km"] = (
#     road_edges[
#         "flooded_length_m"
#     ] / 1000
# )


# # ------------------------------------------------
# # A road segment is considered affected when
# # any part of the segment intersects the flood
# # extent.
# # ------------------------------------------------

# road_edges["flood_affected"] = (
#     road_edges[
#         "flooded_length_m"
#     ] > 0
# )


# # ================================================================
# # 20.15 — EXTRACT FLOOD-AFFECTED ROADS
# # ================================================================

# affected_roads = road_edges[
#     road_edges["flood_affected"]
# ].copy()


# # ------------------------------------------------
# # Total length of affected road portions
# # ------------------------------------------------

# flooded_road_length_km = (
#     affected_roads[
#         "flooded_length_km"
#     ].sum()
# )


# # ------------------------------------------------
# # Percentage of mapped road network affected
# # ------------------------------------------------

# if total_road_length_km > 0:

#     road_affected_percent = (

#         flooded_road_length_km
#         /
#         total_road_length_km
#         *
#         100

#     )

# else:

#     road_affected_percent = 0


# # ================================================================
# # 20.16 — ROAD SUMMARY
# # ================================================================

# print(
#     "\nROAD SUMMARY"
# )

# print(
#     "------------------------------"
# )

# print(
#     "District:",
#     TEST_DISTRICT
# )

# print(
#     "Total OSM-mapped road length:",
#     round(
#         total_road_length_km,
#         3
#     ),
#     "km"
# )

# print(
#     "Flood-affected road length:",
#     round(
#         flooded_road_length_km,
#         3
#     ),
#     "km"
# )

# print(
#     "Roads affected (%):",
#     round(
#         road_affected_percent,
#         2
#     ),
#     "%"
# )

# print(
#     "Total mapped road segments:",
#     len(road_edges)
# )

# print(
#     "Flood-affected road segments:",
#     len(affected_roads)
# )


# # ================================================================
# # 20.17 — SAVE ALL ROADS
# # ================================================================

# print(
#     "\nSaving complete road network..."
# )


# roads_for_export = road_edges.drop(
#     columns=[
#         "flooded_geometry"
#     ],
#     errors="ignore"
# )


# roads_for_export.to_file(
#     road_gpkg_path,
#     layer="all_roads",
#     driver="GPKG"
# )


# print(
#     "All roads saved."
# )


# # ================================================================
# # 20.18 — SAVE FLOOD-AFFECTED ROADS
# # ================================================================

# print(
#     "\nSaving flood-affected roads..."
# )


# affected_roads_export = affected_roads.drop(
#     columns=[
#         "flooded_geometry"
#     ],
#     errors="ignore"
# )


# affected_roads_export.to_file(
#     road_gpkg_path,
#     layer="flood_affected_roads",
#     driver="GPKG"
# )


# print(
#     "Flood-affected roads saved."
# )


# print(
#     "\nRoad GeoPackage:"
# )

# print(
#     road_gpkg_path
# )


# # ================================================================
# # 20.19 — SAVE ROAD SUMMARY CSV
# # ================================================================

# road_summary = pd.DataFrame(
#     [
#         {
#             "district":
#                 TEST_DISTRICT,

#             "total_osm_mapped_road_length_km":
#                 round(
#                     total_road_length_km,
#                     3
#                 ),

#             "flood_affected_road_length_km":
#                 round(
#                     flooded_road_length_km,
#                     3
#                 ),

#             "road_affected_percent":
#                 round(
#                     road_affected_percent,
#                     2
#                 ),

#             "total_mapped_road_segments":
#                 len(road_edges),

#             "flood_affected_road_segments":
#                 len(affected_roads)
#         }
#     ]
# )


# road_summary.to_csv(
#     road_summary_path,
#     index=False
# )


# print(
#     "\nRoad summary CSV saved:"
# )

# print(
#     road_summary_path
# )


# # ================================================================
# # 20.20 — CREATE ROAD MAP PREVIEW
# # ================================================================

# print(
#     "\nCreating road map preview..."
# )


# import matplotlib.pyplot as plt


# fig, ax = plt.subplots(
#     figsize=(12, 12)
# )


# # ------------------------------------------------
# # District boundary
# # ------------------------------------------------

# district_metric.boundary.plot(
#     ax=ax,
#     linewidth=1.5
# )


# # ------------------------------------------------
# # All OSM roads
# # ------------------------------------------------

# road_edges.plot(
#     ax=ax,
#     linewidth=0.5,
#     alpha=0.55
# )


# # ------------------------------------------------
# # Flood-affected road portions
# # ------------------------------------------------

# if len(affected_roads) > 0:

#     affected_roads[
#         ["flooded_geometry"]
#     ].set_geometry(
#         "flooded_geometry"
#     ).plot(
#         ax=ax,
#         linewidth=2.0
#     )


# # ------------------------------------------------
# # Title
# # ------------------------------------------------

# ax.set_title(
#     (
#         f"{TEST_DISTRICT} — "
#         "OSM Road Network & Flood-Affected Roads"
#     ),
#     fontsize=16,
#     pad=15
# )


# # ------------------------------------------------
# # Statistics box
# # ------------------------------------------------

# ax.text(
#     0.02,
#     0.02,

#     (
#         f"Total mapped roads: "
#         f"{total_road_length_km:.1f} km\n"

#         f"Flood-affected road portions: "
#         f"{flooded_road_length_km:.1f} km\n"

#         f"Road network affected: "
#         f"{road_affected_percent:.2f}%"
#     ),

#     transform=ax.transAxes,

#     fontsize=10,

#     verticalalignment="bottom",

#     bbox=dict(
#         boxstyle="round",
#         facecolor="white",
#         alpha=0.85
#     )
# )


# ax.set_axis_off()


# plt.tight_layout()


# plt.savefig(
#     road_preview_path,
#     dpi=200,
#     bbox_inches="tight"
# )


# plt.close()


# print(
#     "Road preview saved:"
# )

# print(
#     road_preview_path
# )


# # ================================================================
# # 20.21 — FINAL OUTPUT
# # ================================================================

# print(
#     "\n================================================"
# )

# print(
#     "ROAD ANALYSIS COMPLETE"
# )

# print(
#     "================================================"
# )

# print(
#     f"District: {TEST_DISTRICT}"
# )

# print(
#     f"Total OSM-mapped roads: "
#     f"{total_road_length_km:.2f} km"
# )

# print(
#     f"Flood-affected road portions: "
#     f"{flooded_road_length_km:.2f} km"
# )

# print(
#     f"Road network affected: "
#     f"{road_affected_percent:.2f}%"
# )

# print(
#     f"Flood-affected road segments: "
#     f"{len(affected_roads)}"
# )

# print(
#     "\nGeoPackage:"
# )

# print(
#     road_gpkg_path
# )

# print(
#     "\nSummary CSV:"
# )

# print(
#     road_summary_path
# )

# print(
#     "\nMap preview:"
# )

# print(
#     road_preview_path
# )

# print(
#     "\n================================================"
# )


















# ============================================================
# ASSAM FLOOD INTELLIGENCE
# DISTRICT-LEVEL FLOOD ANALYSIS
#
# BATCH ANALYSIS FOR 11 DISTRICTS
#
# Methodology:
#   Sentinel-1 VV change detection
#   JRC permanent water exclusion
#   ESA WorldCover exposure
#   GPM IMERG rainfall
#   Copernicus DEM
#   Terrain slope
#   OSM buildings
#   OSM roads
#
# Authoritative flood area:
#   10 m GEE pixelArea calculation
#
# Local flood raster:
#   30 m GeoTIFF used for visualization
#   and local exposure/intersection analysis
# ============================================================


# ============================================================
# SECTION 1 — IMPORTS
# ============================================================

import os
import urllib.request
from collections import Counter

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
    DISTRICT_NAMES,

    BATCH_MODE,
    TEST_DISTRICT,

    OUTPUT_DIR,

    S1_COLLECTION,
    S1_SEARCH_START,
    S1_SEARCH_END,

    PRE_START,
    PRE_END,

    FLOOD_START,
    FLOOD_END,

    POST_START,
    POST_END,

    S1_POLARIZATION,
    S1_INSTRUMENT_MODE,

    FLOOD_DIFFERENCE_THRESHOLD,

    JRC_WATER_COLLECTION,
    PERMANENT_WATER_THRESHOLD,

    WORLDCOVER_COLLECTION,
    WORLD_COVER_CROPLAND,
    WORLD_COVER_TREE_COVER,

    DEM_COLLECTION,

    GPM_COLLECTION,

    OSM_BUILDING_TAG,

    RUN_BUILDING_ANALYSIS,
    RUN_ROAD_ANALYSIS,

    DOWNLOAD_FLOOD_RASTER,
    FLOOD_RASTER_SCALE,

    EXPORT_RAINFALL_GRAPH,

)


# ============================================================
# SECTION 2 — EARTH ENGINE INITIALIZATION
# ============================================================

print()
print("=" * 70)
print("ASSAM FLOOD INTELLIGENCE")
print("DISTRICT-LEVEL BATCH ANALYSIS")
print("=" * 70)

print()

ee.Initialize(
    project=EE_PROJECT
)

print(
    "Earth Engine initialized successfully."
)

print(
    "Earth Engine project:",
    EE_PROJECT
)


# ============================================================
# SECTION 3 — OUTPUT DIRECTORIES
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

raster_dir = os.path.join(
    OUTPUT_DIR,
    "raster"
)

graph_dir = os.path.join(
    OUTPUT_DIR,
    "graphs"
)

building_dir = os.path.join(
    OUTPUT_DIR,
    "buildings"
)

road_dir = os.path.join(
    OUTPUT_DIR,
    "roads"
)

visual_dir = os.path.join(
    OUTPUT_DIR,
    "visual_check"
)

os.makedirs(
    raster_dir,
    exist_ok=True
)

os.makedirs(
    graph_dir,
    exist_ok=True
)

os.makedirs(
    building_dir,
    exist_ok=True
)

os.makedirs(
    road_dir,
    exist_ok=True
)

os.makedirs(
    visual_dir,
    exist_ok=True
)


# ============================================================
# SECTION 4 — SELECT DISTRICTS
# ============================================================

if BATCH_MODE:

    districts_to_process = DISTRICT_NAMES.copy()

else:

    districts_to_process = [
        TEST_DISTRICT
    ]


print(
    "Districts selected for analysis:"
)

for district in districts_to_process:

    print(
        "  -",
        district
    )

print()

print(
    "Total districts:",
    len(districts_to_process)
)


# ============================================================
# SECTION 5 — HELPER FUNCTIONS
# ============================================================


def safe_percentage(
    numerator,
    denominator
):
    """
    Calculate percentage safely.
    """

    if denominator is None:

        return None

    if denominator == 0:

        return 0

    return (
        numerator
        /
        denominator
        *
        100
    )


def safe_float(
    value
):
    """
    Convert value to float safely.
    """

    if value is None:

        return None

    try:

        return float(value)

    except:

        return None


def safe_round(
    value,
    digits=3
):
    """
    Round values while preserving None.
    """

    if value is None:

        return None

    return round(
        float(value),
        digits
    )


# ============================================================
# SECTION 6 — SENTINEL-1 COLLECTION
# ============================================================


def build_s1_collection(
    aoi_geometry
):

    s1 = (

        ee.ImageCollection(
            S1_COLLECTION
        )

        .filterBounds(
            aoi_geometry
        )

        .filterDate(
            S1_SEARCH_START,
            S1_SEARCH_END
        )

        .filter(
            ee.Filter.eq(
                "instrumentMode",
                S1_INSTRUMENT_MODE
            )
        )

        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                S1_POLARIZATION
            )
        )

    )

    return s1


# ============================================================
# SECTION 7 — FIND COMMON SENTINEL-1 ORBIT
# ============================================================


def select_common_orbit(
    s1_pre,
    s1_flood
):

    pre_passes = (
        s1_pre
        .aggregate_array(
            "orbitProperties_pass"
        )
        .getInfo()
    )

    pre_orbits = (
        s1_pre
        .aggregate_array(
            "relativeOrbitNumber_start"
        )
        .getInfo()
    )

    flood_passes = (
        s1_flood
        .aggregate_array(
            "orbitProperties_pass"
        )
        .getInfo()
    )

    flood_orbits = (
        s1_flood
        .aggregate_array(
            "relativeOrbitNumber_start"
        )
        .getInfo()
    )

    pre_keys = [

        f"{p}_{int(o)}"

        for p, o
        in zip(
            pre_passes,
            pre_orbits
        )

    ]

    flood_keys = [

        f"{p}_{int(o)}"

        for p, o
        in zip(
            flood_passes,
            flood_orbits
        )

    ]

    pre_counts = Counter(
        pre_keys
    )

    flood_counts = Counter(
        flood_keys
    )

    common_keys = (

        set(pre_counts)
        .intersection(
            flood_counts
        )

    )

    if not common_keys:

        raise RuntimeError(

            "No common Sentinel-1 "
            "orbit/pass combination "
            "exists between the "
            "pre-flood and flood periods."

        )

    orbit_scores = {

        key: min(
            pre_counts[key],
            flood_counts[key]
        )

        for key
        in common_keys

    }

    selected_key = max(
        orbit_scores,
        key=orbit_scores.get
    )

    selected_pass, selected_orbit = (

        selected_key.rsplit(
            "_",
            1
        )

    )

    selected_orbit = int(
        selected_orbit
    )

    return (
        selected_pass,
        selected_orbit,
        pre_counts[selected_key],
        flood_counts[selected_key]
    )


# ============================================================
# SECTION 8 — FLOOD MASK
# ============================================================


def create_flood_mask(
    aoi_geometry
):

    s1 = build_s1_collection(
        aoi_geometry
    )

    s1_pre = (
        s1.filterDate(
            PRE_START,
            PRE_END
        )
    )

    s1_flood = (
        s1.filterDate(
            FLOOD_START,
            FLOOD_END
        )
    )

    s1_post = (
        s1.filterDate(
            POST_START,
            POST_END
        )
    )

    pre_count = (
        s1_pre.size().getInfo()
    )

    flood_count = (
        s1_flood.size().getInfo()
    )

    post_count = (
        s1_post.size().getInfo()
    )

    print()
    print(
        "Sentinel-1 availability:"
    )

    print(
        "  Search window:",
        s1.size().getInfo()
    )

    print(
        "  Pre-flood images:",
        pre_count
    )

    print(
        "  Flood-period images:",
        flood_count
    )

    print(
        "  Post-flood images:",
        post_count
    )

    if pre_count == 0:

        raise RuntimeError(
            "No Sentinel-1 pre-flood images found."
        )

    if flood_count == 0:

        raise RuntimeError(
            "No Sentinel-1 flood-period images found."
        )

    (
        selected_pass,
        selected_orbit,
        selected_pre_count,
        selected_flood_count

    ) = select_common_orbit(
        s1_pre,
        s1_flood
    )

    print()
    print(
        "Selected Sentinel-1 acquisition geometry:"
    )

    print(
        "  Orbit pass:",
        selected_pass
    )

    print(
        "  Relative orbit:",
        selected_orbit
    )

    print(
        "  Pre-flood images:",
        selected_pre_count
    )

    print(
        "  Flood-period images:",
        selected_flood_count
    )

    s1_pre_consistent = (

        s1_pre

        .filter(
            ee.Filter.eq(
                "orbitProperties_pass",
                selected_pass
            )
        )

        .filter(
            ee.Filter.eq(
                "relativeOrbitNumber_start",
                selected_orbit
            )
        )

        .select(
            S1_POLARIZATION
        )

    )

    s1_flood_consistent = (

        s1_flood

        .filter(
            ee.Filter.eq(
                "orbitProperties_pass",
                selected_pass
            )
        )

        .filter(
            ee.Filter.eq(
                "relativeOrbitNumber_start",
                selected_orbit
            )
        )

        .select(
            S1_POLARIZATION
        )

    )

    consistent_pre_count = (
        s1_pre_consistent
        .size()
        .getInfo()
    )

    consistent_flood_count = (
        s1_flood_consistent
        .size()
        .getInfo()
    )

    if consistent_pre_count == 0:

        raise RuntimeError(
            "Consistent pre-flood collection is empty."
        )

    if consistent_flood_count == 0:

        raise RuntimeError(
            "Consistent flood collection is empty."
        )

    pre_vv = (

        s1_pre_consistent

        .median()

        .clip(
            aoi_geometry
        )

    )

    flood_vv = (

        s1_flood_consistent

        .median()

        .clip(
            aoi_geometry
        )

    )

    vv_change = (

        flood_vv
        .subtract(
            pre_vv
        )

    )

    candidate_flood = (

        vv_change
        .lt(
            FLOOD_DIFFERENCE_THRESHOLD
        )

    )

    permanent_water = (

        ee.Image(
            JRC_WATER_COLLECTION
        )

        .select(
            "occurrence"
        )

        .gte(
            PERMANENT_WATER_THRESHOLD
        )

    )

    flood_mask = (

        candidate_flood

        .And(
            permanent_water.Not()
        )

        .selfMask()

        .clip(
            aoi_geometry
        )

    )

    return (
        flood_mask,
        pre_vv,
        flood_vv,
        vv_change
    )


# ============================================================
# SECTION 9 — FLOOD AREA
# ============================================================


def calculate_flood_area(
    flood_mask,
    aoi_geometry
):

    pixel_area = (
        ee.Image.pixelArea()
    )

    flood_area_image = (

        pixel_area
        .updateMask(
            flood_mask
        )

    )

    flood_area_result = (

        flood_area_image

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    flood_area_m2 = (
        flood_area_result
        .get("area")
    )

    flood_area_km2 = ee.Number(

        ee.Algorithms.If(

            flood_area_m2,

            flood_area_m2,

            0

        )

    ).divide(
        1e6
    )

    district_area_result = (

        pixel_area

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    district_area_m2 = (
        district_area_result
        .get("area")
    )

    district_area_km2 = (

        ee.Number(
            district_area_m2
        )

        .divide(
            1e6
        )

    )

    flood_percentage = (

        flood_area_km2

        .divide(
            district_area_km2
        )

        .multiply(
            100
        )

    )

    return (

        safe_float(
            district_area_km2.getInfo()
        ),

        safe_float(
            flood_area_km2.getInfo()
        ),

        safe_float(
            flood_percentage.getInfo()
        )

    )


# ============================================================
# SECTION 10 — WORLDCOVER
# ============================================================


def create_worldcover_masks(
    aoi_geometry
):

    worldcover = (

        ee.ImageCollection(
            WORLDCOVER_COLLECTION
        )

        .first()

        .select(
            "Map"
        )

        .clip(
            aoi_geometry
        )

    )

    cropland_mask = (

        worldcover
        .eq(
            WORLD_COVER_CROPLAND
        )

    )

    forest_mask = (

        worldcover
        .eq(
            WORLD_COVER_TREE_COVER
        )

    )

    return (
        worldcover,
        cropland_mask,
        forest_mask
    )


# ============================================================
# SECTION 11 — LAND COVER EXPOSURE
# ============================================================


def calculate_landcover_exposure(
    flood_mask,
    cropland_mask,
    forest_mask,
    aoi_geometry
):

    pixel_area = (
        ee.Image.pixelArea()
    )


    # --------------------------------------------------------
    # CROPLAND
    # --------------------------------------------------------

    flooded_cropland = (

        flood_mask

        .And(
            cropland_mask
        )

        .selfMask()

    )

    flooded_cropland_area_image = (

        pixel_area

        .updateMask(
            flooded_cropland
        )

    )

    flooded_cropland_result = (

        flooded_cropland_area_image

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    flooded_cropland_m2 = (
        flooded_cropland_result
        .get("area")
    )

    flooded_cropland_km2 = ee.Number(

        ee.Algorithms.If(

            flooded_cropland_m2,

            flooded_cropland_m2,

            0

        )

    ).divide(
        1e6
    )


    cropland_area_image = (

        pixel_area

        .updateMask(
            cropland_mask
        )

    )

    cropland_area_result = (

        cropland_area_image

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    cropland_area_m2 = (
        cropland_area_result
        .get("area")
    )

    cropland_area_km2 = (

        ee.Number(
            cropland_area_m2
        )

        .divide(
            1e6
        )

    )

    cropland_affected_percentage = (

        flooded_cropland_km2

        .divide(
            cropland_area_km2
        )

        .multiply(
            100
        )

    )


    # --------------------------------------------------------
    # FOREST / TREE COVER
    # --------------------------------------------------------

    flooded_forest = (

        flood_mask

        .And(
            forest_mask
        )

        .selfMask()

    )

    flooded_forest_area_image = (

        pixel_area

        .updateMask(
            flooded_forest
        )

    )

    flooded_forest_result = (

        flooded_forest_area_image

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    flooded_forest_m2 = (
        flooded_forest_result
        .get("area")
    )

    flooded_forest_km2 = ee.Number(

        ee.Algorithms.If(

            flooded_forest_m2,

            flooded_forest_m2,

            0

        )

    ).divide(
        1e6
    )


    forest_area_image = (

        pixel_area

        .updateMask(
            forest_mask
        )

    )

    forest_area_result = (

        forest_area_image

        .reduceRegion(

            reducer=ee.Reducer.sum(),

            geometry=aoi_geometry,

            scale=10,

            maxPixels=1e9

        )

    )

    forest_area_m2 = (
        forest_area_result
        .get("area")
    )

    forest_area_km2 = (

        ee.Number(
            forest_area_m2
        )

        .divide(
            1e6
        )

    )

    forest_affected_percentage = (

        flooded_forest_km2

        .divide(
            forest_area_km2
        )

        .multiply(
            100
        )

    )


    return {

        "flooded_cropland":
            flooded_cropland,

        "flooded_forest":
            flooded_forest,

        "total_cropland_km2":
            safe_float(
                cropland_area_km2.getInfo()
            ),

        "flooded_cropland_km2":
            safe_float(
                flooded_cropland_km2.getInfo()
            ),

        "cropland_affected_percent":
            safe_float(
                cropland_affected_percentage.getInfo()
            ),

        "total_forest_km2":
            safe_float(
                forest_area_km2.getInfo()
            ),

        "flooded_forest_km2":
            safe_float(
                flooded_forest_km2.getInfo()
            ),

        "forest_affected_percent":
            safe_float(
                forest_affected_percentage.getInfo()
            )

    }


# ============================================================
# SECTION 12 — RAINFALL
# ============================================================


def calculate_rainfall(
    aoi_geometry
):

    print()
    print(
        "Calculating GPM rainfall..."
    )

    gpm = (

        ee.ImageCollection(
            GPM_COLLECTION
        )

        .filterBounds(
            aoi_geometry
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

        daily_images = (

            gpm_rainfall

            .filterDate(
                day_start,
                day_end
            )

        )

        daily_rainfall = (

            daily_images

            .sum()

            .rename(
                "daily_rainfall"
            )

            .clip(
                aoi_geometry
            )

        )

        district_mean = (

            daily_rainfall

            .reduceRegion(

                reducer=ee.Reducer.mean(),

                geometry=aoi_geometry,

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
                    district_mean

            }

        )


    daily_rainfall_fc = ee.FeatureCollection(

        day_offsets.map(
            calculate_daily_rainfall
        )

    )


    daily_features = (

        daily_rainfall_fc

        .getInfo()

        ["features"]

    )


    daily_records = [

        feature["properties"]

        for feature
        in daily_features

    ]


    daily_records = [

        record

        for record
        in daily_records

        if record.get(
            "rainfall_mm"
        ) is not None

    ]


    if len(daily_records) > 0:

        flood_period_rainfall = sum(

            record["rainfall_mm"]

            for record
            in daily_records

        )

        maximum_daily_rainfall = max(

            record["rainfall_mm"]

            for record
            in daily_records

        )

    else:

        flood_period_rainfall = None

        maximum_daily_rainfall = None


    return (

        daily_records,

        flood_period_rainfall,

        maximum_daily_rainfall

    )


# ============================================================
# SECTION 13 — SAVE RAINFALL OUTPUTS
# ============================================================


def save_rainfall_outputs(
    district,
    daily_records
):

    if len(daily_records) == 0:

        return None


    rainfall_df = pd.DataFrame(
        daily_records
    )

    rainfall_df["date"] = pd.to_datetime(
        rainfall_df["date"]
    )

    rainfall_df = rainfall_df.sort_values(
        "date"
    )


    csv_path = os.path.join(

        OUTPUT_DIR,

        f"{district}_daily_rainfall.csv"

    )

    rainfall_df.to_csv(

        csv_path,

        index=False

    )


    graph_path = None


    if EXPORT_RAINFALL_GRAPH:

        graph_path = os.path.join(

            graph_dir,

            f"{district}_daily_rainfall.png"

        )


        plt.figure(
            figsize=(12, 5)
        )

        plt.plot(

            rainfall_df["date"],

            rainfall_df["rainfall_mm"],

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

            f"{district} — "
            "Daily Rainfall During Flood Period"

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

            graph_path,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()


    return (
        csv_path,
        graph_path
    )


# ============================================================
# SECTION 14 — DEM
# ============================================================


def calculate_dem_and_slope(
    aoi_geometry
):

    print()
    print(
        "Calculating elevation and slope..."
    )


    dem_collection = (

        ee.ImageCollection(
            DEM_COLLECTION
        )

        .filterBounds(
            aoi_geometry
        )

    )


    if dem_collection.size().getInfo() == 0:

        raise RuntimeError(
            "No Copernicus DEM found for district."
        )


    native_projection = (

        dem_collection

        .first()

        .projection()

    )


    dem = (

        dem_collection

        .mosaic()

        .setDefaultProjection(
            native_projection
        )

        .select(
            "DEM"
        )

        .clip(
            aoi_geometry
        )

    )


    elevation_stats = (

        dem

        .reduceRegion(

            reducer=

                ee.Reducer.mean()

                .combine(

                    reducer2=ee.Reducer.min(),

                    sharedInputs=True

                )

                .combine(

                    reducer2=ee.Reducer.max(),

                    sharedInputs=True

                ),

            geometry=aoi_geometry,

            scale=30,

            maxPixels=1e9,

            bestEffort=True

        )

        .getInfo()

    )


    mean_elevation = (
        elevation_stats.get(
            "DEM_mean"
        )
    )

    min_elevation = (
        elevation_stats.get(
            "DEM_min"
        )
    )

    max_elevation = (
        elevation_stats.get(
            "DEM_max"
        )
    )


    slope = (

        ee.Terrain

        .slope(
            dem
        )

        .rename(
            "slope"
        )

        .updateMask(
            dem.mask()
        )

        .clip(
            aoi_geometry
        )

    )


    slope_stats = (

        slope

        .reduceRegion(

            reducer=

                ee.Reducer.mean()

                .combine(

                    reducer2=ee.Reducer.min(),

                    sharedInputs=True

                )

                .combine(

                    reducer2=ee.Reducer.max(),

                    sharedInputs=True

                ),

            geometry=aoi_geometry,

            scale=30,

            maxPixels=1e9,

            bestEffort=True

        )

        .getInfo()

    )


    mean_slope = (
        slope_stats.get(
            "slope_mean"
        )
    )

    min_slope = (
        slope_stats.get(
            "slope_min"
        )
    )

    max_slope = (
        slope_stats.get(
            "slope_max"
        )
    )


    if mean_slope is None:

        raise RuntimeError(
            "Slope calculation returned None."
        )


    return {

        "dem":
            dem,

        "slope":
            slope,

        "mean_elevation_m":
            safe_float(
                mean_elevation
            ),

        "minimum_elevation_m":
            safe_float(
                min_elevation
            ),

        "maximum_elevation_m":
            safe_float(
                max_elevation
            ),

        "mean_slope_degrees":
            safe_float(
                mean_slope
            ),

        "minimum_slope_degrees":
            safe_float(
                min_slope
            ),

        "maximum_slope_degrees":
            safe_float(
                max_slope
            )

    }


# ============================================================
# SECTION 15 — CREATE FLOOD EXPOSURE RASTER
# ============================================================


def create_flood_raster(
    district,
    flood_mask,
    flooded_cropland,
    flooded_forest,
    aoi_geometry
):

    output_filename = (

        f"{district.replace(' ', '_')}"
        "_flood_exposure.tif"

    )

    output_path = os.path.join(

        raster_dir,

        output_filename

    )


    if (

        os.path.exists(output_path)

        and

        os.path.getsize(output_path) > 0

    ):

        print()
        print(
            "Flood raster already exists:"
        )

        print(
            output_path
        )

        return output_path


    combined_flood_map = (

        ee.Image(0)

        .where(
            flood_mask,
            1
        )

        .where(
            flooded_cropland,
            2
        )

        .where(
            flooded_forest,
            3
        )

        .selfMask()

        .clip(
            aoi_geometry
        )

    )


    region = (
        aoi_geometry
        .getInfo()
    )


    region = region[
        "coordinates"
    ]

    # region = aoi_geometry.bounds().getInfo()
    # print()
    print(
        "Preparing flood raster download..."
    )

    print(
        "District:",
        district
    )

    print(
        "Resolution:",
        FLOOD_RASTER_SCALE,
        "m"
    )


    download_url = (

        combined_flood_map

        .getDownloadURL({

            "scale":
                FLOOD_RASTER_SCALE,

            "region":
                region,

            "format":
                "GEO_TIFF"

        })

    )


    print(
        "Downloading flood raster..."
    )


    urllib.request.urlretrieve(

        download_url,

        output_path

    )


    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "Flood raster download failed."
        )


    size_mb = (

        os.path.getsize(
            output_path
        )

        /

        (1024 * 1024)

    )


    print(
        "Flood raster saved:",
        output_path
    )

    print(
        "File size:",
        round(size_mb, 2),
        "MB"
    )


    return output_path


# ============================================================
# SECTION 16 — BUILDING EXPOSURE
# ============================================================


def calculate_building_exposure(
    district,
    flood_raster_path,
    aoi_geometry
):

    print()
    print(
        "================================================"
    )

    print(
        "BUILDING EXPOSURE"
    )

    print(
        "District:",
        district
    )

    print(
        "================================================"
    )


    if not os.path.exists(
        flood_raster_path
    ):

        print(
            "Flood raster unavailable."
        )

        return {

            "total_osm_mapped_buildings":
                None,

            "flood_affected_buildings":
                None,

            "buildings_affected_percent":
                None

        }


    # --------------------------------------------------------
    # LOAD FLOOD RASTER
    # --------------------------------------------------------

    with rasterio.open(
        flood_raster_path
    ) as src:

        flood_array = src.read(1)

        flood_transform = src.transform

        flood_crs = src.crs


    flood_binary = (
        flood_array > 0
    )


    flood_shapes = shapes(

        flood_array,

        mask=flood_binary,

        transform=flood_transform

    )


    flood_polygons = []


    for geom, value in flood_shapes:

        if value > 0:

            flood_polygons.append(
                shape(geom)
            )


    if len(flood_polygons) == 0:

        return {

            "total_osm_mapped_buildings":
                0,

            "flood_affected_buildings":
                0,

            "buildings_affected_percent":
                0

        }


    flood_polygon = unary_union(
        flood_polygons
    )


    flood_gdf = gpd.GeoDataFrame(

        {
            "flooded": [1]
        },

        geometry=[
            flood_polygon
        ],

        crs=flood_crs

    )


    flood_gdf_wgs84 = (
        flood_gdf
        .to_crs(
            "EPSG:4326"
        )
    )


    flood_polygon_wgs84 = (

        flood_gdf_wgs84

        .geometry

        .iloc[0]

    )


    # --------------------------------------------------------
    # DISTRICT GEOMETRY
    # --------------------------------------------------------

    district_geometry = shape(

        aoi_geometry.getInfo()

    )


    # --------------------------------------------------------
    # OSM BUILDINGS
    # --------------------------------------------------------

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

    except Exception as e:

        print(
            "OSM building download failed:"
        )

        print(e)

        return {

            "total_osm_mapped_buildings":
                None,

            "flood_affected_buildings":
                None,

            "buildings_affected_percent":
                None

        }


    # --------------------------------------------------------
    # KEEP POLYGON BUILDINGS
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

        buildings = buildings.to_crs(
            "EPSG:4326"
        )


    total_buildings = len(
        buildings
    )


    print(
        "Total OSM-mapped buildings:",
        total_buildings
    )


    # --------------------------------------------------------
    # FLOOD INTERSECTION
    #
    # NO BUFFER
    # --------------------------------------------------------

    flood_intersection_gdf = (

        gpd.GeoDataFrame(

            {
                "flood": [1]
            },

            geometry=[
                flood_polygon_wgs84
            ],

            crs="EPSG:4326"

        )

    )


    affected_buildings = gpd.sjoin(

        buildings,

        flood_intersection_gdf,

        how="inner",

        predicate="intersects"

    )


    affected_buildings = (

        affected_buildings[

            ~

            affected_buildings.index
            .duplicated(
                keep="first"
            )

        ]

        .copy()

    )


    affected_count = len(
        affected_buildings
    )


    affected_percentage = safe_percentage(

        affected_count,

        total_buildings

    )


    print(
        "Flood-affected buildings:",
        affected_count
    )

    print(
        "Buildings affected:",
        f"{affected_percentage:.2f}%"
        if affected_percentage is not None
        else "No data"
    )


    # --------------------------------------------------------
    # SAVE AFFECTED BUILDINGS
    # --------------------------------------------------------

    affected_path = os.path.join(

        building_dir,

        f"{district.replace(' ', '_')}"
        "_affected_buildings.gpkg"

    )


    useful_columns = [

        column

        for column

        in [
            "osmid",
            "building",
            "geometry"
        ]

        if column
        in affected_buildings.columns

    ]


    affected_export = (

        affected_buildings[
            useful_columns
        ]

        .copy()

    )


    if "index_right" in (
        affected_export.columns
    ):

        affected_export = (

            affected_export

            .drop(
                columns=[
                    "index_right"
                ]
            )

        )


    if len(affected_export) > 0:

        affected_export.to_file(

            affected_path,

            driver="GPKG"

        )


    # --------------------------------------------------------
    # BUILDING SUMMARY
    # --------------------------------------------------------

    building_summary_path = os.path.join(

        OUTPUT_DIR,

        f"{district.replace(' ', '_')}"
        "_building_summary.csv"

    )


    building_summary = pd.DataFrame(

        [

            {

                "district":
                    district,

                "total_osm_mapped_buildings":
                    total_buildings,

                "flood_affected_buildings":
                    affected_count,

                "affected_buildings_percent":
                    round(
                        affected_percentage,
                        2
                    )
                    if affected_percentage
                    is not None
                    else None

            }

        ]

    )


    building_summary.to_csv(

        building_summary_path,

        index=False

    )


    return {

        "total_osm_mapped_buildings":
            total_buildings,

        "flood_affected_buildings":
            affected_count,

        "buildings_affected_percent":
            affected_percentage

    }



# # ============================================================
# # SECTION 16 — BUILDING EXPOSURE
# # ============================================================


# def calculate_building_exposure(
#     district,
#     flood_raster_path,
#     aoi_geometry
# ):

#     print()
#     print(
#         "================================================"
#     )

#     print(
#         "BUILDING EXPOSURE"
#     )

#     print(
#         "District:",
#         district
#     )

#     print(
#         "================================================"
#     )


#     if not os.path.exists(
#         flood_raster_path
#     ):

#         print(
#             "Flood raster unavailable."
#         )

#         return {

#             "total_osm_mapped_buildings":
#                 None,

#             "flood_affected_buildings":
#                 None,

#             "buildings_affected_percent":
#                 None

#         }


#     # --------------------------------------------------------
#     # LOAD FLOOD RASTER
#     # --------------------------------------------------------

#     print(
#         "Loading flood raster..."
#     )


#     with rasterio.open(
#         flood_raster_path
#     ) as src:

#         flood_array = src.read(1)

#         flood_transform = src.transform

#         flood_crs = src.crs


#     flood_binary = (
#         flood_array > 0
#     )


#     # --------------------------------------------------------
#     # CONVERT FLOOD RASTER TO POLYGONS
#     # --------------------------------------------------------

#     print(
#         "Converting flood raster to polygons..."
#     )


#     flood_shapes = shapes(

#         flood_array,

#         mask=flood_binary,

#         transform=flood_transform

#     )


#     flood_polygons = []


#     for geom, value in flood_shapes:

#         if value > 0:

#             flood_polygons.append(
#                 shape(geom)
#             )


#     if len(flood_polygons) == 0:

#         print(
#             "No flooded polygons found."
#         )

#         return {

#             "total_osm_mapped_buildings":
#                 0,

#             "flood_affected_buildings":
#                 0,

#             "buildings_affected_percent":
#                 0

#         }


#     print(
#         "Flood polygons generated:",
#         len(flood_polygons)
#     )


#     # --------------------------------------------------------
#     # COMBINE FLOOD POLYGONS
#     # --------------------------------------------------------

#     print(
#         "Combining flood polygons..."
#     )


#     flood_polygon = unary_union(
#         flood_polygons
#     )


#     # --------------------------------------------------------
#     # SIMPLIFY FLOOD GEOMETRY
#     #
#     # Used only for building-intersection efficiency.
#     # Original flood raster remains unchanged.
#     # --------------------------------------------------------

#     print(
#         "Simplifying flood geometry..."
#     )


#     flood_polygon_simplified = (

#         flood_polygon

#         .simplify(

#             tolerance=5,

#             preserve_topology=True

#         )

#     )


#     # --------------------------------------------------------
#     # DISTRICT GEOMETRY
#     # --------------------------------------------------------

#     district_geometry = shape(

#         aoi_geometry.getInfo()

#     )


#     # --------------------------------------------------------
#     # OSM BUILDINGS
#     # --------------------------------------------------------

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

#     except Exception as e:

#         print(
#             "OSM building download failed:"
#         )

#         print(e)

#         return {

#             "total_osm_mapped_buildings":
#                 None,

#             "flood_affected_buildings":
#                 None,

#             "buildings_affected_percent":
#                 None

#         }


#     # --------------------------------------------------------
#     # KEEP POLYGON BUILDINGS
#     # --------------------------------------------------------

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

#         buildings = buildings.to_crs(

#             "EPSG:4326"

#         )


#     total_buildings = len(

#         buildings

#     )


#     print(

#         "Total OSM-mapped buildings:",

#         total_buildings

#     )


#     if total_buildings == 0:

#         print(

#             "No polygon buildings found."

#         )

#         return {

#             "total_osm_mapped_buildings":
#                 0,

#             "flood_affected_buildings":
#                 0,

#             "buildings_affected_percent":
#                 0

#         }


#     # --------------------------------------------------------
#     # PROJECT BUILDINGS TO FLOOD RASTER CRS
#     #
#     # Spatial intersection is performed in the raster CRS.
#     # --------------------------------------------------------

#     print(

#         "Projecting buildings to flood raster CRS..."

#     )


#     buildings_projected = (

#         buildings

#         .to_crs(

#             flood_crs

#         )

#     )


#     # --------------------------------------------------------
#     # FLOOD INTERSECTION
#     #
#     # NO BUFFER
#     # --------------------------------------------------------

#     flood_intersection_gdf = (

#         gpd.GeoDataFrame(

#             {

#                 "flood": [1]

#             },

#             geometry=[

#                 flood_polygon_simplified

#             ],

#             crs=flood_crs

#         )

#     )


#     # --------------------------------------------------------
#     # PRELIMINARY BOUNDING BOX FILTER
#     # --------------------------------------------------------

#     print(

#         "Filtering buildings using flood extent..."

#     )


#     minx, miny, maxx, maxy = (

#         flood_polygon_simplified.bounds

#     )


#     candidate_buildings = (

#         buildings_projected.cx[

#             minx:maxx,

#             miny:maxy

#         ]

#         .copy()

#     )


#     print(

#         "Candidate buildings:",

#         len(candidate_buildings)

#     )


#     if len(candidate_buildings) == 0:

#         print(

#             "No buildings found within flood bounding box."

#         )

#         affected_buildings = (

#             candidate_buildings

#         )

#     else:

#         # ----------------------------------------------------
#         # FINAL SPATIAL INTERSECTION
#         # ----------------------------------------------------

#         print(

#             "Running final building intersection..."

#         )


#         affected_buildings = gpd.sjoin(

#             candidate_buildings,

#             flood_intersection_gdf,

#             how="inner",

#             predicate="intersects"

#         )


#         # ----------------------------------------------------
#         # REMOVE DUPLICATE BUILDING RECORDS
#         # ----------------------------------------------------

#         affected_buildings = (

#             affected_buildings[

#                 ~

#                 affected_buildings.index

#                 .duplicated(

#                     keep="first"

#                 )

#             ]

#             .copy()

#         )


#     # --------------------------------------------------------
#     # BUILDING EXPOSURE SUMMARY
#     # --------------------------------------------------------

#     affected_count = len(

#         affected_buildings

#     )


#     affected_percentage = safe_percentage(

#         affected_count,

#         total_buildings

#     )


#     print(

#         "Flood-affected buildings:",

#         affected_count

#     )


#     print(

#         "Buildings affected:",

#         f"{affected_percentage:.2f}%"

#         if affected_percentage is not None

#         else "No data"

#     )


#     # --------------------------------------------------------
#     # SAVE AFFECTED BUILDINGS
#     # --------------------------------------------------------

#     affected_path = os.path.join(

#         building_dir,

#         f"{district.replace(' ', '_')}"

#         "_affected_buildings.gpkg"

#     )


#     useful_columns = [

#         column

#         for column

#         in [

#             "osmid",

#             "building",

#             "geometry"

#         ]

#         if column

#         in affected_buildings.columns

#     ]


#     affected_export = (

#         affected_buildings[

#             useful_columns

#         ]

#         .copy()

#     )


#     if "index_right" in (

#         affected_export.columns

#     ):

#         affected_export = (

#             affected_export

#             .drop(

#                 columns=[

#                     "index_right"

#                 ]

#             )

#         )


#     # --------------------------------------------------------
#     # CONVERT OUTPUT TO WGS84
#     # --------------------------------------------------------

#     if len(affected_export) > 0:

#         affected_export = (

#             affected_export

#             .set_crs(

#                 flood_crs,

#                 allow_override=True

#             )

#             .to_crs(

#                 "EPSG:4326"

#             )

#         )


#         print(

#             "Saving affected buildings..."

#         )


#         affected_export.to_file(

#             affected_path,

#             driver="GPKG"

#         )

#         print(

#             "Affected buildings saved:",

#             affected_path

#         )

#     else:

#         print(

#             "No affected buildings to export."

#         )


#     # --------------------------------------------------------
#     # BUILDING SUMMARY CSV
#     # --------------------------------------------------------

#     building_summary_path = os.path.join(

#         OUTPUT_DIR,

#         f"{district.replace(' ', '_')}"

#         "_building_summary.csv"

#     )


#     building_summary = pd.DataFrame(

#         [

#             {

#                 "district":

#                     district,

#                 "total_osm_mapped_buildings":

#                     total_buildings,

#                 "flood_affected_buildings":

#                     affected_count,

#                 "affected_buildings_percent":

#                     round(

#                         affected_percentage,

#                         2

#                     )

#                     if affected_percentage

#                     is not None

#                     else None

#             }

#         ]

#     )


#     building_summary.to_csv(

#         building_summary_path,

#         index=False

#     )


#     print(

#         "Building summary saved:",

#         building_summary_path

#     )


#     # --------------------------------------------------------
#     # RETURN BUILDING RESULTS
#     # --------------------------------------------------------

#     return {

#         "total_osm_mapped_buildings":

#             total_buildings,

#         "flood_affected_buildings":

#             affected_count,

#         "buildings_affected_percent":

#             affected_percentage

#     }
# ============================================================
# SECTION 17 — ROAD NETWORK EXPOSURE
# ============================================================


def calculate_road_exposure(
    district,
    flood_raster_path,
    aoi_geometry
):

    print()
    print(
        "================================================"
    )

    print(
        "ROAD NETWORK EXPOSURE"
    )

    print(
        "District:",
        district
    )

    print(
        "================================================"
    )


    if not os.path.exists(
        flood_raster_path
    ):

        print(
            "Flood raster unavailable."
        )

        return {

            "total_osm_mapped_road_length_km":
                None,

            "flood_affected_road_length_km":
                None,

            "road_affected_percent":
                None,

            "total_mapped_road_segments":
                None,

            "flood_affected_road_segments":
                None

        }


    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    district_geometry = shape(

        aoi_geometry.getInfo()

    )


    district_gdf = gpd.GeoDataFrame(

        {
            "district": [district]
        },

        geometry=[
            district_geometry
        ],

        crs="EPSG:4326"

    )


    # --------------------------------------------------------
    # OSM ROAD NETWORK
    # --------------------------------------------------------

    print(
        "Downloading OSM road network..."
    )

    print(
        "This may take a little while..."
    )


    try:

        road_graph = (

            ox.graph_from_polygon(

                district_geometry,

                network_type="drive",

                simplify=True

            )

        )

    except Exception as e:

        print(
            "OSM road network download failed:"
        )

        print(e)

        return {

            "total_osm_mapped_road_length_km":
                None,

            "flood_affected_road_length_km":
                None,

            "road_affected_percent":
                None,

            "total_mapped_road_segments":
                None,

            "flood_affected_road_segments":
                None

        }


    road_nodes, road_edges = (

        ox.graph_to_gdfs(

            road_graph,

            nodes=True,

            edges=True

        )

    )


    road_edges = (
        road_edges
        .reset_index()
    )


    road_edges = (

        road_edges[
            road_edges.geometry.notnull()
        ]

        .copy()

    )


    road_edges = (

        road_edges

        .drop_duplicates(
            subset="geometry"
        )

    )


    print(
        "Mapped OSM road segments:",
        len(road_edges)
    )


    # --------------------------------------------------------
    # LOCAL METRIC CRS
    # --------------------------------------------------------

    metric_crs = (
        district_gdf
        .estimate_utm_crs()
    )


    road_edges = (
        road_edges
        .to_crs(
            metric_crs
        )
    )


    district_metric = (
        district_gdf
        .to_crs(
            metric_crs
        )
    )


    # --------------------------------------------------------
    # CLIP ROADS TO DISTRICT
    # --------------------------------------------------------

    road_edges = gpd.clip(

        road_edges,

        district_metric

    )


    road_edges = (

        road_edges[
            road_edges.geometry.notnull()
        ]

        .copy()

    )


    road_edges = (

        road_edges[
            ~road_edges.geometry.is_empty
        ]

        .copy()

    )


    # --------------------------------------------------------
    # TOTAL ROAD LENGTH
    # --------------------------------------------------------

    road_edges["length_m"] = (

        road_edges
        .geometry
        .length

    )


    road_edges["length_km"] = (

        road_edges["length_m"]
        /
        1000

    )


    total_road_length_km = (

        road_edges[
            "length_km"
        ]

        .sum()

    )


    print(
        "Total OSM-mapped road length:",
        round(
            total_road_length_km,
            3
        ),
        "km"
    )


    # --------------------------------------------------------
    # READ FLOOD RASTER
    # --------------------------------------------------------

    with rasterio.open(
        flood_raster_path
    ) as src:

        flood_array = src.read(1)

        raster_transform = src.transform

        raster_crs = src.crs


    flood_mask = (
        flood_array >= 1
    )


    flood_pixel_count = int(
        flood_mask.sum()
    )


    if flood_pixel_count == 0:

        print(
            "No flooded pixels found."
        )

        return {

            "total_osm_mapped_road_length_km":
                total_road_length_km,

            "flood_affected_road_length_km":
                0,

            "road_affected_percent":
                0,

            "total_mapped_road_segments":
                len(road_edges),

            "flood_affected_road_segments":
                0

        }


    # --------------------------------------------------------
    # VECTORIZE FLOOD
    # --------------------------------------------------------

    flood_shapes = shapes(

        flood_mask.astype(
            "uint8"
        ),

        mask=flood_mask,

        transform=raster_transform

    )


    flood_polygons = []


    for geom, value in flood_shapes:

        if value == 1:

            flood_polygons.append(
                shape(geom)
            )


    if len(flood_polygons) == 0:

        raise RuntimeError(
            "Flood raster could not be converted "
            "to polygons."
        )


    flood_union = unary_union(
        flood_polygons
    )


    flood_gdf = gpd.GeoDataFrame(

        {
            "flooded": [1]
        },

        geometry=[
            flood_union
        ],

        crs=raster_crs

    )


    flood_gdf = (
        flood_gdf
        .to_crs(
            metric_crs
        )
    )


    flood_geometry = (

        flood_gdf

        .geometry

        .iloc[0]

    )


    # --------------------------------------------------------
    # INTERSECTION
    # --------------------------------------------------------

    road_edges[
        "flooded_geometry"
    ] = (

        road_edges.geometry

        .intersection(
            flood_geometry
        )

    )


    road_edges[
        "flooded_length_m"
    ] = (

        road_edges[
            "flooded_geometry"
        ]

        .length

    )


    road_edges[
        "flooded_length_km"
    ] = (

        road_edges[
            "flooded_length_m"
        ]

        /
        1000

    )


    road_edges[
        "flood_affected"
    ] = (

        road_edges[
            "flooded_length_m"
        ]

        >
        0

    )


    affected_roads = (

        road_edges[
            road_edges[
                "flood_affected"
            ]
        ]

        .copy()

    )


    flooded_road_length_km = (

        affected_roads[
            "flooded_length_km"
        ]

        .sum()

    )


    road_affected_percent = safe_percentage(

        flooded_road_length_km,

        total_road_length_km

    )


    # --------------------------------------------------------
    # ROAD SUMMARY
    # --------------------------------------------------------

    print()

    print(
        "Total mapped roads:",
        round(
            total_road_length_km,
            3
        ),
        "km"
    )

    print(
        "Flood-affected road portions:",
        round(
            flooded_road_length_km,
            3
        ),
        "km"
    )

    print(
        "Road network affected:",
        f"{road_affected_percent:.2f}%"
        if road_affected_percent is not None
        else "No data"
    )

    print(
        "Flood-affected road segments:",
        len(affected_roads)
    )


    # --------------------------------------------------------
    # SAVE ROAD GEOPACKAGE
    # --------------------------------------------------------

    road_gpkg_path = os.path.join(

        road_dir,

        f"{district.replace(' ', '_')}"
        "_roads.gpkg"

    )


    roads_for_export = (

        road_edges

        .drop(

            columns=[
                "flooded_geometry"
            ],

            errors="ignore"

        )

    )


    roads_for_export.to_file(

        road_gpkg_path,

        layer="all_roads",

        driver="GPKG"

    )


    affected_roads_export = (

        affected_roads

        .drop(

            columns=[
                "flooded_geometry"
            ],

            errors="ignore"

        )

    )


    if len(
        affected_roads_export
    ) > 0:

        affected_roads_export.to_file(

            road_gpkg_path,

            layer="flood_affected_roads",

            driver="GPKG"

        )


    # --------------------------------------------------------
    # ROAD CSV
    # --------------------------------------------------------

    road_summary_path = os.path.join(

        OUTPUT_DIR,

        f"{district.replace(' ', '_')}"
        "_road_summary.csv"

    )


    road_summary = pd.DataFrame(

        [

            {

                "district":
                    district,

                "total_osm_mapped_road_length_km":
                    round(
                        total_road_length_km,
                        3
                    ),

                "flood_affected_road_length_km":
                    round(
                        flooded_road_length_km,
                        3
                    ),

                "road_affected_percent":
                    round(
                        road_affected_percent,
                        2
                    )
                    if road_affected_percent
                    is not None
                    else None,

                "total_mapped_road_segments":
                    len(
                        road_edges
                    ),

                "flood_affected_road_segments":
                    len(
                        affected_roads
                    )

            }

        ]

    )


    road_summary.to_csv(

        road_summary_path,

        index=False

    )


    # --------------------------------------------------------
    # ROAD PREVIEW
    # --------------------------------------------------------

    road_preview_path = os.path.join(

        road_dir,

        f"{district.replace(' ', '_')}"
        "_road_flood_preview.png"

    )


    fig, ax = plt.subplots(

        figsize=(12, 12)

    )


    district_metric.boundary.plot(

        ax=ax,

        linewidth=1.5

    )


    road_edges.plot(

        ax=ax,

        linewidth=0.5,

        alpha=0.55

    )


    if len(
        affected_roads
    ) > 0:

        affected_roads[

            [
                "flooded_geometry"
            ]

        ].set_geometry(

            "flooded_geometry"

        ).plot(

            ax=ax,

            linewidth=2.0

        )


    ax.set_title(

        f"{district} — "
        "OSM Road Network & Flood-Affected Roads",

        fontsize=16,

        pad=15

    )


    ax.text(

        0.02,

        0.02,

        (

            f"Total mapped roads: "
            f"{total_road_length_km:.1f} km\n"

            f"Flood-affected road portions: "
            f"{flooded_road_length_km:.1f} km\n"

            f"Road network affected: "
            f"{road_affected_percent:.2f}%"

        ),

        transform=ax.transAxes,

        fontsize=10,

        verticalalignment="bottom",

        bbox=dict(

            boxstyle="round",

            facecolor="white",

            alpha=0.85

        )

    )


    ax.set_axis_off()

    plt.tight_layout()


    plt.savefig(

        road_preview_path,

        dpi=200,

        bbox_inches="tight"

    )


    plt.close()


    return {

        "total_osm_mapped_road_length_km":
            total_road_length_km,

        "flood_affected_road_length_km":
            flooded_road_length_km,

        "road_affected_percent":
            road_affected_percent,

        "total_mapped_road_segments":
            len(road_edges),

        "flood_affected_road_segments":
            len(affected_roads)

    }


# ============================================================
# SECTION 18 — PROCESS ONE DISTRICT
# ============================================================


def analyze_district(
    district
):

    print()
    print()
    print("=" * 75)
    print(
        f"STARTING DISTRICT: {district.upper()}"
    )
    print("=" * 75)


    # ========================================================
    # 18.1 — LOAD AOI
    # ========================================================

    if district not in DISTRICT_ASSETS:

        raise KeyError(

            f"No Earth Engine asset configured "
            f"for district: {district}"

        )


    aoi = ee.FeatureCollection(

        DISTRICT_ASSETS[
            district
        ]

    )


    aoi_geometry = (
        aoi.geometry()
    )


    aoi_feature_count = (
        aoi.size().getInfo()
    )


    print()

    print(
        "AOI features:",
        aoi_feature_count
    )


    # ========================================================
    # 18.2 — FLOOD MASK
    # ========================================================

    print()
    print(
        "SECTION — FLOOD DETECTION"
    )


    (
        flood_mask,
        pre_vv,
        flood_vv,
        vv_change

    ) = create_flood_mask(
        aoi_geometry
    )


    # ========================================================
    # 18.3 — FLOODED AREA
    # ========================================================

    print()
    print(
        "SECTION — FLOODED AREA"
    )


    (
        district_area_km2,
        flooded_area_km2,
        flooded_area_percent

    ) = calculate_flood_area(

        flood_mask,

        aoi_geometry

    )


    print()

    print(
        "District:",
        district
    )

    print(
        "District area:",
        round(
            district_area_km2,
            3
        ),
        "km²"
    )

    print(
        "Flooded area:",
        round(
            flooded_area_km2,
            3
        ),
        "km²"
    )

    print(
        "Flooded area:",
        round(
            flooded_area_percent,
            3
        ),
        "%"
    )


    # ========================================================
    # 18.4 — WORLDCOVER
    # ========================================================

    (
        worldcover,
        cropland_mask,
        forest_mask

    ) = create_worldcover_masks(

        aoi_geometry

    )


    # ========================================================
    # 18.5 — LAND COVER EXPOSURE
    # ========================================================

    landcover = (

        calculate_landcover_exposure(

            flood_mask,

            cropland_mask,

            forest_mask,

            aoi_geometry

        )

    )


    print()

    print(
        "Total cropland:",
        round(
            landcover[
                "total_cropland_km2"
            ],
            3
        ),
        "km²"
    )

    print(
        "Flood-affected cropland:",
        round(
            landcover[
                "flooded_cropland_km2"
            ],
            3
        ),
        "km²"
    )

    print(
        "Cropland affected:",
        round(
            landcover[
                "cropland_affected_percent"
            ],
            3
        ),
        "%"
    )


    print()

    print(
        "Total forest/tree cover:",
        round(
            landcover[
                "total_forest_km2"
            ],
            3
        ),
        "km²"
    )

    print(
        "Flood-affected forest:",
        round(
            landcover[
                "flooded_forest_km2"
            ],
            3
        ),
        "km²"
    )

    print(
        "Forest affected:",
        round(
            landcover[
                "forest_affected_percent"
            ],
            3
        ),
        "%"
    )


    # ========================================================
    # 18.6 — RAINFALL
    # ========================================================

    (
        daily_records,

        flood_period_rainfall,

        maximum_daily_rainfall

    ) = calculate_rainfall(

        aoi_geometry

    )


    rainfall_outputs = (

        save_rainfall_outputs(

            district,

            daily_records

        )

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


    # ========================================================
    # 18.7 — DEM AND SLOPE
    # ========================================================

    terrain = (

        calculate_dem_and_slope(

            aoi_geometry

        )

    )


    print()

    print(
        "Mean elevation:",
        round(
            terrain[
                "mean_elevation_m"
            ],
            3
        ),
        "m"
    )

    print(
        "Minimum elevation:",
        round(
            terrain[
                "minimum_elevation_m"
            ],
            3
        ),
        "m"
    )

    print(
        "Maximum elevation:",
        round(
            terrain[
                "maximum_elevation_m"
            ],
            3
        ),
        "m"
    )

    print(
        "Mean slope:",
        round(
            terrain[
                "mean_slope_degrees"
            ],
            3
        ),
        "°"
    )

    print(
        "Minimum slope:",
        round(
            terrain[
                "minimum_slope_degrees"
            ],
            3
        ),
        "°"
    )

    print(
        "Maximum slope:",
        round(
            terrain[
                "maximum_slope_degrees"
            ],
            3
        ),
        "°"
    )


    # ========================================================
    # 18.8 — FLOOD RASTER
    # ========================================================

    flood_raster_path = None


    if DOWNLOAD_FLOOD_RASTER:

        flood_raster_path = (

            create_flood_raster(

                district,

                flood_mask,

                landcover[
                    "flooded_cropland"
                ],

                landcover[
                    "flooded_forest"
                ],

                aoi_geometry

            )

        )


    # ========================================================
    # 18.9 — BUILDINGS
    # ========================================================

    if RUN_BUILDING_ANALYSIS:

        building_results = (

            calculate_building_exposure(

                district,

                flood_raster_path,

                aoi_geometry

            )

        )

    else:

        building_results = {

            "total_osm_mapped_buildings":
                None,

            "flood_affected_buildings":
                None,

            "buildings_affected_percent":
                None

        }


    # ========================================================
    # 18.10 — ROADS
    # ========================================================

    if RUN_ROAD_ANALYSIS:

        road_results = (

            calculate_road_exposure(

                district,

                flood_raster_path,

                aoi_geometry

            )

        )

    else:

        road_results = {

            "total_osm_mapped_road_length_km":
                None,

            "flood_affected_road_length_km":
                None,

            "road_affected_percent":
                None,

            "total_mapped_road_segments":
                None,

            "flood_affected_road_segments":
                None

        }


    # ========================================================
    # 18.11 — FINAL DISTRICT RECORD
    # ========================================================

    summary = {

        "district":
            district,

        "district_area_km2":
            district_area_km2,

        "flooded_area_km2":
            flooded_area_km2,

        "flooded_area_percent":
            flooded_area_percent,

        "total_cropland_km2":
            landcover[
                "total_cropland_km2"
            ],

        "flooded_cropland_km2":
            landcover[
                "flooded_cropland_km2"
            ],

        "cropland_affected_percent":
            landcover[
                "cropland_affected_percent"
            ],

        "total_forest_km2":
            landcover[
                "total_forest_km2"
            ],

        "flooded_forest_km2":
            landcover[
                "flooded_forest_km2"
            ],

        "forest_affected_percent":
            landcover[
                "forest_affected_percent"
            ],

        "flood_period_rainfall_mm":
            flood_period_rainfall,

        "maximum_daily_rainfall_mm":
            maximum_daily_rainfall,

        "rainfall_days":
            len(
                daily_records
            ),

        "mean_elevation_m":
            terrain[
                "mean_elevation_m"
            ],

        "minimum_elevation_m":
            terrain[
                "minimum_elevation_m"
            ],

        "maximum_elevation_m":
            terrain[
                "maximum_elevation_m"
            ],

        "mean_slope_degrees":
            terrain[
                "mean_slope_degrees"
            ],

        "minimum_slope_degrees":
            terrain[
                "minimum_slope_degrees"
            ],

        "maximum_slope_degrees":
            terrain[
                "maximum_slope_degrees"
            ],

        "total_osm_mapped_buildings":
            building_results[
                "total_osm_mapped_buildings"
            ],

        "flood_affected_buildings":
            building_results[
                "flood_affected_buildings"
            ],

        "buildings_affected_percent":
            building_results[
                "buildings_affected_percent"
            ],

        "total_osm_mapped_road_length_km":
            road_results[
                "total_osm_mapped_road_length_km"
            ],

        "flood_affected_road_length_km":
            road_results[
                "flood_affected_road_length_km"
            ],

        "road_affected_percent":
            road_results[
                "road_affected_percent"
            ],

        "total_mapped_road_segments":
            road_results[
                "total_mapped_road_segments"
            ],

        "flood_affected_road_segments":
            road_results[
                "flood_affected_road_segments"
            ]

    }


    # ========================================================
    # 18.12 — SAVE DISTRICT SUMMARY
    # ========================================================

    district_summary_path = os.path.join(

        OUTPUT_DIR,

        f"{district.replace(' ', '_')}"
        "_flood_intelligence_summary.csv"

    )


    district_df = pd.DataFrame(
        [summary]
    )


    district_df.to_csv(

        district_summary_path,

        index=False

    )


    print()
    print(
        "=" * 70
    )

    print(
        f"{district.upper()} ANALYSIS COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        "Summary:",
        district_summary_path
    )


    return summary


# ============================================================
# SECTION 19 — BATCH PROCESS ALL DISTRICTS
# ============================================================


print()
print()
print("=" * 75)
print("STARTING 11-DISTRICT FLOOD INTELLIGENCE ANALYSIS")
print("=" * 75)

print()


all_results = []

failed_districts = []


for district in districts_to_process:

    try:

        result = analyze_district(
            district
        )

        all_results.append(
            result
        )

    except Exception as e:

        print()
        print()
        print("=" * 75)

        print(
            f"ERROR IN DISTRICT: {district}"
        )

        print("=" * 75)

        print(
            str(e)
        )

        print()

        print(
            "This district will be recorded "
            "as failed and the batch will continue."
        )


        failed_districts.append(

            {
                "district":
                    district,

                "error":
                    str(e)

            }

        )


# ============================================================
# SECTION 20 — MASTER SUMMARY
# ============================================================


# print()
# print()
# print("=" * 75)
# print("CREATING MASTER DISTRICT SUMMARY")
# print("=" * 75)


# if len(all_results) > 0:

#     master_df = pd.DataFrame(
#         all_results
#     )


#     # --------------------------------------------------------
#     # ROUND NUMERICAL VALUES
#     # --------------------------------------------------------

#     for column in master_df.columns:

#         if column == "district":

#             continue

#         if pd.api.types.is_numeric_dtype(
#             master_df[column]
#         ):

#             master_df[column] = (

#                 master_df[column]

#                 .round(3)

# #             )


#     # --------------------------------------------------------
#     # SAVE MASTER CSV
#     # --------------------------------------------------------

#     master_path = os.path.join(

#         OUTPUT_DIR,

#         "assam_flood_intelligence_master.csv"

#     )


#     master_df.to_csv(

#         master_path,

#         index=False

#     )


#     print()

#     print(
#         "MASTER CSV SAVED:"
#     )

#     print(
#         master_path
#     )


#     print()

#     print(
#         "DISTRICT SUMMARY"
#     )

#     print(
#         master_df.to_string(
#             index=False
#         )
#     )


# else:

#     print(
#         "No district completed successfully."
#     )


# ============================================================
# SECTION 21 — FAILED DISTRICTS
# ============================================================


# if len(
#     failed_districts
# ) > 0:

#     failed_df = pd.DataFrame(
#         failed_districts
#     )


#     failed_path = os.path.join(

#         OUTPUT_DIR,

#         "failed_districts.csv"

#     )


#     failed_df.to_csv(

#         failed_path,

#         index=False

#     )


#     print()
#     print(
#         "=" * 75
#     )

#     print(
#         "DISTRICTS WITH ERRORS"
#     )

#     print(
#         "=" * 75
#     )


#     print(
#         failed_df.to_string(
#             index=False
#         )
#     )


#     print()

#     print(
#         "Error log:",
#         failed_path
#     )


# else:

#     print()
#     print(
#         "All selected districts completed successfully."
#     )


# # ============================================================
# # SECTION 22 — FINAL OUTPUT CHECK
# # ============================================================


# print()
# print()
# print("=" * 75)
# print("ASSAM FLOOD INTELLIGENCE BATCH ANALYSIS COMPLETE")
# print("=" * 75)

# print()

# print(
#     "Successfully processed:",
#     len(all_results)
# )

# print(
#     "Failed:",
#     len(failed_districts)
# )

# print()

# print(
#     "Output directory:",
#     OUTPUT_DIR
# )

# print()

# print(
#     "Expected master file:"
# )

# print(
#     os.path.join(
#         OUTPUT_DIR,
#         "assam_flood_intelligence_master.csv"
#     )
# )

# print()

# print(
#     "Output folders:"
# )

# print(
#     "  raster/"
# )

# print(
#     "  graphs/"
# )

# print(
#     "  buildings/"
# )

# print(
#     "  roads/"
# )

# print(
#     "  visual_check/"
# )

# print()

# print(
#     "=" * 75
# )