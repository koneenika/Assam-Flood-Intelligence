# ============================================================
# ASSAM FLOOD INTELLIGENCE
# DISTRICT-LEVEL FLOOD ANALYSIS
# CONFIGURATION
# ============================================================


# ============================================================
# EARTH ENGINE
# ============================================================

EE_PROJECT = "koneenika-504814"


# ============================================================
# DISTRICT ASSETS
# ============================================================

DISTRICT_ASSETS = {

    "Biswanath":
        "projects/koneenika-504814/assets/BISWANATH",

    "Charaideo":
        "projects/koneenika-504814/assets/CHARAIDEO",

    "Darrang":
        "projects/koneenika-504814/assets/DARRANG",

    "Golaghat":
        "projects/koneenika-504814/assets/GOLAGHAT",

    "Hojai":
        "projects/koneenika-504814/assets/HOJAI",

    "Jorhat":
        "projects/koneenika-504814/assets/JORHAT",

    # "Karbi Anglong":
    #     "projects/koneenika-504814/assets/KARBI_ANALOG",

    "Lakhimpur":
        "projects/koneenika-504814/assets/LAKHIMPUR",

    "Nagaon":
        "projects/koneenika-504814/assets/NAGAON",

    "Sivasagar":
        "projects/koneenika-504814/assets/SHIVASAGAR",

    "Sonitpur":
        "projects/koneenika-504814/assets/SONITPUR",
}
# ============================================================
# ASSAM STATE ASSET
# ============================================================

ASSAM_ASSET = (
    "projects/koneenika-504814/assets/ASSAM"
)

# ============================================================
# DISTRICT LIST
# ============================================================

DISTRICT_NAMES = [

    "Biswanath",
    "Charaideo",
    "Darrang",
    "Golaghat",
    "Hojai",
    "Jorhat",
    # "Karbi Anglong",
    "Lakhimpur",
    "Nagaon",
    "Sivasagar",
    "Sonitpur",

]


# ============================================================
# BATCH MODE
# ============================================================

# True = process all 11 districts
# False = process only TEST_DISTRICT

BATCH_MODE = False

TEST_DISTRICT = "Jorhat"


# ============================================================
# EVENT
# ============================================================

EVENT_NAME = "Assam Flood 2026"


# ============================================================
# SENTINEL-1 SEARCH WINDOW
# ============================================================

S1_SEARCH_START = "2026-06-01"

# Earth Engine filterDate end is exclusive
S1_SEARCH_END = "2026-10-01"


# ============================================================
# FLOOD ANALYSIS PERIODS
# ============================================================

PRE_START = "2026-06-15"
PRE_END = "2026-07-18"

FLOOD_START = "2026-07-18"
FLOOD_END = "2026-08-12"

POST_START = "2026-08-12"
POST_END = "2026-10-01"


# ============================================================
# SENTINEL-1
# ============================================================

S1_COLLECTION = "COPERNICUS/S1_GRD"

S1_POLARIZATION = "VV"

S1_INSTRUMENT_MODE = "IW"


# ============================================================
# FLOOD DETECTION
# ============================================================

FLOOD_DIFFERENCE_THRESHOLD = -2.0


# ============================================================
# JRC GLOBAL SURFACE WATER
# ============================================================

JRC_WATER_COLLECTION = (
    "JRC/GSW1_4/GlobalSurfaceWater"
)

PERMANENT_WATER_THRESHOLD = 90


# ============================================================
# ESA WORLDCOVER
# ============================================================

WORLDCOVER_COLLECTION = (
    "ESA/WorldCover/v200"
)

WORLD_COVER_WATER = 80

WORLD_COVER_TREE_COVER = 10

WORLD_COVER_CROPLAND = 40


# ============================================================
# DEM
# ============================================================

DEM_COLLECTION = (
    "COPERNICUS/DEM/GLO30_2024_1"
)


# ============================================================
# RAINFALL
# ============================================================

GPM_COLLECTION = (
    "NASA/GPM_L3/IMERG_V07"
)


# ============================================================
# OSM
# ============================================================

OSM_BUILDING_TAG = {
    "building": True
}


# ============================================================
# ANALYSIS OPTIONS
# ============================================================

RUN_BUILDING_ANALYSIS = True

RUN_ROAD_ANALYSIS = True


# ============================================================
# LOCAL FLOOD RASTER
# ============================================================

# 30 m raster is a visualization/intersection product.
# Authoritative flood area remains the 10 m GEE calculation.

DOWNLOAD_FLOOD_RASTER = True

FLOOD_RASTER_SCALE = 30


# ============================================================
# OPTIONAL RASTER EXPORTS
# ============================================================

EXPORT_ELEVATION_MAP = False

EXPORT_SLOPE_MAP = False

EXPORT_SOIL_MAP = False

EXPORT_SOIL_MOISTURE = False

EXPORT_FLOOD_DEPTH = False

EXPORT_LARGE_RASTER = False


# ============================================================
# OPTIONAL RAINFALL EXPORTS
# ============================================================

EXPORT_RAINFALL_GRAPH = True


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_DIR = "Output"

VISUAL_CHECK_DIR = (
    "Output/visual_check"
)