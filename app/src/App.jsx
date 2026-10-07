import { useEffect, useMemo, useState } from "react";

import {
  ArrowLeft,
  ArrowRight,
  Building2,
  CalendarDays,
  Check,
  ChevronRight,
  CloudRain,
  Droplets,
  Leaf,
  Map,
  MapPinned,
  Mountain,
  Navigation,
  Route,
  Sparkles,
  Trees,
  Waves,
} from "lucide-react";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  GeoJSON,
  ImageOverlay,
  MapContainer,
  TileLayer,
  useMap,
} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";
import "./App.css";


/* =========================================================
   PROJECT SCOPE
========================================================= */

const ANALYZED_DISTRICTS = [
  "Biswanath",
  "Charaideo",
  "Darrang",
  "Golaghat",
  "Hojai",
  "Jorhat",
  "Nagaon",
  "Sivasagar",
  "Sonitpur",
];

const EXCLUDED_DISTRICTS = [
  "Lakhimpur",
  "Karbi Anglong",
];


/* =========================================================
   DATA PATHS
========================================================= */

const MASTER_DATA_URL =
  "/data/master_dashboard_data.json";

const ASSAM_GEOJSON_URL =
  "https://cdn.jsdelivr.net/gh/udit-001/india-maps-data@2884453/geojson/states/assam.geojson";


/* =========================================================
   BASE MAPS
========================================================= */

/*
  Assam overview:
  Normal OSM map — no API key.
*/

const OVERVIEW_MAP_URL =
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";


/*
  District page:
  Satellite basemap from Esri ArcGIS.
  No API key is required for this tile endpoint.
*/

const DISTRICT_MAP_URL =
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";


/* =========================================================
   GENERAL HELPERS
========================================================= */

function normalizeDistrict(name) {
  return String(name || "")
    .trim()
    .toLowerCase();
}


function isExcludedDistrict(name) {

  return EXCLUDED_DISTRICTS.some(
    (district) =>
      normalizeDistrict(district) ===
      normalizeDistrict(name)
  );

}


function getFeatureDistrict(feature) {

  const props =
    feature?.properties || {};

  return (
    props.DISTRICT ||
    props.district ||
    props.DISTRICT_NAME ||
    props.district_name ||
    props.DTNAME ||
    props.DT_NAME ||
    props.NAME_2 ||
    props.NAME ||
    "Unknown District"
  );

}


function getProperty(
  properties,
  names
) {

  for (const name of names) {

    if (
      properties?.[name] !==
        undefined &&
      properties?.[name] !==
        null
    ) {

      return properties[name];

    }

  }

  return null;

}


function extractArray(
  json,
  keys = []
) {

  if (Array.isArray(json)) {
    return json;
  }


  for (const key of keys) {

    if (
      Array.isArray(
        json?.[key]
      )
    ) {

      return json[key];

    }

  }


  if (
    Array.isArray(
      json?.data
    )
  ) {

    return json.data;

  }


  return [];

}


function escapeHtml(value) {

  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

}


function normalizeBounds(
  boundsData
) {

  if (!boundsData) {
    return null;
  }


  if (
    Array.isArray(boundsData) &&
    boundsData.length === 2 &&
    Array.isArray(boundsData[0]) &&
    Array.isArray(boundsData[1])
  ) {

    return boundsData;

  }


  if (
    Array.isArray(
      boundsData?.bounds
    ) &&
    boundsData.bounds.length === 2
  ) {

    return boundsData.bounds;

  }


  const south =
    boundsData.south ??
    boundsData.bottom ??
    boundsData.min_lat ??
    boundsData.minLat;


  const west =
    boundsData.west ??
    boundsData.left ??
    boundsData.min_lon ??
    boundsData.minLng;


  const north =
    boundsData.north ??
    boundsData.top ??
    boundsData.max_lat ??
    boundsData.maxLat;


  const east =
    boundsData.east ??
    boundsData.right ??
    boundsData.max_lon ??
    boundsData.maxLng;


  if (
    [south, west, north, east].every(
      (value) =>
        value !== undefined &&
        value !== null
    )
  ) {

    return [
      [south, west],
      [north, east],
    ];

  }


  return null;
}


/* =========================================================
   FLOOD COLOUR
========================================================= */

function getFloodColor(percent) {

  if (percent >= 12) {
    return "#D53A31";
  }

  if (percent >= 7) {
    return "#E7583E";
  }

  if (percent >= 4) {
    return "#ED8750";
  }

  if (percent >= 2) {
    return "#DDA64B";
  }

  return "#C8BB62";

}

/* =========================================================
   FLOOD IMPACT CLASSIFICATION
========================================================= */

function getFloodImpactStatus(percent) {

  const value =
    Number(percent) || 0;


  if (value >= 12) {

    return {
      label: "Very High Flood Impact",
      shortLabel: "VERY HIGH IMPACT",
      className: "very-high",
    };

  }


  if (value >= 7) {

    return {
      label: "High Flood Impact",
      shortLabel: "HIGH IMPACT",
      className: "high",
    };

  }


  if (value >= 2) {

    return {
      label: "Moderate Flood Impact",
      shortLabel: "MODERATE IMPACT",
      className: "moderate",
    };

  }


  return {
    label: "Low Flood Impact",
    shortLabel: "LOW IMPACT",
    className: "low",
  };

}
/* =========================================================
   WHY IT FLOODED — DISTRICT-SPECIFIC CONTEXT
========================================================= */

const DISTRICT_FLOOD_REASONS = {

  Biswanath: [
    "The district lies along the Brahmaputra floodplain, with several rivers and tributaries including the Solengi, Brahmajan, Chatrang and Sessa contributing to local flood vulnerability.",
    "Low-lying flood-prone areas around the Brahmaputra and its tributaries can experience inundation when river levels rise during the monsoon flood period.",
    "The July 2026 event affected Biswanath early in the flood season, with rainfall and rising river systems contributing to the observed flood footprint.",
  ],

  Charaideo: [
    "Charaideo experienced exceptionally heavy rainfall during the July 2026 flood period, with rainfall reported well above normal during the event.",
    "The district is drained by systems including the Desang and its tributaries, which can respond rapidly to intense upstream rainfall.",
    "CWC-linked observations recorded new high flood levels in the Desang system during July 2026, indicating unusually elevated river conditions in the basin.",
  ],

  Darrang: [
    "Darrang has extensive low-lying floodplain areas, reflected in its comparatively low mean elevation within the nine districts analysed.",
    "The district is influenced by the Brahmaputra and associated tributary drainage systems, making river rise and overbank flow important flood pathways.",
    "Its July 2026 flood footprint was the largest among the analysed districts, with 16.14% of the district area identified as flooded in this assessment.",
  ],

  Golaghat: [
    "The Dhansiri is the principal river system in Golaghat and drains a large catchment extending into Nagaland before joining the Brahmaputra.",
    "Heavy rainfall in the upstream catchment can increase river discharge and raise water levels downstream through the Dhansiri and connected tributaries.",
    "Golaghat was among the Assam districts affected during the July 2026 flood event, when heavy rainfall and swollen river systems increased inundation pressure.",
  ],

  Hojai: [
    "The Kopili is one of the major rivers affecting Hojai, while the Jamuna and smaller tributaries also contribute to the district's flood drainage system.",
    "Heavy rainfall in the upstream hill catchments can rapidly increase downstream discharge and create flash-flood conditions.",
    "The district's low-lying riverine areas are particularly exposed when high river levels restrict normal drainage from surrounding floodplains.",
  ],

  Jorhat: [
    "Northern Jorhat is largely situated within the Brahmaputra floodplain, where relatively low floodplain elevations increase exposure to riverine inundation.",
    "Heavy rainfall during July 2026 contributed to swollen river systems across Upper Assam, while the Brahmaputra also remained a major drainage constraint.",
    "The flood footprint in Jorhat expanded along low-lying areas during the event, consistent with the interaction between intense rainfall, tributary response and high river levels.",
  ],

  Nagaon: [
    "Nagaon is crossed by major river systems including the Brahmaputra, Kopili and Kollong, together with extensive wetlands, beels and marshy lowlands.",
    "Heavy rainfall in the upstream Kopili catchment can increase river discharge and contribute to flooding downstream.",
    "When the Brahmaputra is already high, drainage from tributaries such as the Kopili and Kollong can become less efficient, increasing the potential for prolonged inundation.",
  ],

  Sivasagar: [
    "Sivasagar is drained by several major rivers including the Dikhow, Desang, Janji and Darika, all ultimately connected to the Brahmaputra drainage system.",
    "The district experienced some of the most severe river conditions during the July 2026 event, with the Dikhow and Desang systems reaching exceptionally high levels.",
    "CWC-linked observations recorded new high flood levels in multiple Sivasagar river systems during July 2026, indicating severe riverine pressure during the event.",
  ],

  Sonitpur: [
    "Sonitpur lies between the Brahmaputra and the foothills of Arunachal Pradesh, making it vulnerable to both riverine flooding and rapid runoff from upstream catchments.",
    "The Jia-Bharali and its tributaries can receive substantial upstream flows from the Arunachal foothills during intense monsoon rainfall.",
    "Low-lying areas around Tezpur and other river corridors can experience inundation when the Brahmaputra and tributary levels rise simultaneously.",
  ],

};

/* =========================================================
   MASTER DATA NORMALISER
========================================================= */

function normalizeDistrictRecord(
  record
) {

  return {

    district:
      record.district,

    districtArea:
      record.flood?.district_area_km2 ??
      0,

    floodedArea:
      record.flood?.flooded_area_km2 ??
      0,

    floodedPercent:
      record.flood?.flooded_area_percent ??
      0,

    totalCropland:
      record.agriculture?.total_cropland_km2 ??
      0,

    floodedCropland:
      record.agriculture?.flooded_cropland_km2 ??
      0,

    croplandAffectedPercent:
      record.agriculture?.affected_percent ??
      0,

    totalForest:
      record.forest?.total_forest_km2 ??
      0,

    floodedForest:
      record.forest?.flooded_forest_km2 ??
      0,

    forestAffectedPercent:
      record.forest?.affected_percent ??
      0,

    totalBuildings:
      record.buildings?.total_mapped ??
      0,

    affectedBuildings:
      record.buildings?.affected ??
      0,

    buildingsAffectedPercent:
      record.buildings?.affected_percent ??
      0,

    totalRoadLength:
      record.roads?.total_length_km ??
      0,

    affectedRoadLength:
      record.roads?.affected_length_km ??
      0,

    roadAffectedPercent:
      record.roads?.affected_percent ??
      0,

    totalRoadSegments:
      record.roads?.total_mapped_road_segments ??
      0,

    affectedRoadSegments:
      record.roads?.flood_affected_road_segments ??
      0,

    rainfall:
      record.rainfall?.flood_period_total_mm ??
      0,

    maxDailyRainfall:
      record.rainfall?.maximum_daily_mm ??
      0,

    rainfallDays:
      record.rainfall?.rainfall_days ??
      0,

    meanElevation:
      record.topography?.mean_elevation_m ??
      0,

    minElevation:
      record.topography?.minimum_elevation_m ??
      0,

    maxElevation:
      record.topography?.maximum_elevation_m ??
      0,

    meanSlope:
      record.topography?.mean_slope_degrees ??
      0,

    minSlope:
      record.topography?.minimum_slope_degrees ??
      0,

    maxSlope:
      record.topography?.maximum_slope_degrees ??
      0,

    floodedCroplandShare:
      record.flooded_area_land_cover
        ?.cropland_percent ??
      0,

    floodedForestShare:
      record.flooded_area_land_cover
        ?.forest_percent ??
      0,

    floodedOtherShare:
      record.flooded_area_land_cover
        ?.other_percent ??
      0,

  };

}


/* =========================================================
   DASHBOARD DATA HOOK
========================================================= */

function useDashboardData() {

  const [
    districtData,
    setDistrictData,
  ] = useState({});


  const [
    overviewData,
    setOverviewData,
  ] = useState({});
  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {

    let cancelled = false;


    async function loadData() {

      try {

        setLoading(true);
        setError("");


        const masterResponse =
          await fetch(
            MASTER_DATA_URL
          );


        if (
          !masterResponse.ok
        ) {

          throw new Error(
            "Could not load master dashboard data."
          );

        }


        const masterJson =
          await masterResponse.json();


        const overview =
          masterJson?.overview ?? {};
        const records =
          extractArray(
            masterJson,
            [
              "districts",
              "records",
            ]
          );


        const districtLookup = {};


        records.forEach(
          (record) => {

            const normalized =
              normalizeDistrictRecord(
                record
              );


            if (
              normalized.district &&
              !isExcludedDistrict(
                normalized.district
              )
            ) {

              districtLookup[
                normalized.district
              ] =
                normalized;

            }

          }
        );


        if (!cancelled) {

          setDistrictData(
            districtLookup
          );


          setOverviewData(
            overview
          );
        }

      } catch (err) {

        if (!cancelled) {

          setError(
            err.message ||
            "Unable to load dashboard data."
          );

        }

      } finally {

        if (!cancelled) {

          setLoading(false);

        }

      }

    }


    loadData();


    return () => {

      cancelled = true;

    };

  }, []);


  return {
    districtData,
    overviewData,
    loading,
    error,
  };

}


/* =========================================================
   RAINFALL DATA HOOK
========================================================= */

function useRainfallData(
  district
) {

  const [
    rainfallData,
    setRainfallData,
  ] = useState([]);


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {

    if (!district) {

      setRainfallData([]);

      return;

    }


    let cancelled = false;


    async function loadRainfall() {

      try {

        setLoading(true);
        setError("");


        const response =
          await fetch(
            `/data/rainfall/${encodeURIComponent(
              district
            )}.json`
          );


        if (!response.ok) {

          throw new Error(
            `Rainfall data unavailable for ${district}.`
          );

        }


        const json =
          await response.json();


        const raw =
          extractArray(
            json,
            [
              "rainfall",
              "series",
              "daily",
              "records",
            ]
          );


        const series =
          raw
            .map(
              (
                item,
                index
              ) => {

                const rainfallValue =
                  Number(
                    item.rainfall ??
                    item.rainfall_mm ??
                    item.Rainfall ??
                    item.Rainfall_mm ??
                    item.value ??
                    item.Value ??
                    0
                  );


                const date =
                  item.date ??
                  item.Date ??
                  item.day ??
                  item.Day ??
                  `Day ${
                    index + 1
                  }`;


                return {

                  date:
                    String(
                      date
                    ),

                  rainfall:
                    Number.isFinite(
                      rainfallValue
                    )
                      ? rainfallValue
                      : 0,

                };

              }
            );


        if (!cancelled) {

          setRainfallData(
            series
          );

        }

      } catch (err) {

        if (!cancelled) {

          setError(
            err.message ||
            "Unable to load rainfall data."
          );

        }

      } finally {

        if (!cancelled) {

          setLoading(false);

        }

      }

    }


    loadRainfall();


    return () => {

      cancelled = true;

    };

  }, [district]);


  return {
    rainfallData,
    loading,
    error,
  };

}


/* =========================================================
   ASSAM GEOJSON HOOK
========================================================= */

function useAssamGeoJson() {

  const [
    geoJson,
    setGeoJson,
  ] = useState(null);


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {

    let cancelled = false;


    async function loadGeoJson() {

      try {

        setLoading(true);
        setError("");


        const response =
          await fetch(
            ASSAM_GEOJSON_URL
          );


        if (!response.ok) {

          throw new Error(
            `Map request failed: ${response.status}`
          );

        }


        const json =
          await response.json();


        if (!cancelled) {

          setGeoJson(json);

        }

      } catch (err) {

        if (!cancelled) {

          setError(
            err.message ||
            "Unable to load Assam boundaries."
          );

        }

      } finally {

        if (!cancelled) {

          setLoading(false);

        }

      }

    }


    loadGeoJson();


    return () => {

      cancelled = true;

    };

  }, []);


  return {
    geoJson,
    loading,
    error,
  };

}


/* =========================================================
   DISTRICT SPATIAL DATA HOOK
========================================================= */

function useDistrictSpatialData(
  district
) {

  const [
    spatial,
    setSpatial,
  ] = useState({

    buildings:
      null,

    roads:
      null,

    floodImage:
      null,

    floodBounds:
      null,

  });


  const [
    loading,
    setLoading,
  ] = useState(false);


  const [
    error,
    setError,
  ] = useState("");


  useEffect(() => {

    if (!district) {
      return;
    }


    let cancelled = false;


    async function loadSpatial() {

      try {

        setLoading(true);
        setError("");


        const base =
          `/data/spatial/${encodeURIComponent(
            district
          )}`;


        const [
          buildingsResponse,
          roadsResponse,
          boundsResponse,
        ] =
          await Promise.all([
            fetch(
              `${base}/buildings.geojson`
            ),

            fetch(
              `${base}/affected_roads.geojson`
            ),

            fetch(
              `${base}/flood_extent_bounds.json`
            ),
          ]);


        if (
          !buildingsResponse.ok
        ) {

          throw new Error(
            `Buildings layer unavailable for ${district}.`
          );

        }


        if (
          !roadsResponse.ok
        ) {

          throw new Error(
            `Affected road layer unavailable for ${district}.`
          );

        }


        if (
          !boundsResponse.ok
        ) {

          throw new Error(
            `Flood raster bounds unavailable for ${district}.`
          );

        }


        const buildings =
          await buildingsResponse.json();


        const roads =
          await roadsResponse.json();


        const boundsJson =
          await boundsResponse.json();


        const floodBounds =
          normalizeBounds(
            boundsJson
          );


        if (!floodBounds) {

          throw new Error(
            `Invalid flood bounds for ${district}.`
          );

        }


        if (!cancelled) {

          setSpatial({

            buildings,

            roads,

            floodImage:
              `${base}/flood_extent.png`,

            floodBounds,

          });

        }

      } catch (err) {

        if (!cancelled) {

          setError(
            err.message ||
            "Unable to load spatial layers."
          );

        }

      } finally {

        if (!cancelled) {

          setLoading(false);

        }

      }

    }


    loadSpatial();


    return () => {

      cancelled = true;

    };

  }, [district]);


  return {
    spatial,
    loading,
    error,
  };

}


/* =========================================================
   FIT MAP
========================================================= */

function FitBounds({
  geoJson,
  districtName = null,
  boundsOverride = null,
  extraZoom = 0,
}) {

  const map =
    useMap();


  useEffect(() => {

    if (boundsOverride) {

      try {

        map.fitBounds(
          boundsOverride,
          {
            padding: [
              20,
              20,
            ],
          }
        );


        if (extraZoom) {

          map.setZoom(
            map.getZoom() +
            extraZoom
          );

        }

      } catch {
        // Keep map.
      }

      return;

    }


    if (!geoJson) {
      return;
    }


    let mapData =
      geoJson;


    if (districtName) {

      const features =
        geoJson.features?.filter(
          (feature) =>
            normalizeDistrict(
              getFeatureDistrict(
                feature
              )
            ) ===
            normalizeDistrict(
              districtName
            )
        ) || [];


      if (
        features.length
      ) {

        mapData = {
          ...geoJson,
          features,
        };

      }

    }


    try {

      const bounds =
        L.geoJSON(
          mapData
        ).getBounds();


      if (
        bounds.isValid()
      ) {

        map.fitBounds(
          bounds,
          {
            padding: [
              20,
              20,
            ],
          }
        );


        if (extraZoom) {

          map.setZoom(
            map.getZoom() +
            extraZoom
          );

        }

      }

    } catch {
      // Keep map.
    }

  }, [
    geoJson,
    districtName,
    boundsOverride,
    extraZoom,
    map,
  ]);


  return null;

}


/* =========================================================
   MAIN APP
========================================================= */

function App() {

  const {
    districtData,
    overviewData,
    loading:
      dataLoading,
    error:
      dataError,
  } =
    useDashboardData();


  const {
    geoJson,
    loading:
      mapLoading,
    error:
      mapError,
  } =
    useAssamGeoJson();


  const [
    page,
    setPage,
  ] =
    useState(
      "overview"
    );


  const [
    selectedDistrict,
    setSelectedDistrict,
  ] =
    useState(null);


  const availableDistricts =
    useMemo(
      () =>
        ANALYZED_DISTRICTS.filter(
          (district) =>
            Boolean(
              districtData[
                district
              ]
            )
        ),
      [districtData]
    );


  function openDistrict(
    district
  ) {

    if (
      !districtData[
        district
      ]
    ) {
      return;
    }


    setSelectedDistrict(
      district
    );


    setPage(
      "district"
    );


    window.scrollTo({
      top: 0,
      behavior:
        "smooth",
    });

  }


  function goOverview() {

    setSelectedDistrict(
      null
    );


    setPage(
      "overview"
    );


    window.scrollTo({
      top: 0,
      behavior:
        "smooth",
    });

  }


  function navigateTo(
    sectionId
  ) {

    setPage(
      "overview"
    );


    setTimeout(() => {

      document
        .getElementById(
          sectionId
        )
        ?.scrollIntoView({
          behavior:
            "smooth",
          block:
            "start",
        });

    }, 70);

  }


  return (

    <div
      className={`app-shell ${
        page ===
        "district"
          ? "district-mode"
          : "overview-mode"
      }`}
    >

      <Header
        page={
          page
        }
        onOverview={
          goOverview
        }
        onNavigate={
          navigateTo
        }
      />


      {page ===
      "overview" ? (

        <OverviewPage
          districtData={
            districtData
          }

          availableDistricts={
            availableDistricts
          }

          overviewData={
            overviewData
          }
          geoJson={
            geoJson
          }

          mapLoading={
            mapLoading
          }

          mapError={
            mapError
          }

          dataLoading={
            dataLoading
          }

          dataError={
            dataError
          }

          onOpenDistrict={
            openDistrict
          }

          onNavigate={
            navigateTo
          }

        />

      ) : (

        <DistrictDetailPage
          district={
            selectedDistrict
          }

          data={
            selectedDistrict
              ? districtData[
                  selectedDistrict
                ]
              : null
          }

          geoJson={
            geoJson
          }

          mapLoading={
            mapLoading
          }

          mapError={
            mapError
          }

          onBack={
            goOverview
          }

        />

      )}

    </div>

  );

}


/* =========================================================
   HEADER
========================================================= */

function Header({
  page,
  onOverview,
  onNavigate,
}) {

  return (

    <header className="site-header">

      <button
        className="brand"
        onClick={
          onOverview
        }
      >

        <div className="brand-symbol">

          <MapPinned size={25} />

        </div>


        <div className="brand-text">

          <h1>
            Assam Flood Intelligence
          </h1>


          <p>
            Satellite data
            <span>•</span>
            Open geospatial data
            <span>•</span>
            District insights
          </p>

        </div>

      </button>


      <nav className="header-nav">

        <button
          className={
            page ===
            "overview"
              ? "header-link active"
              : "header-link"
          }
          onClick={
            onOverview
          }
        >
          Overview
        </button>


        <button
          className="header-link"
          onClick={() =>
            onNavigate(
              "district-explorer"
            )
          }
        >
          District Explorer
        </button>
<button
          className="header-link"
          onClick={() =>
            onNavigate(
              "methodology-section"
            )
          }
        >
          Methodology
        </button>

      </nav>


      <div className="event-pill">

        <CalendarDays
          size={17}
        />


        <div>

          <span>
            ANALYZED EVENT
          </span>


          <strong>
            July 2026
          </strong>

        </div>

      </div>

    </header>

  );

}


/* =========================================================
   OVERVIEW
========================================================= */

function OverviewPage({
  districtData,
  availableDistricts,
  overviewData,
  geoJson,
  mapLoading,
  mapError,
  dataLoading,
  onOpenDistrict,
  onNavigate,
}) {

  const totalFloodedArea =
    Object.values(
      districtData
    ).reduce(
      (
        total,
        district
      ) =>
        total +
        district.floodedArea,
      0
    );


  const highestPeriodRainfall =
    Math.max(
      0,
      ...Object.values(
        districtData
      ).map(
        (
          district
        ) =>
          district.rainfall
      )
    );


  const highestDailyRainfall =
    Math.max(
      0,
      ...Object.values(
        districtData
      ).map(
        (
          district
        ) =>
          district.maxDailyRainfall
      )
    );


  return (

    <main className="page">


      {/* HERO */}

      <section className="overview-hero">

        <div className="hero-copy">

          <div className="tiny-label">
            ASSAM • FLOOD EVENT INTELLIGENCE
          </div>


          <h2>

            One state.
            <br />

            <span>
              One flood story.
            </span>

          </h2>


          <p>

            Explore the analyzed July 2026 flood event
            across Assam through satellite-derived flood
            extent, rainfall, terrain and infrastructure.

          </p>


          <div className="hero-actions">

            <button
              className="plum-button"
              onClick={() =>
                onNavigate(
                  "district-explorer"
                )
              }
            >

              Explore districts

              <ArrowRight
                size={17}
              />

            </button>
</div>


          <div className="hero-note">

            <Sparkles size={16} />

            <span>

              {dataLoading
                ? "Loading analyzed district data..."
                : `${availableDistricts.length} analyzed districts are currently included in the project.`}

            </span>

          </div>

        </div>


        {/* EVENT SNAPSHOT */}

        <div className="hero-aside">

          <div className="hero-aside-top">

            <span>
              EVENT SNAPSHOT
            </span>


            <strong>
              July 2026
            </strong>

          </div>


          <div className="hero-snapshot">

            <SnapshotItem
              icon={Map}
              label="Analyzed districts"
              value={
                availableDistricts.length
              }
            />


            <SnapshotItem
              icon={Droplets}
              label="Flooded area"
              value={
                `${totalFloodedArea.toFixed(
                  1
                )} km²`
              }
            />


            <SnapshotItem
              icon={CloudRain}
              label="Highest daily rainfall"
              value={
                `${highestDailyRainfall.toFixed(
                  1
                )} mm`
              }
            />


            <SnapshotItem
              icon={Waves}
              label="Highest flood-period rainfall"
              value={
                `${highestPeriodRainfall.toFixed(
                  1
                )} mm`
              }
            />

          </div>

        </div>

      </section>


      {/* ASSAM MAP */}

      <section className="overview-map-grid">

        <div className="map-card large-card">

          <div className="card-heading">

            <div>

              <p>
                SPATIAL OVERVIEW
              </p>


              <h3>
                Assam flood map
              </h3>


              <span>

                All Assam districts are shown.
                The nine analyzed districts are
                highlighted and clickable.

              </span>

            </div>


            <div className="map-key">

              <div>

                <span className="key-dot lower"></span>

                Lower flood extent

              </div>


              <div>

                <span className="key-dot higher"></span>

                Higher flood extent

              </div>

            </div>

          </div>


          <div className="overview-leaflet-wrapper">

            <AssamMap
              geoJson={
                geoJson
              }

              loading={
                mapLoading
              }

              error={
                mapError
              }

              districtData={
                districtData
              }

              onDistrictClick={
                onOpenDistrict
              }

            />

          </div>

        </div>


        <aside className="overview-side">


          <div className="story-card">

            <div className="story-icon">

              <Leaf size={21} />

            </div>


            <p>
              HOW TO READ THIS
            </p>


            <h3>
              Start with the map.
            </h3>


            <span>

              This is the Assam-wide entry point.
              Explore the highlighted districts first,
              then open an individual district for its
              detailed flood and exposure analysis.

            </span>

          </div>


          <div className="soft-card event-card-large">

            <div className="card-heading small-heading">

              <div>

                <p>
                  ANALYZED FOOTPRINT
                </p>


                <h3>
                  Districts in this study
                </h3>

              </div>


              <Map size={19} />

            </div>


            <div className="district-chip-grid">

              {availableDistricts.map(
                (
                  district
                ) => (

                  <button
                    key={
                      district
                    }
                    onClick={() =>
                      onOpenDistrict(
                        district
                      )
                    }
                  >

                    {district}

                    <ChevronRight
                      size={15}
                    />

                  </button>

                )
              )}

            </div>

          </div>

        </aside>

      </section>


      {/* OVERVIEW EVENT DATA */}

      <OverviewEventData
        overviewData={
          overviewData
        }
      />


      {/* DISTRICT EXPLORER */}

      <section
        id="district-explorer"
        className="district-explorer"
      >

        <div className="section-heading">

          <div>

            <p>
              DISTRICT EXPLORER
            </p>


            <h3>
              Choose a district to go deeper.
            </h3>

          </div>


          <span>
            {availableDistricts.length}
            analyzed districts
          </span>

        </div>


        <div className="district-list">

          {availableDistricts.map(
            (
              district,
              index
            ) => {

              const item =
                districtData[
                  district
                ];


              return (

                <button
                  key={
                    district
                  }
                  className="district-row"
                  onClick={() =>
                    onOpenDistrict(
                      district
                    )
                  }
                >

                  <div className="district-row-number">

                    {String(
                      index + 1
                    ).padStart(
                      2,
                      "0"
                    )}

                  </div>


                  <div className="district-row-name">

                    <strong>
                      {district}
                    </strong>


                    <span>
                      Assam
                    </span>

                  </div>


                  <div className="district-row-stat">

                    <span>
                      Flooded area
                    </span>


                    <strong>

                      {item.floodedArea.toFixed(
                        2
                      )} km²

                    </strong>

                  </div>


                  <div className="district-row-stat">

                    <span>
                      District extent
                    </span>


                    <strong>

                      {item.floodedPercent.toFixed(
                        2
                      )}%

                    </strong>

                  </div>


                  <div className="district-row-stat">

                    <span>
                      Flood-period rainfall
                    </span>


                    <strong>

                      {item.rainfall.toFixed(
                        1
                      )} mm

                    </strong>

                  </div>


                  <div className="district-row-arrow">

                    <ChevronRight
                      size={20}
                    />

                  </div>

                </button>

              );

            }
          )}

        </div>

      </section>


      {/* METHODOLOGY */}

      <section
        id="methodology-section"
        className="methodology-section"
      >

        <div className="methodology-card">

          <div className="methodology-mark">

            <Sparkles size={21} />

          </div>


          <div>

            <p>
              METHODOLOGY
            </p>


            <h3>
              An event-focused geospatial dashboard
            </h3>


            <span>

              Flood extent, rainfall, terrain and
              infrastructure layers are presented
              as observations from the analyzed
              July 2026 event.

            </span>

          </div>


          <button
            onClick={() =>
              window.scrollTo({
                top: 0,
                behavior:
                  "smooth",
              })
            }
          >

            Back to top

            <ArrowRight
              size={16}
            />

          </button>

        </div>

      </section>


      <footer className="site-footer">

        <div>
          Assam Flood Intelligence
        </div>


        <span>
          Satellite + open geospatial data
        </span>


        <span>
          •
        </span>


        <span>
          July 2026 analyzed event
        </span>


        <span className="footer-status">

          <span></span>

          Analysis ready

        </span>

      </footer>

    </main>

  );

}


/* =========================================================
   OVERVIEW EVENT DATA
========================================================= */

function OverviewEventData({
  overviewData,
}) {

  const rainfall =
    overviewData?.rainfall || {};

  const rainfallSummary =
    rainfall.summary || {};

  const rainfallDaily =
    Array.isArray(rainfall.daily)
      ? rainfall.daily.map((item) => ({
          date: item.date || "",
          label: item.date
            ? item.date.slice(5).replace("-", "/")
            : "",
          rainfall: Number(item.rainfall_mm ?? 0),
        }))
      : [];

  const landCover =
    Array.isArray(overviewData?.landcover?.landcover)
      ? overviewData.landcover.landcover
      : [];

  const totalFloodedArea = Number(
    overviewData?.landcover?.total_flooded_area_km2 ?? 0
  );

  const landCoverColors = {
    Cropland: "#D6AD49",
    Forest: "#79986B",
    Other: "#8BADD4",
  };

  return (
    <section
      id="event-data-section"
      className="overview-event-data"
    >

      <div className="section-heading">
        <div>
          <p>EVENT OVERVIEW</p>
          <h3>Assam-wide rainfall data</h3>
        </div>
      </div>

      <div className="overview-event-grid">

        <div className="overview-rainfall-card soft-card">
          <div className="overview-rainfall-summary">
            <div>
              <p>ASSAM-WIDE RAINFALL</p>
              <h4>
                {Number(
                  rainfallSummary.accumulated_rainfall_mm ?? 0
                ).toFixed(2)}
                <span> mm</span>
              </h4>
</div>

            <div className="overview-rainfall-stats">
              <div>
                <span>Maximum daily</span>
                <strong>
                  {Number(
                    rainfallSummary.maximum_daily_rainfall_mm ?? 0
                  ).toFixed(2)} mm
                </strong>
              </div>
              <div>
                <span>Rainfall days</span>
                <strong>
                  {Number(
                    rainfallSummary.rainfall_days ?? rainfallDaily.length
                  )}
                </strong>
              </div>
            </div>
          </div>

          <div className="overview-rainfall-chart">
            {rainfallDaily.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={rainfallDaily}
                  margin={{ top: 18, right: 18, left: 2, bottom: 18 }}
                >
                  <defs>
                    <linearGradient
                      id="overviewRainfallFill"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop offset="0%" stopColor="#527CAA" stopOpacity={0.42} />
                      <stop offset="100%" stopColor="#527CAA" stopOpacity={0.06} />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    strokeDasharray="2 3"
                    stroke="rgba(82,124,170,0.16)"
                  />

                  <XAxis
                    dataKey="label"
                    tick={{ fill: "#71252B", fontSize: 8 }}
                    tickLine={false}
                    axisLine={{ stroke: "rgba(113,37,43,0.22)" }}
                  />

                  <YAxis
                    tick={{ fill: "#71252B", fontSize: 8 }}
                    tickLine={false}
                    axisLine={{ stroke: "rgba(113,37,43,0.22)" }}
                    tickFormatter={(value) => Number(value).toFixed(0)}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#F7F2E8",
                      border: "1px solid rgba(113,37,43,0.15)",
                      borderRadius: "10px",
                      fontSize: "9px",
                      color: "#71252B",
                    }}
                    labelStyle={{ color: "#71252B", fontWeight: 800 }}
                    formatter={(value) => [
                      `${Number(value).toFixed(2)} mm`,
                      "Rainfall",
                    ]}
                  />

                  <Area
                    type="monotone"
                    dataKey="rainfall"
                    stroke="#527CAA"
                    strokeWidth={2.5}
                    fill="url(#overviewRainfallFill)"
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="chart-empty">
                <CloudRain size={30} />
                <strong>No Assam-wide rainfall data available</strong>
                <span>The overview rainfall dataset could not be loaded.</span>
              </div>
            )}
          </div>
        </div>

        <div className="overview-landcover-card soft-card">
          <div className="card-heading">
            <div>
              <p>FLOODED LAND COVER</p>
              <h3>Flooded land cover</h3>
            </div>
            <Leaf size={21} />
          </div>

          <div className="overview-landcover-layout">
            <div className="overview-landcover-chart">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={landCover}
                    dataKey="area_km2"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={44}
                    outerRadius={66}
                    paddingAngle={2}
                  >
                    {landCover.map((item) => (
                      <Cell
                        key={item.name}
                        fill={
                          landCoverColors[item.name] || "#8BADD4"
                        }
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "#F7F2E8",
                      border: "1px solid rgba(113,37,43,0.15)",
                      borderRadius: "10px",
                      fontSize: "9px",
                    }}
                    formatter={(value) => [
                      `${Number(value).toFixed(2)} km²`,
                      "Flooded area",
                    ]}
                  />
                </PieChart>
              </ResponsiveContainer>

              <div className="overview-pie-center">
                <strong>{totalFloodedArea.toFixed(1)}</strong>
                <span>km² flooded</span>
              </div>
            </div>

            <div className="overview-landcover-legend">
              {landCover.map((item) => (
                <div
                  className="overview-landcover-item"
                  key={item.name}
                >
                  <span
                    style={{
                      backgroundColor:
                        landCoverColors[item.name] || "#8BADD4",
                    }}
                  ></span>
                  <div>
                    <strong>{item.name}</strong>
                    <small>
                      {Number(item.percentage ?? 0).toFixed(2)}%
                    </small>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}


/* =========================================================
   SNAPSHOT ITEM
========================================================= */

function SnapshotItem({
  icon: Icon,
  label,
  value,
}) {

  return (

    <div className="snapshot-item">

      <div className="snapshot-icon">

        <Icon size={22} />

      </div>


      <div className="snapshot-copy">

        <span>
          {label}
        </span>


        <strong>
          {value}
        </strong>

      </div>

    </div>

  );

}


/* =========================================================
   ASSAM MAP
========================================================= */

function AssamMap({
  geoJson,
  loading,
  error,
  districtData,
  onDistrictClick,
}) {

  const [
    baseMap,
    setBaseMap,
  ] = useState("map");

  function style(
    feature
  ) {

    const district =
      getFeatureDistrict(
        feature
      );


    if (
      isExcludedDistrict(
        district
      )
    ) {

      return {

        color:
          "transparent",

        weight:
          0,

        fillOpacity:
          0,

        opacity:
          0,

        interactive:
          false,

      };

    }


    const matchedDistrict =
      ANALYZED_DISTRICTS.find(
        (name) =>
          normalizeDistrict(
            name
          ) ===
          normalizeDistrict(
            district
          )
      );


    if (
      matchedDistrict &&
      districtData[
        matchedDistrict
      ]
    ) {

      const data =
        districtData[
          matchedDistrict
        ];


      return {

        color:
          "#71252B",

        weight:
          2.2,

        fillColor:
          getFloodColor(
            data.floodedPercent
          ),

        fillOpacity:
          0.71,

        opacity:
          1,

      };

    }


    return {

      color:
        "#81909A",

      weight:
        0.8,

      fillColor:
        "#DBE4E7",

      fillOpacity:
        0.23,

      opacity:
        0.8,

    };

  }


  function onEachFeature(
    feature,
    layer
  ) {

    const district =
      getFeatureDistrict(
        feature
      );


    if (
      isExcludedDistrict(
        district
      )
    ) {
      return;
    }


    const matchedDistrict =
      ANALYZED_DISTRICTS.find(
        (name) =>
          normalizeDistrict(
            name
          ) ===
          normalizeDistrict(
            district
          )
      );


    const analyzed =
      Boolean(
        matchedDistrict &&
        districtData[
          matchedDistrict
        ]
      );


    layer.bindTooltip(
      matchedDistrict ||
      district,
      {

        permanent:
          true,

        direction:
          "center",

        className:
          analyzed
            ? "district-map-label analyzed"
            : "district-map-label",

        opacity:
          1,

        interactive:
          false,

      }
    );


    if (!analyzed) {
      return;
    }


    const data =
      districtData[
        matchedDistrict
      ];


    layer.bindPopup(
      `
        <div class="map-popup">

          <strong>
            ${escapeHtml(
              matchedDistrict
            )}
          </strong>

          <span>
            Flooded area:
            ${data.floodedArea.toFixed(
              2
            )} km²
          </span>

          <span>
            Flood extent:
            ${data.floodedPercent.toFixed(
              2
            )}%
          </span>

          <span class="popup-action">
            Click to open district dashboard.
          </span>

        </div>
      `
    );


    layer.on({

      click:
        () =>
          onDistrictClick(
            matchedDistrict
          ),


      mouseover:
        (event) => {

          event.target.setStyle({

            weight:
              3.2,

            color:
              "#CAFFA6",

            fillOpacity:
              0.88,

          });


          event.target.bringToFront();

        },


      mouseout:
        (event) => {

          event.target.setStyle(
            style(
              feature
            )
          );

        },

    });

  }


  return (

    <div className="map-container-shell">

      {loading && (

        <div className="map-loading">

          <div className="loading-spinner"></div>


          <strong>
            Loading Assam map
          </strong>


          <span>
            Fetching district boundaries...
          </span>

        </div>

      )}


      {error && (

        <div className="map-error">

          <Map size={28} />


          <strong>
            Map boundary source unavailable
          </strong>


          <span>
            The dashboard data is ready,
            but the map boundary source
            could not be loaded.
          </span>

        </div>

      )}


      <MapContainer
        center={[
          26.20,
          93.05,
        ]}
        zoom={
          7
        }
        minZoom={
          6
        }
        maxZoom={
          11
        }
        scrollWheelZoom={
          true
        }
        zoomControl={
          true
        }
        className="leaflet-map"
      >

        <TileLayer
          attribution={
            baseMap === "map"
              ? "&copy; OpenStreetMap contributors"
              : "Tiles &copy; Esri"
          }
          url={
            baseMap === "map"
              ? OVERVIEW_MAP_URL
              : DISTRICT_MAP_URL
          }
        />


        {geoJson && (

          <>

            <GeoJSON
              data={
                geoJson
              }

              style={
                style
              }

              onEachFeature={
                onEachFeature
              }

            />


            <FitBounds
              geoJson={
                geoJson
              }

              extraZoom={
                0.7
              }

            />

          </>

        )}

      </MapContainer>


      <div className="map-basemap-toggle">
        <BaseMapToggle
          value={
            baseMap
          }
          onChange={
            setBaseMap
          }
        />
      </div>


      <div className="leaflet-overlay-card">

        <div>

          <span>
            WHOLE ASSAM
          </span>


          <strong>
            Analyzed flood event
          </strong>

        </div>


        <div className="overlay-pill">

          {Object.keys(
            districtData
          ).length}

          districts

        </div>

      </div>


      <div className="leaflet-scale-note">

        Background map • District labels always visible

      </div>

    </div>

  );

}


/* =========================================================
   DISTRICT DETAIL
========================================================= */

function DistrictDetailPage({
  district,
  data,
  geoJson,
  mapLoading,
  onBack,
}) {

  const {
    spatial,
    loading:
      spatialLoading,
    error:
      spatialError,
  } =
    useDistrictSpatialData(
      district
    );


  const {
    rainfallData,
    loading:
      rainfallLoading,
    error:
      rainfallError,
  } =
    useRainfallData(
      district
    );


  const [
    showFlood,
    setShowFlood,
  ] =
    useState(
      true
    );


  const [
    showBuildings,
    setShowBuildings,
  ] =
    useState(
      true
    );


  const [
    showRoads,
    setShowRoads,
  ] =
    useState(
      true
    );




  const [
    baseMap,
    setBaseMap,
  ] = useState("map");

  useEffect(() => {

    setShowFlood(
      true
    );

    setShowBuildings(
      true
    );

    setShowRoads(
      true
    );

  }, [district]);


  if (
    !district ||
    !data
  ) {

    return (

      <main className="page district-page">

        <div className="missing-district">

          <h2>
            District data unavailable
          </h2>


          <button
            className="district-primary-button"
            onClick={
              onBack
            }
          >

            <ArrowLeft size={17} />

            Back to Assam

          </button>

        </div>

      </main>

    );

  }


  const landCoverData = [

    {
      name:
        "Cropland",

      value:
        data.floodedCroplandShare,
    },

    {
      name:
        "Forest",

      value:
        data.floodedForestShare,
    },

    {
      name:
        "Other",

      value:
        data.floodedOtherShare,
    },

  ];


  const minimumRainfall =
    rainfallData.length
      ? Math.min(
          ...rainfallData.map(
            (
              item
            ) =>
              item.rainfall
          )
        )
      : null;

  const districtFloodReasons =
  DISTRICT_FLOOD_REASONS[district] || [];

  const floodImpact =
  getFloodImpactStatus(
    data.floodedPercent
  );

  const riskFactors = [

    {
      group:
        "HAZARD",

      label:
        "Flood Extent",

      value:
        `${data.floodedPercent.toFixed(
          2
        )}%`,

      detail:
        "Share of district area identified as flooded.",

      tone:
        "blue",

    },


    {
      group:
        "HAZARD",

      label:
        "Flood-period Rainfall",

      value:
        `${data.rainfall.toFixed(
          2
        )} mm`,

      detail:
        "Total rainfall during the analyzed event.",

      tone:
        "blue",

    },


    {
      group:
        "HAZARD",

      label:
        "Mean Elevation",

      value:
        `${data.meanElevation.toFixed(
          2
        )} m`,

      detail:
        "Mean elevation of the district.",

      tone:
        "blue",

    },


    {
      group:
        "HAZARD",

      label:
        "Mean Slope",

      value:
        `${data.meanSlope.toFixed(
          2
        )}°`,

      detail:
        "Mean terrain slope of the district.",

      tone:
        "blue",

    },


    {
      group:
        "EXPOSURE",

      label:
        "Flooded Cropland",

      value:
        `${data.floodedCropland.toFixed(
          2
        )} km²`,

      detail:
        `${data.croplandAffectedPercent.toFixed(
          2
        )}% of mapped cropland.`,

      tone:
        "green",

    },


    {
      group:
        "EXPOSURE",

      label:
        "Flooded Forest",

      value:
        `${data.floodedForest.toFixed(
          2
        )} km²`,

      detail:
        `${data.forestAffectedPercent.toFixed(
          2
        )}% of mapped forest.`,

      tone:
        "green",

    },


    {
      group:
        "EXPOSURE",

      label:
        "Buildings Affected",

      value:
        `${data.affectedBuildings}`,

      detail:
        `${data.buildingsAffectedPercent.toFixed(
          2
        )}% of mapped buildings.`,

      tone:
        "green",

    },


    {
      group:
        "EXPOSURE",

      label:
        "Road Network Affected",

      value:
        `${data.affectedRoadLength.toFixed(
          2
        )} km`,

      detail:
        `${data.roadAffectedPercent.toFixed(
          2
        )}% of mapped road length.`,

      tone:
        "green",

    },

  ];


  return (

    <main className="page district-page">


      {/* DISTRICT HEADER */}

      <section className="district-hero">

        <button
          className="district-back-button"
          onClick={
            onBack
          }
        >

          <ArrowLeft size={18} />

          Assam overview

        </button>


        <div className="district-hero-row">

          <div>

            <p className="district-label">
              DISTRICT ANALYSIS
            </p>


            <h2>
              {district}
            </h2>


            <p className="district-hero-description">

              July 2026 flood-event assessment
              using satellite-derived flood extent,
              rainfall, terrain and infrastructure
              information.

            </p>

          </div>


          <div
            className={`district-status-badge flood-impact-${floodImpact.className}`}
          >

           <span></span>

           <div>

            <small>
               FLOOD IMPACT
            </small>

            <strong>
              {floodImpact.label}
            </strong>

          </div>

         </div>

        </div>

      </section>


      {/* =================================================
          SIX TOP METRICS
      ================================================= */}

      <section className="district-metric-grid">

        <DistrictMetric
          icon={Droplets}
          label="Flooded Area"
          value={
            data.floodedArea.toFixed(
              2
            )
          }
          unit="km²"
          detail="Detected flood extent"
        />


        <DistrictMetric
          icon={Map}
          label="Flood Extent"
          value={
            data.floodedPercent.toFixed(
              2
            )
          }
          unit="%"
          detail="Share of district area"
        />


        <DistrictMetric
          icon={Leaf}
          label="Flooded Cropland"
          value={
            data.floodedCropland.toFixed(
              2
            )
          }
          unit="km²"
          detail={
            `${data.croplandAffectedPercent.toFixed(
              2
            )}% of cropland`
          }
        />


        <DistrictMetric
          icon={Trees}
          label="Flooded Forest"
          value={
            data.floodedForest.toFixed(
              2
            )
          }
          unit="km²"
          detail={
            `${data.forestAffectedPercent.toFixed(
              2
            )}% of forest`
          }
        />


        <DistrictMetric
          icon={Building2}
          label="Buildings Affected"
          value={
            data.affectedBuildings
          }
          unit=""
          detail={
            `${data.buildingsAffectedPercent.toFixed(
              2
            )}% of mapped buildings`
          }
        />


        <DistrictMetric
          icon={Route}
          label="Roads Affected"
          value={
            data.affectedRoadLength.toFixed(
              2
            )
          }
          unit="km"
          detail={
            `${data.roadAffectedPercent.toFixed(
              2
            )}% of mapped road length`
          }
        />

      </section>


      {/* =================================================
          MAP + RIGHT SIDE
      ================================================= */}

      <section className="district-main-grid">


        {/* MAP */}

        <div className="district-map-card panel">

          <div className="district-map-header">

            <div>

              <p>
                SPATIAL IMPACT
              </p>


              <h3>
                {district} flood map
              </h3>


              <span>
                Flood extent, affected buildings
                and affected road network.
              </span>

            </div>


            <div className="map-controls-and-legend">


              <div className="map-layer-controls">

                <LayerToggle
                  label="Flood"
                  icon={Droplets}
                  active={
                    showFlood
                  }
                  onClick={() =>
                    setShowFlood(
                      (value) =>
                        !value
                    )
                  }
                />


                <LayerToggle
                  label="Buildings"
                  icon={Building2}
                  active={
                    showBuildings
                  }
                  onClick={() =>
                    setShowBuildings(
                      (value) =>
                        !value
                    )
                  }
                />


                <LayerToggle
                  label="Roads"
                  icon={Route}
                  active={
                    showRoads
                  }
                  onClick={() =>
                    setShowRoads(
                      (value) =>
                        !value
                    )
                  }
                />

              </div>


              <div className="spatial-legend">

                <div>

                  <span className="legend-marker flood-marker"></span>

                  <span>
                    Flood extent
                  </span>

                </div>


                <div>

                  <span className="legend-marker building-marker"></span>

                  <span>
                    Affected buildings
                  </span>

                </div>


                <div>

                  <span className="legend-marker road-marker"></span>

                  <span>
                    Affected roads
                  </span>

                </div>


                <div>

                  <span className="legend-marker boundary-marker"></span>

                  <span>
                    District boundary
                  </span>

                </div>

              </div>

            </div>

          </div>


          <div className="district-map-wrapper">


            {(spatialLoading ||
              mapLoading) && (

              <div className="spatial-loading-overlay">

                <div className="loading-spinner"></div>


                <strong>
                  Loading spatial layers
                </strong>


                <span>
                  Preparing flood, building and
                  road data...
                </span>

              </div>

            )}


            {spatialError && (

              <div className="spatial-error-overlay">

                <Map size={27} />


                <strong>
                  Spatial layer loading issue
                </strong>


                <span>
                  {spatialError}
                </span>

              </div>

            )}


            <MapContainer
              key={
                district
              }

              center={[
                26.15,
                92.95,
              ]}

              zoom={
                8
              }

              scrollWheelZoom={
                true
              }

              zoomControl={
                true
              }

              className="leaflet-map district-leaflet-map"
            >


              {/* BACKGROUND BASEMAP */}

              <TileLayer
                attribution={
                  baseMap === "map"
                    ? "&copy; OpenStreetMap contributors"
                    : "Tiles &copy; Esri"
                }
                url={
                  baseMap === "map"
                    ? OVERVIEW_MAP_URL
                    : DISTRICT_MAP_URL
                }
              />


              {/* DISTRICT BOUNDARY */}

              {geoJson && (

                <>

                  <GeoJSON
                    data={
                      geoJson
                    }


                    style={(
                      feature
                    ) => {

                      const name =
                        getFeatureDistrict(
                          feature
                        );


                      if (
                        normalizeDistrict(
                          name
                        ) ===
                        normalizeDistrict(
                          district
                        )
                      ) {

                        return {

                          color:
                            "#601c22",

                          weight:
                            3.5,

                          fillColor:
                            "#71252B",

                          fillOpacity:
                            0.04,

                          opacity:
                            1,

                        };

                      }


                      return {

                        color:
                          "rgba(202,255,166,0.15)",

                        weight:
                          0.4,

                        fillOpacity:
                          0,

                      };

                    }}


                    onEachFeature={(
                      feature,
                      layer
                    ) => {

                      const name =
                        getFeatureDistrict(
                          feature
                        );


                      if (
                        normalizeDistrict(
                          name
                        ) ===
                        normalizeDistrict(
                          district
                        )
                      ) {

                        layer.bindTooltip(
                          district,
                          {

                            permanent:
                              true,

                            direction:
                              "center",

                            className:
                              "district-detail-label",

                            opacity:
                              1,

                            interactive:
                              false,

                          }
                        );

                      }

                    }}

                  />


                  <FitBounds
                    geoJson={
                      geoJson
                    }

                    districtName={
                      district
                    }

                    boundsOverride={
                      spatial.floodBounds
                    }

                  />

                </>

              )}


              {/* FLOOD RASTER */}

              {showFlood &&
                spatial.floodImage &&
                spatial.floodBounds && (

                  <ImageOverlay
                    url={
                      spatial.floodImage
                    }

                    bounds={
                      spatial.floodBounds
                    }

                    opacity={
                      0.95
                    }

                    className="flood-mask-layer"

                  />

                )}


              {/* BUILDINGS — PLUM */}

              {showBuildings &&
                spatial.buildings && (

                  <GeoJSON
                    data={
                      spatial.buildings
                    }


                    style={{

                      color:
                        "#CAFFA6",

                      weight:
                        1.2,

                      opacity:
                        1,

                      fillColor:
                        "#6f0009",

                      fillOpacity:
                        0.96,

                    }}


                    pointToLayer={(
                      feature,
                      latlng
                    ) =>
                      L.circleMarker(
                        latlng,
                        {

                          radius:
                            5.5,

                          color:
                            "#CAFFA6",

                          weight:
                            1.5,

                          fillColor:
                            "#71252B",

                          fillOpacity:
                            1,

                        }
                      )
                    }


                    onEachFeature={(
                      feature,
                      layer
                    ) => {

                      const properties =
                        feature.properties ||
                        {};


                      const buildingType =
                        getProperty(
                          properties,
                          [
                            "building",
                            "Building",
                            "type",
                          ]
                        );


                      const osmId =
                        getProperty(
                          properties,
                          [
                            "id",
                            "ID",
                            "osm_id",
                          ]
                        );


                      layer.bindPopup(
                        `
                          <div class="map-popup">

                            <strong>
                              Affected Building
                            </strong>

                            ${
                              buildingType
                                ? `<span>Type: ${escapeHtml(
                                    buildingType
                                  )}</span>`
                                : ""
                            }

                            ${
                              osmId
                                ? `<span>OSM ID: ${escapeHtml(
                                    osmId
                                  )}</span>`
                                : ""
                            }

                          </div>
                        `
                      );

                    }}

                  />

                )}


              {/* ROADS — BRIGHT BLUE */}

              {showRoads &&
                spatial.roads && (

                  <>

                    <GeoJSON
                      data={
                        spatial.roads
                      }

                      style={{

                        color:
                          "#CAFFA6",

                        weight:
                          7,

                        opacity:
                          0.9,

                      }}

                    />


                    <GeoJSON
                      data={
                        spatial.roads
                      }

                      style={{

                        color:
                          "#59BCE5",

                        weight:
                          4,

                        opacity:
                          1,

                      }}


                      onEachFeature={(
                        feature,
                        layer
                      ) => {

                        const properties =
                          feature.properties ||
                          {};


                        const highway =
                          getProperty(
                            properties,
                            [
                              "highway",
                              "Highway",
                            ]
                          );


                        const name =
                          getProperty(
                            properties,
                            [
                              "name",
                              "Name",
                            ]
                          );


                        const affectedLength =
                          getProperty(
                            properties,
                            [
                              "flooded_length_km",
                              "Flooded_length_km",
                              "flood_affected_length_km",
                            ]
                          );


                        const totalLength =
                          getProperty(
                            properties,
                            [
                              "length_km",
                              "Length_km",
                            ]
                          );


                        const length =
                          affectedLength ??
                          totalLength;


                        layer.bindPopup(
                          `
                            <div class="map-popup">

                              <strong>
                                Affected Road
                              </strong>

                              ${
                                highway
                                  ? `<span>Class: ${escapeHtml(
                                      highway
                                    )}</span>`
                                  : ""
                              }

                              ${
                                name
                                  ? `<span>Name: ${escapeHtml(
                                      name
                                    )}</span>`
                                  : ""
                              }

                              ${
                                length
                                  ? `<span>Length: ${Number(
                                      length
                                    ).toFixed(
                                      2
                                    )} km</span>`
                                  : ""
                              }

                            </div>
                          `
                        );

                      }}

                    />

                  </>

                )}

            </MapContainer>


            <div className="map-basemap-toggle district-basemap-toggle">
              <BaseMapToggle
                value={
                  baseMap
                }
                onChange={
                  setBaseMap
                }
              />
            </div>


            <div className="map-layer-status">

              <MapStatus
                label="FLOOD"
                visible={
                  showFlood
                }
                value={
                  showFlood
                    ? "ON"
                    : "OFF"
                }
              />


              <MapStatus
                label="BUILDINGS"
                visible={
                  showBuildings
                }
                value={
                  showBuildings
                    ? String(
                        data.affectedBuildings
                      )
                    : "OFF"
                }
              />


              <MapStatus
                label="ROADS"
                visible={
                  showRoads
                }
                value={
                  showRoads
                    ? String(
                        data.affectedRoadSegments
                      )
                    : "OFF"
                }
              />

            </div>

          </div>

        </div>


        {/* RIGHT SIDE */}

        <div className="district-side-column">


          {/* INFRASTRUCTURE */}

          <div className="district-infrastructure-card panel">

            <div className="district-card-heading">

              <div>

                <p>
                  DISTRICT INFRASTRUCTURE
                </p>


                <h3>
                  Exposure &amp; impact
                </h3>

              </div>


              <Building2
                size={22}
              />

            </div>


            <InfrastructureItem
              icon={Building2}
              label="BUILDINGS AFFECTED"
              value={
                data.affectedBuildings
              }
              detail={
                `${data.buildingsAffectedPercent.toFixed(
                  2
                )}% of mapped buildings`
              }
              tone="building"
            />


            <InfrastructureItem
              icon={Route}
              label="ROAD NETWORK AFFECTED"
              value={
                data.affectedRoadLength.toFixed(
                  2
                )
              }
              unit="km"
              detail={
                `${data.roadAffectedPercent.toFixed(
                  2
                )}% of mapped road length`
              }
              tone="road"
            />

          </div>


          {/* LAND COVER + TERRAIN */}

          <div className="district-profile-card panel">

            <div className="district-card-heading">

              <div>

                <p>
                  DISTRICT PROFILE
                </p>


                <h3>
                  Land cover &amp; terrain
                </h3>

              </div>


              <Trees size={22} />

            </div>


            <div className="mini-section-label">

              FLOODED LAND COVER

            </div>


            <div className="profile-pie-layout">


              <div className="profile-pie-chart">

                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >

                  <PieChart>

                    <Pie
                      data={
                        landCoverData
                      }

                      dataKey="value"

                      nameKey="name"

                      cx="50%"

                      cy="50%"

                      innerRadius={
                        45
                      }

                      outerRadius={
                        67
                      }

                      paddingAngle={
                        2
                      }

                    >

                      <Cell
                        fill="#D6AD49"
                      />

                      <Cell
                        fill="#79986B"
                      />

                      <Cell
                        fill="#8BADD4"
                      />

                    </Pie>


                    <Tooltip
                      contentStyle={{
                        background:
                          "#F7F2E8",

                        border:
                          "1px solid rgba(113,37,43,0.15)",

                        borderRadius:
                          "10px",

                        fontSize:
                          "9px",
                      }}

                      formatter={
                        (value) =>
                          [
                            `${Number(
                              value
                            ).toFixed(
                              2
                            )}%`,

                            "Share",
                          ]
                      }

                    />

                  </PieChart>

                </ResponsiveContainer>


                <div className="pie-center">

                  <strong>

                    {data.floodedArea.toFixed(
                      1
                    )}

                  </strong>


                  <span>
                    km² flooded
                  </span>

                </div>

              </div>


              <div className="landcover-legend">

                <LandCoverLegend
                  label="Cropland"
                  value={
                    data.floodedCroplandShare
                  }
                  color="#D6AD49"
                />


                <LandCoverLegend
                  label="Forest"
                  value={
                    data.floodedForestShare
                  }
                  color="#79986B"
                />


                <LandCoverLegend
                  label="Other"
                  value={
                    data.floodedOtherShare
                  }
                  color="#8BADD4"
                />

              </div>

            </div>


            <div className="profile-divider"></div>


            <div className="profile-terrain">

              <TerrainMini
                icon={Mountain}
                label="Elevation"
                value={
                  `${data.meanElevation.toFixed(
                    2
                  )} m`
                }
                detail={
                  `${data.minElevation.toFixed(
                    2
                  )}–${data.maxElevation.toFixed(
                    2
                  )} m`
                }
              />


              <TerrainMini
                icon={Navigation}
                label="Slope"
                value={
                  `${data.meanSlope.toFixed(
                    2
                  )}°`
                }
                detail={
                  `${data.minSlope.toFixed(
                    2
                  )}–${data.maxSlope.toFixed(
                    2
                  )}°`
                }
              />

            </div>

          </div>

        </div>

      </section>


      {/* =================================================
          EVENT RAINFALL + RAINFALL GRAPH
      ================================================= */}

      <section className="district-rainfall-section panel">


        <div className="district-rainfall-summary">

          <div>

            <p>
              EVENT RAINFALL
            </p>


            <h3>

              {data.rainfall.toFixed(
                2
              )}

              <span>
                mm
              </span>

            </h3>


            <span>
              Total rainfall during the analyzed
              flood period.
            </span>

          </div>


          <div className="mini-detail-grid">


            <div>

              <span>
                Minimum
              </span>


              <strong>

                {minimumRainfall !==
                null
                  ? `${minimumRainfall.toFixed(
                      2
                    )} mm`
                  : "—"}

              </strong>

            </div>


            <div>

              <span>
                Maximum
              </span>


              <strong>

                {data.maxDailyRainfall.toFixed(
                  2
                )}{" "}
                mm

              </strong>

            </div>


            <div>

              <span>
                Rainfall Days
              </span>


              <strong>
                {data.rainfallDays}
              </strong>

            </div>

          </div>

        </div>


        <div className="district-chart-heading">

          <div>

            <p>
              RAINFALL TIME SERIES
            </p>


            <h3>
              Daily rainfall during flood period
            </h3>


            <span>
              Daily rainfall observations for{" "}
              {district}.
            </span>

          </div>


          <CloudRain
            size={24}
          />

        </div>


        <div className="rainfall-chart-body">

          {rainfallLoading ? (

            <div className="chart-empty">

              <div className="loading-spinner"></div>


              <strong>
                Loading rainfall series
              </strong>

            </div>

          ) : rainfallError ? (

            <div className="chart-empty">

              <CloudRain size={28} />


              <strong>
                Rainfall graph unavailable
              </strong>


              <span>
                {rainfallError}
              </span>

            </div>

          ) : rainfallData.length === 0 ? (

            <div className="chart-empty">

              <CloudRain size={28} />


              <strong>
                No rainfall observations
              </strong>

            </div>

          ) : (

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <AreaChart
                data={
                  rainfallData
                }

                margin={{
                  top:
                    18,

                  right:
                    25,

                  left:
                    5,

                  bottom:
                    15,
                }}
              >

                <defs>

                  <linearGradient
                    id="rainfallFill"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >

                    <stop
                      offset="0%"
                      stopColor="#8BADD4"
                      stopOpacity={
                        0.82
                      }
                    />


                    <stop
                      offset="100%"
                      stopColor="#8BADD4"
                      stopOpacity={
                        0.09
                      }
                    />

                  </linearGradient>

                </defs>


                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="rgba(113,37,43,0.1)"
                />


                <XAxis
                  dataKey="date"
                  tick={{
                    fill:
                      "#71252B",

                    fontSize:
                      8,
                  }}

                  tickLine={
                    false
                  }
                />


                <YAxis
                  tick={{
                    fill:
                      "#71252B",

                    fontSize:
                      8,
                  }}

                  tickLine={
                    false
                  }
                />


                <Tooltip
                  contentStyle={{
                    background:
                      "#F7F2E8",

                    border:
                      "1px solid rgba(113,37,43,0.14)",

                    borderRadius:
                      "10px",

                    fontSize:
                      "9px",
                  }}

                  formatter={
                    (value) =>
                      [
                        `${Number(
                          value
                        ).toFixed(
                          2
                        )} mm`,

                        "Rainfall",
                      ]
                  }

                />


                <Area
                  type="monotone"

                  dataKey="rainfall"

                  stroke="#527CAA"

                  strokeWidth={
                    3
                  }

                  fill="url(#rainfallFill)"

                  dot={{
                    r:
                      3,

                    fill:
                      "#71252B",

                    stroke:
                      "#CAFFA6",

                    strokeWidth:
                      1.5,
                  }}

                  activeDot={{
                    r:
                      6,
                  }}

                />

              </AreaChart>

            </ResponsiveContainer>

          )}

        </div>

      </section>

           


      

      <section className="why-flooded-section panel">

        <div className="why-flooded-heading">

          <p>
            WHY IT FLOODED
          </p>

          <h3>
            What shaped the flood in {district}?
          </h3>

          <span>
            District-specific geographic and hydrological
            factors that help explain the observed July 2026
            flood footprint.
          </span>

        </div>


        <div className="why-flooded-grid">

          {districtFloodReasons.map(
            (reason, index) => (

              <div
                className="why-flooded-card"
                key={index}
              >

                <div className="why-flooded-number">
                  {String(index + 1).padStart(2, "0")}
                </div>

                <p>
                  {reason}
                </p>

              </div>

            )
          )}

        </div>


        <div className="why-flooded-note">

          <strong>
            Context note:
          </strong>{" "}

          These points provide geographic and hydrological
          context for the observed flood extent. They are
          not an official government flood-risk rating or
          a statistical causal model.

        </div>

      </section>


      {/* =================================================
          BOTTOM HAZARD + EXPOSURE
      ================================================= */}

      <section className="risk-profile-section"></section>

      {/* =================================================
          BOTTOM HAZARD + EXPOSURE
      ================================================= */}

      <section className="risk-profile-section">


        <div className="risk-profile-heading">

          <p>
            HAZARD &amp; EXPOSURE INDICATORS
          </p>


          <h3>
            What shapes the event impact?
          </h3>



        </div>


        <div className="risk-factor-columns">


          {/* HAZARD */}

          <div className="risk-factor-group">

            <div className="risk-group-title blue-title">

              <Waves size={15} />

              <span>
                HAZARD INDICATORS
              </span>

            </div>


            <div className="risk-factor-grid">

              {riskFactors
                .filter(
                  (
                    factor
                  ) =>
                    factor.group ===
                    "HAZARD"
                )
                .map(
                  (
                    factor
                  ) => (

                    <RiskFactorCard
                      key={
                        factor.label
                      }

                      {...factor}

                    />

                  )
                )}

            </div>

          </div>


          {/* EXPOSURE */}

          <div className="risk-factor-group">

            <div className="risk-group-title green-title">

              <Leaf size={15} />

              <span>
                EXPOSURE INDICATORS
              </span>

            </div>


            <div className="risk-factor-grid">

              {riskFactors
                .filter(
                  (
                    factor
                  ) =>
                    factor.group ===
                    "EXPOSURE"
                )
                .map(
                  (
                    factor
                  ) => (

                    <RiskFactorCard
                      key={
                        factor.label
                      }

                      {...factor}

                    />

                  )
                )}

            </div>

          </div>

        </div>


        <div className="risk-method-note">

          <span>
            Hazard = flood and terrain conditions
          </span>


          <span>
            Exposure = affected land and infrastructure
          </span>


          <strong>
            These indicators describe the analyzed
            event, not an official government risk rating.
          </strong>

        </div>

      </section>


      {/* RETURN */}

      <section className="district-next-card">

        <div>

          <p>
            BACK TO CONTEXT
          </p>


          <h3>
            Return to the Assam overview
          </h3>

        </div>


        <button
          onClick={
            onBack
          }
        >

          Return to Assam overview

          <ArrowRight
            size={17}
          />

        </button>

      </section>

    </main>

  );

}


/* =========================================================
   DISTRICT METRIC
========================================================= */

function DistrictMetric({
  icon: Icon,
  label,
  value,
  unit,
  detail,
}) {

  return (

    <div className="district-metric">

      <div className="district-metric-icon">

        <Icon size={22} />

      </div>


      <span>
        {label}
      </span>


      <strong>

        {value}

        {unit && (

          <small>
            {unit}
          </small>

        )}

      </strong>


      <p>
        {detail}
      </p>

    </div>

  );

}


/* =========================================================
   BASE MAP TOGGLE
========================================================= */

function BaseMapToggle({
  value,
  onChange,
}) {

  return (
    <div className="base-map-toggle">
      <button
        type="button"
        className={value === "map" ? "active" : ""}
        onClick={() => onChange("map")}
      >
        Map
      </button>

      <button
        type="button"
        className={value === "hybrid" ? "active" : ""}
        onClick={() => onChange("hybrid")}
      >
        Hybrid
      </button>
    </div>
  );
}


/* =========================================================
   LAYER TOGGLE
========================================================= */

function LayerToggle({
  label,
  icon: Icon,
  active,
  onClick,
}) {

  return (

    <button
      className={`map-layer-toggle ${
        active
          ? "active"
          : ""
      }`}
      onClick={
        onClick
      }
    >

      <Icon size={14} />


      <span>
        {label}
      </span>


      {active ? (

        <span className="toggle-check">

          <Check size={10} />

        </span>

      ) : (

        <span className="toggle-off">
          OFF
        </span>

      )}

    </button>

  );

}


/* =========================================================
   MAP STATUS
========================================================= */

function MapStatus({
  label,
  visible,
  value,
}) {

  return (

    <div
      className={`map-status ${
        visible
          ? "visible"
          : "hidden"
      }`}
    >

      <span>
        {label}
      </span>


      <strong>
        {value}
      </strong>

    </div>

  );

}


/* =========================================================
   INFRASTRUCTURE ITEM
========================================================= */

function InfrastructureItem({
  icon: Icon,
  label,
  value,
  unit = "",
  detail,
  tone,
}) {

  return (

    <div className="infrastructure-feature">

      <div
        className={`infrastructure-icon ${tone}`}
      >

        <Icon size={23} />

      </div>


      <div className="infrastructure-copy">

        <span>
          {label}
        </span>


        <strong>

          {value}

          {unit && (

            <em>
              {unit}
            </em>

          )}

        </strong>


        <small>
          {detail}
        </small>

      </div>

    </div>

  );

}


/* =========================================================
   LAND COVER LEGEND
========================================================= */

function LandCoverLegend({
  label,
  value,
  color,
}) {

  return (

    <div className="landcover-legend-item">

      <span
        style={{
          backgroundColor:
            color,
        }}
      ></span>


      <div>

        <strong>
          {label}
        </strong>


        <small>

          {Number(
            value
          ).toFixed(
            2
          )}%

        </small>

      </div>

    </div>

  );

}


/* =========================================================
   TERRAIN MINI
========================================================= */

function TerrainMini({
  icon: Icon,
  label,
  value,
  detail,
}) {

  return (

    <div className="terrain-mini">

      <div className="terrain-mini-icon">

        <Icon size={19} />

      </div>


      <div>

        <span>
          {label}
        </span>


        <strong>
          {value}
        </strong>


        <small>
          Range {detail}
        </small>

      </div>

    </div>

  );

}


/* =========================================================
   RISK FACTOR CARD
========================================================= */

function RiskFactorCard({
  label,
  value,
  detail,
  tone,
}) {

  return (

    <div
      className={`risk-factor-card ${
        tone
      }`}
    >

      <span className="risk-factor-label">

        {label}

      </span>


      <strong className="risk-factor-value">

        {value}

      </strong>


      <span className="risk-factor-detail">

        {detail}

      </span>

    </div>

  );

}


export default App;