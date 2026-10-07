"""
ASSAM FLOOD INTELLIGENCE
Neamatighat River Monitoring Pipeline

TARGET
------
Station : Neamatighat
River   : Brahmaputra
District: Jorhat
State   : Assam

SOURCE STRATEGY
---------------
1. CWC official flood bulletins / daily water-level reports
2. CWC station reference values
3. No Assam NWDP fallback for Neamatighat because the current
   Assam NWDP telemetry resource does not contain this station.

OUTPUTS
-------
Output/
└── river/
    ├── assam_river_timeseries.csv
    ├── assam_river_timeseries_recent.csv
    ├── assam_gauge_stations.csv
    ├── assam_current_river_levels.csv
    └── assam_river_thresholds.csv

Cache/
└── dashboard_data/
    └── river/
        ├── assam_gauges.json
        ├── assam_current_levels.json
        ├── assam_river_timeseries.json
        └── assam_river_dashboard.json

IMPORTANT
---------
No water level is fabricated.
No forecast is fabricated.
No trend is copied from unrelated sources.
If CWC data cannot be obtained, the script stops rather than
silently generating incorrect data.
"""

from __future__ import annotations

import io
import json
import re
import time
from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import requests

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(r"D:\PORTFOLIO PROJECT\Assam Flood")

OUTPUT_DIR = PROJECT_ROOT / "Output" / "river"
CACHE_DIR = PROJECT_ROOT / "Cache" / "dashboard_data" / "river"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. TARGET
# ============================================================

TARGET_STATION = "Neamatighat"
TARGET_RIVER = "Brahmaputra"
TARGET_DISTRICT = "Jorhat"
TARGET_STATE = "Assam"

TIMESERIES_DAYS = 30


# ============================================================
# 3. KNOWN CWC STATION REFERENCE
# ============================================================
#
# These are station-specific reference values reported by CWC.
#
# Neamatighat:
# Warning      = 84.54 m
# Danger       = 85.54 m
# HFL          = 87.37 m
#
# The HFL value is historical and is NOT a current observation.
#

STATION_REFERENCE = {
    "station": TARGET_STATION,
    "river": TARGET_RIVER,
    "district": TARGET_DISTRICT,
    "state": TARGET_STATE,
    "warning_level_m": 84.54,
    "danger_level_m": 85.54,
    "hfl_m": 87.37,
    "hfl_date": "11-07-1991",
}


# ============================================================
# 4. CWC URLs
# ============================================================

CWC_HOME = "https://cwc.gov.in"

# CWC flood forecasting / report pages.
# We query these pages instead of looping through unrelated NWDP
# telemetry resources.
CWC_FLOOD_FORECAST_URLS = [
    "https://cwc.gov.in/flood-forecast",
    "https://cwc.gov.in/flood-forecasting",
    "https://cwc.gov.in/flood-situation-report",
]


# ============================================================
# 5. HTTP SESSION
# ============================================================

SESSION = requests.Session()

SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/154.0 Safari/537.36"
        )
    }
)

REQUEST_TIMEOUT = 30


# ============================================================
# 6. LOGGING
# ============================================================

def log(message: str) -> None:
    print(f"[RIVER] {message}")


# ============================================================
# 7. NORMALIZATION HELPERS
# ============================================================

def normalize_text(value) -> str:
    if value is None:
        return ""

    value = str(value)

    value = (
        value.replace("\xa0", " ")
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_station(value: str) -> str:
    value = normalize_text(value).lower()

    value = value.replace(" ", "")
    value = value.replace("-", "")
    value = value.replace("_", "")

    return value


def normalize_river(value: str) -> str:
    value = normalize_text(value).lower()

    value = value.replace(" ", "")
    value = value.replace("-", "")
    value = value.replace("_", "")

    return value


# ============================================================
# 8. DOWNLOAD
# ============================================================

def download_url(url: str) -> bytes | None:

    try:
        log(f"Downloading: {url}")

        response = SESSION.get(
            url,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.content

    except Exception as exc:

        log(f"Download failed: {exc}")

        return None


# ============================================================
# 9. DISCOVER PDF LINKS FROM CWC PAGE
# ============================================================

def discover_cwc_pdf_links() -> list[str]:

    log("Searching official CWC pages for flood bulletin PDFs...")

    discovered = set()

    for page_url in CWC_FLOOD_FORECAST_URLS:

        try:

            response = SESSION.get(
                page_url,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                continue

            html = response.text

            links = re.findall(
                r'href=["\']([^"\']+\.pdf[^"\']*)["\']',
                html,
                flags=re.IGNORECASE,
            )

            for link in links:

                link = link.strip()

                if link.startswith("/"):
                    link = CWC_HOME + link

                elif link.startswith("./"):
                    link = CWC_HOME + "/" + link[2:]

                elif not link.startswith("http"):
                    link = CWC_HOME + "/" + link.lstrip("/")

                discovered.add(link)

        except Exception as exc:

            log(f"Could not read {page_url}: {exc}")

    links = sorted(discovered)

    log(f"Discovered {len(links)} PDF links.")

    return links


# ============================================================
# 10. SEARCH CWC SITE DIRECTLY
# ============================================================

def search_cwc_for_neamatighat() -> list[str]:

    """
    Uses CWC's website search endpoint if available.

    This is intentionally conservative.
    We only retain URLs that look like CWC PDFs/pages.
    """

    urls = []

    search_urls = [
        (
            "https://cwc.gov.in/search/node"
            "?keys=Neamatighat"
        ),
        (
            "https://cwc.gov.in/search"
            "?search_api_fulltext=Neamatighat"
        ),
    ]

    for url in search_urls:

        try:

            response = SESSION.get(
                url,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                continue

            html = response.text

            found = re.findall(
                r'href=["\']([^"\']+)["\']',
                html,
                flags=re.IGNORECASE,
            )

            for item in found:

                item = item.strip()

                if (
                    "cwc.gov.in" in item
                    and (
                        ".pdf" in item.lower()
                        or "flood" in item.lower()
                    )
                ):
                    urls.append(item)

        except Exception:
            pass

    return list(dict.fromkeys(urls))


# ============================================================
# 11. PDF TEXT EXTRACTION
# ============================================================

def extract_pdf_text(pdf_bytes: bytes) -> str:

    if pdfplumber is None:

        raise RuntimeError(
            "pdfplumber is not installed.\n"
            "Run:\n"
            "pip install pdfplumber"
        )

    text_parts = []

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:

        for page in pdf.pages:

            try:
                text = page.extract_text()

                if text:
                    text_parts.append(text)

            except Exception:
                continue

    return "\n".join(text_parts)


# ============================================================
# 12. FIND NEAMATIGHAT IN PDF
# ============================================================

def extract_neamatighat_records(
    pdf_text: str,
    source_url: str,
) -> list[dict]:

    """
    Extracts CWC rows containing Neamatighat.

    CWC PDFs vary slightly in formatting, so this function uses
    multiple patterns rather than assuming one fixed table layout.
    """

    records = []

    clean = normalize_text(pdf_text)

    # --------------------------------------------------------
    # Pattern A:
    #
    # Brahmaputra JORHAT
    # 84.54 85.54 87.37
    # 84.63 ...
    # Neamatighat
    # Assam
    #
    # --------------------------------------------------------

    pattern_a = re.compile(
        r"""
        Brahmaputra
        .*?
        JORHAT
        .*?
        (?P<warning>\d{2,3}\.\d{1,3})
        \s+
        (?P<danger>\d{2,3}\.\d{1,3})
        \s+
        (?P<hfl>\d{2,3}\.\d{1,3})
        .*?
        (?P<actual>\d{2,3}\.\d{1,3})
        .*?
        Neamatighat
        .*?
        (?:Assam)?
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    match = pattern_a.search(clean)

    if match:

        try:

            records.append(
                {
                    "station": TARGET_STATION,
                    "river": TARGET_RIVER,
                    "district": TARGET_DISTRICT,
                    "state": TARGET_STATE,
                    "warning_level_m": float(
                        match.group("warning")
                    ),
                    "danger_level_m": float(
                        match.group("danger")
                    ),
                    "hfl_m": float(
                        match.group("hfl")
                    ),
                    "water_level_m": float(
                        match.group("actual")
                    ),
                    "source": "CWC",
                    "source_url": source_url,
                }
            )

        except Exception:
            pass

    # --------------------------------------------------------
    # Pattern B:
    #
    # Search around the literal station name.
    #
    # This handles PDF extraction where table columns become
    # rearranged.
    # --------------------------------------------------------

    if not records:

        station_matches = list(
            re.finditer(
                r"Neamatighat",
                clean,
                flags=re.IGNORECASE,
            )
        )

        for match in station_matches:

            start = max(
                0,
                match.start() - 800,
            )

            end = min(
                len(clean),
                match.end() + 800,
            )

            block = clean[start:end]

            numbers = re.findall(
                r"\b\d{2,3}\.\d{1,3}\b",
                block,
            )

            numbers = [
                float(x)
                for x in numbers
            ]

            # Known threshold values are used ONLY as a
            # validation anchor, not fabricated observations.
            #
            # We look for an actual value in the nearby block.

            for value in numbers:

                if (
                    70 <= value <= 100
                    and abs(value - 84.54) > 0.001
                    and abs(value - 85.54) > 0.001
                    and abs(value - 87.37) > 0.001
                ):

                    records.append(
                        {
                            "station": TARGET_STATION,
                            "river": TARGET_RIVER,
                            "district": TARGET_DISTRICT,
                            "state": TARGET_STATE,
                            "warning_level_m": 84.54,
                            "danger_level_m": 85.54,
                            "hfl_m": 87.37,
                            "water_level_m": value,
                            "source": "CWC",
                            "source_url": source_url,
                        }
                    )

                    break

    return records


# ============================================================
# 13. EXTRACT DATE/TIME FROM PDF
# ============================================================

def extract_datetime_from_text(
    pdf_text: str,
) -> datetime | None:

    clean = normalize_text(pdf_text)

    patterns = [

        # 29-09-2026 08:00
        r"(\d{2})[-/](\d{2})[-/](\d{4}).{0,30}?(\d{1,2}):(\d{2})",

        # 29/09/2026 08:00
        r"(\d{2})/(\d{2})/(\d{4}).{0,30}?(\d{1,2}):(\d{2})",

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            clean,
        )

        if not match:
            continue

        try:

            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))

            hour = int(match.group(4))
            minute = int(match.group(5))

            return datetime(
                year,
                month,
                day,
                hour,
                minute,
            )

        except Exception:
            continue

    return None


# ============================================================
# 14. TREND
# ============================================================

def calculate_trend(
    previous_level: float | None,
    current_level: float | None,
) -> str:

    if (
        previous_level is None
        or current_level is None
    ):
        return "Unknown"

    difference = (
        current_level
        - previous_level
    )

    if difference > 0.01:
        return "Rising"

    if difference < -0.01:
        return "Falling"

    return "Steady"


# ============================================================
# 15. STATUS
# ============================================================

def calculate_status(
    water_level: float,
    warning: float | None,
    danger: float | None,
    hfl: float | None,
) -> str:

    if (
        hfl is not None
        and water_level >= hfl
    ):
        return "Above HFL"

    if (
        danger is not None
        and water_level >= danger
    ):
        return "Above Danger"

    if (
        warning is not None
        and water_level >= warning
    ):
        return "Above Warning"

    if warning is not None:
        return "Below Warning"

    return "No threshold reference"


# ============================================================
# 16. BUILD OBSERVATION RECORD
# ============================================================

def build_observation(
    record: dict,
    observation_datetime: datetime,
    previous_level: float | None,
) -> dict:

    water_level = float(
        record["water_level_m"]
    )

    warning = record.get(
        "warning_level_m"
    )

    danger = record.get(
        "danger_level_m"
    )

    hfl = record.get(
        "hfl_m"
    )

    trend = calculate_trend(
        previous_level,
        water_level,
    )

    status = calculate_status(
        water_level,
        warning,
        danger,
        hfl,
    )

    difference_warning = None
    difference_danger = None
    difference_hfl = None

    if warning is not None:
        difference_warning = (
            water_level - warning
        )

    if danger is not None:
        difference_danger = (
            water_level - danger
        )

    if hfl is not None:
        difference_hfl = (
            water_level - hfl
        )

    return {
        "date": observation_datetime.strftime(
            "%Y-%m-%d"
        ),

        "time": observation_datetime.strftime(
            "%H:%M"
        ),

        "datetime": observation_datetime.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "station": TARGET_STATION,

        "river": TARGET_RIVER,

        "district": TARGET_DISTRICT,

        "state": TARGET_STATE,

        "latitude": None,

        "longitude": None,

        "water_level_m": water_level,

        "trend": trend,

        "status": status,

        "warning_level_m": warning,

        "danger_level_m": danger,

        "hfl_m": hfl,

        "difference_from_warning_m":
            difference_warning,

        "difference_from_danger_m":
            difference_danger,

        "difference_from_hfl_m":
            difference_hfl,

        "source": "CWC",

        "source_url":
            record.get("source_url"),
    }


# ============================================================
# 17. FALLBACK: USE KNOWN CURRENT REPORT DATA
# ============================================================

def parse_current_from_cwc_page(
    text: str,
) -> list[dict]:

    """
    Searches arbitrary CWC-derived page text for a Neamatighat
    observation.

    This is deliberately conservative.
    """

    records = []

    clean = normalize_text(text)

    if (
        "Neamatighat" not in clean
        and "NEAMATIGHAT" not in clean
    ):
        return records

    # Look around the station.
    matches = list(
        re.finditer(
            r"Neamatighat",
            clean,
            flags=re.IGNORECASE,
        )
    )

    for match in matches:

        block = clean[
            max(0, match.start() - 500):
            min(len(clean), match.end() + 500)
        ]

        # Find water-level-like numbers.
        numbers = re.findall(
            r"\b\d{2,3}\.\d{1,3}\b",
            block,
        )

        candidates = []

        for number in numbers:

            value = float(number)

            if 70 <= value <= 100:
                candidates.append(value)

        # Remove known threshold/reference values.
        candidates = [
            x
            for x in candidates
            if abs(x - 84.54) > 0.001
            and abs(x - 85.54) > 0.001
            and abs(x - 87.37) > 0.001
        ]

        if candidates:

            records.append(
                {
                    "station": TARGET_STATION,
                    "river": TARGET_RIVER,
                    "district": TARGET_DISTRICT,
                    "state": TARGET_STATE,
                    "warning_level_m": 84.54,
                    "danger_level_m": 85.54,
                    "hfl_m": 87.37,
                    "water_level_m": candidates[0],
                    "source": "CWC",
                }
            )

            break

    return records


# ============================================================
# 18. COLLECT CWC DATA
# ============================================================

def collect_cwc_data() -> list[dict]:

    log("")
    log("================================================")
    log("CWC NEAMATIGHAT DATA COLLECTION")
    log("================================================")

    if pdfplumber is None:

        log(
            "pdfplumber is not installed."
        )

        log(
            "Install it with:"
        )

        log(
            "pip install pdfplumber"
        )

        raise RuntimeError(
            "pdfplumber is required."
        )

    pdf_links = discover_cwc_pdf_links()

    # Search endpoint as an additional source of links.
    search_links = (
        search_cwc_for_neamatighat()
    )

    pdf_links.extend(search_links)

    pdf_links = list(
        dict.fromkeys(pdf_links)
    )

    # --------------------------------------------------------
    # Only inspect a reasonable number of recent PDFs.
    #
    # NEVER loop through unrelated NWDP resources.
    # --------------------------------------------------------

    pdf_links = pdf_links[-100:]

    log(
        f"Checking {len(pdf_links)} CWC bulletin PDFs..."
    )

    all_records = []

    for index, pdf_url in enumerate(
        pdf_links,
        start=1,
    ):

        log(
            f"[{index}/{len(pdf_links)}] "
            f"Checking CWC bulletin..."
        )

        pdf_bytes = download_url(
            pdf_url
        )

        if not pdf_bytes:
            continue

        try:

            text = extract_pdf_text(
                pdf_bytes
            )

        except Exception as exc:

            log(
                f"PDF extraction failed: {exc}"
            )

            continue

        if (
            "Neamatighat" not in text
            and "NEAMATIGHAT" not in text
        ):
            continue

        log(
            "Found Neamatighat in CWC bulletin."
        )

        records = (
            extract_neamatighat_records(
                text,
                pdf_url,
            )
        )

        observation_datetime = (
            extract_datetime_from_text(
                text
            )
        )

        for record in records:

            record[
                "observation_datetime"
            ] = observation_datetime

        all_records.extend(
            records
        )

        # Once we have a valid recent bulletin,
        # continue checking a few more to build a
        # useful time series.
        if len(all_records) >= 10:
            break

        time.sleep(0.25)

    return all_records


# ============================================================
# 19. BUILD DATAFRAME
# ============================================================

def build_dataframe(
    raw_records: list[dict],
) -> pd.DataFrame:

    rows = []

    for record in raw_records:

        dt = record.get(
            "observation_datetime"
        )

        if dt is None:
            continue

        if record.get(
            "water_level_m"
        ) is None:
            continue

        rows.append(
            {
                "datetime": dt,

                "date": dt.strftime(
                    "%Y-%m-%d"
                ),

                "time": dt.strftime(
                    "%H:%M"
                ),

                "station":
                    TARGET_STATION,

                "river":
                    TARGET_RIVER,

                "district":
                    TARGET_DISTRICT,

                "state":
                    TARGET_STATE,

                "water_level_m":
                    float(
                        record[
                            "water_level_m"
                        ]
                    ),

                "warning_level_m":
                    float(
                        record.get(
                            "warning_level_m",
                            84.54,
                        )
                    ),

                "danger_level_m":
                    float(
                        record.get(
                            "danger_level_m",
                            85.54,
                        )
                    ),

                "hfl_m":
                    float(
                        record.get(
                            "hfl_m",
                            87.37,
                        )
                    ),

                "source":
                    "CWC",

                "source_url":
                    record.get(
                        "source_url"
                    ),
            }
        )

    if not rows:

        return pd.DataFrame()

    df = pd.DataFrame(rows)

    df = df.sort_values(
        "datetime"
    )

    df = df.drop_duplicates(
        subset=[
            "station",
            "river",
            "datetime",
        ],
        keep="last",
    )

    # --------------------------------------------------------
    # Trend
    # --------------------------------------------------------

    df["trend"] = "Unknown"

    for i in range(
        1,
        len(df),
    ):

        previous = float(
            df.iloc[
                i - 1
            ]["water_level_m"]
        )

        current = float(
            df.iloc[
                i
            ]["water_level_m"]
        )

        df.loc[
            df.index[i],
            "trend"
        ] = calculate_trend(
            previous,
            current,
        )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    df["status"] = df.apply(
        lambda row:
            calculate_status(
                row["water_level_m"],
                row["warning_level_m"],
                row["danger_level_m"],
                row["hfl_m"],
            ),
        axis=1,
    )

    df[
        "difference_from_warning_m"
    ] = (
        df["water_level_m"]
        - df["warning_level_m"]
    )

    df[
        "difference_from_danger_m"
    ] = (
        df["water_level_m"]
        - df["danger_level_m"]
    )

    df[
        "difference_from_hfl_m"
    ] = (
        df["water_level_m"]
        - df["hfl_m"]
    )

    return df


# ============================================================
# 20. SAVE TIME SERIES
# ============================================================

def save_timeseries(
    df: pd.DataFrame,
) -> None:

    if df.empty:
        return

    output = df.copy()

    output["datetime"] = (
        output["datetime"]
        .dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    path = (
        OUTPUT_DIR
        / "assam_river_timeseries.csv"
    )

    output.to_csv(
        path,
        index=False,
    )

    log(
        f"Saved: {path}"
    )

    # --------------------------------------------------------
    # Recent 30 days
    # --------------------------------------------------------

    latest = df["datetime"].max()

    cutoff = (
        latest
        - timedelta(
            days=TIMESERIES_DAYS
        )
    )

    recent = df[
        df["datetime"] >= cutoff
    ].copy()

    recent["datetime"] = (
        recent["datetime"]
        .dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    recent_path = (
        OUTPUT_DIR
        / "assam_river_timeseries_recent.csv"
    )

    recent.to_csv(
        recent_path,
        index=False,
    )

    log(
        f"Saved: {recent_path}"
    )


# ============================================================
# 21. CURRENT LEVEL
# ============================================================

def build_current_level(
    df: pd.DataFrame,
) -> dict:

    latest = df.iloc[-1]

    return {
        "station":
            TARGET_STATION,

        "river":
            TARGET_RIVER,

        "district":
            TARGET_DISTRICT,

        "state":
            TARGET_STATE,

        "water_level_m":
            float(
                latest[
                    "water_level_m"
                ]
            ),

        "date":
            latest[
                "date"
            ],

        "time":
            latest[
                "time"
            ],

        "datetime":
            latest[
                "datetime"
            ].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "trend":
            latest[
                "trend"
            ],

        "status":
            latest[
                "status"
            ],

        "warning_level_m":
            float(
                latest[
                    "warning_level_m"
                ]
            ),

        "danger_level_m":
            float(
                latest[
                    "danger_level_m"
                ]
            ),

        "hfl_m":
            float(
                latest[
                    "hfl_m"
                ]
            ),

        "difference_from_warning_m":
            float(
                latest[
                    "difference_from_warning_m"
                ]
            ),

        "difference_from_danger_m":
            float(
                latest[
                    "difference_from_danger_m"
                ]
            ),

        "difference_from_hfl_m":
            float(
                latest[
                    "difference_from_hfl_m"
                ]
            ),

        "source":
            "CWC",
    }


# ============================================================
# 22. GAUGE INVENTORY
# ============================================================

def build_gauge_inventory(
    df: pd.DataFrame,
) -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "station":
                    TARGET_STATION,

                "river":
                    TARGET_RIVER,

                "district":
                    TARGET_DISTRICT,

                "state":
                    TARGET_STATE,

                "latitude":
                    None,

                "longitude":
                    None,

                "source":
                    "CWC",
            }
        ]
    )


# ============================================================
# 23. THRESHOLD TABLE
# ============================================================

def build_threshold_table() -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "station":
                    TARGET_STATION,

                "river":
                    TARGET_RIVER,

                "district":
                    TARGET_DISTRICT,

                "state":
                    TARGET_STATE,

                "warning_level_m":
                    84.54,

                "danger_level_m":
                    85.54,

                "hfl_m":
                    87.37,

                "hfl_date":
                    "11-07-1991",

                "source":
                    "CWC",
            }
        ]
    )


# ============================================================
# 24. SAVE INVENTORY + THRESHOLDS
# ============================================================

def save_reference_outputs(
    df: pd.DataFrame,
) -> None:

    inventory = (
        build_gauge_inventory(
            df
        )
    )

    inventory_path = (
        OUTPUT_DIR
        / "assam_gauge_stations.csv"
    )

    inventory.to_csv(
        inventory_path,
        index=False,
    )

    thresholds = (
        build_threshold_table()
    )

    thresholds_path = (
        OUTPUT_DIR
        / "assam_river_thresholds.csv"
    )

    thresholds.to_csv(
        thresholds_path,
        index=False,
    )

    log(
        f"Saved: {inventory_path}"
    )

    log(
        f"Saved: {thresholds_path}"
    )


# ============================================================
# 25. SAVE CURRENT LEVEL
# ============================================================

def save_current_level(
    current: dict,
) -> None:

    current_df = pd.DataFrame(
        [current]
    )

    path = (
        OUTPUT_DIR
        / "assam_current_river_levels.csv"
    )

    current_df.to_csv(
        path,
        index=False,
    )

    log(
        f"Saved: {path}"
    )


# ============================================================
# 26. JSON SERIALIZATION
# ============================================================

def save_json(
    data,
    path: Path,
) -> None:

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    log(
        f"Saved: {path}"
    )


# ============================================================
# 27. BUILD DASHBOARD JSON
# ============================================================

def build_dashboard_json(
    df: pd.DataFrame,
    current: dict,
) -> None:

    # --------------------------------------------------------
    # Recent 30-day series
    # --------------------------------------------------------

    latest_dt = df[
        "datetime"
    ].max()

    cutoff = (
        latest_dt
        - timedelta(
            days=TIMESERIES_DAYS
        )
    )

    recent = df[
        df["datetime"] >= cutoff
    ].copy()

    series = []

    for _, row in recent.iterrows():

        series.append(
            {
                "date":
                    row[
                        "date"
                    ],

                "time":
                    row[
                        "time"
                    ],

                "datetime":
                    row[
                        "datetime"
                    ].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "water_level_m":
                    float(
                        row[
                            "water_level_m"
                        ]
                    ),
            }
        )

    # --------------------------------------------------------
    # Gauge
    # --------------------------------------------------------

    gauge = {
        "station":
            TARGET_STATION,

        "river":
            TARGET_RIVER,

        "district":
            TARGET_DISTRICT,

        "state":
            TARGET_STATE,

        "latitude":
            None,

        "longitude":
            None,

        "source":
            "CWC",

        "warning_level_m":
            84.54,

        "danger_level_m":
            85.54,

        "hfl_m":
            87.37,

        "hfl_date":
            "11-07-1991",
    }

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    dashboard = {
        "project":
            "Assam Flood Intelligence",

        "updated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "source":
            "Central Water Commission",

        "stations": [
            {
                "gauge":
                    gauge,

                "current":
                    current,

                "timeseries":
                    series,
            }
        ],
    }

    # --------------------------------------------------------
    # Separate JSON files
    # --------------------------------------------------------

    save_json(
        [gauge],
        CACHE_DIR
        / "assam_gauges.json",
    )

    save_json(
        [current],
        CACHE_DIR
        / "assam_current_levels.json",
    )

    save_json(
        {
            "station":
                TARGET_STATION,

            "river":
                TARGET_RIVER,

            "timeseries":
                series,
        },
        CACHE_DIR
        / "assam_river_timeseries.json",
    )

    save_json(
        dashboard,
        CACHE_DIR
        / "assam_river_dashboard.json",
    )


# ============================================================
# 28. MAIN
# ============================================================

def main():

    log("")
    log(
        "================================================"
    )

    log(
        "Starting Neamatighat river monitoring pipeline..."
    )

    log(
        "================================================"
    )

    log(
        f"Target station : {TARGET_STATION}"
    )

    log(
        f"Target river   : {TARGET_RIVER}"
    )

    log(
        f"Target district: {TARGET_DISTRICT}"
    )

    log(
        f"Target state   : {TARGET_STATE}"
    )

    log("")
    log(
        "IMPORTANT: Assam NWDP telemetry is NOT being used "
        "for this station."
    )

    log(
        "Source: Central Water Commission flood bulletins."
    )

    # --------------------------------------------------------
    # Collect
    # --------------------------------------------------------

    raw_records = (
        collect_cwc_data()
    )

    if not raw_records:

        log("")
        log(
            "================================================"
        )

        log(
            "NO NEAMATIGHAT OBSERVATION FOUND"
        )

        log(
            "================================================"
        )

        log(
            "The CWC website did not expose a directly "
            "downloadable bulletin through the discovered pages."
        )

        log(
            "No fake water-level data will be generated."
        )

        return

    # --------------------------------------------------------
    # Dataframe
    # --------------------------------------------------------

    df = build_dataframe(
        raw_records
    )

    if df.empty:

        log(
            "No valid observations after parsing."
        )

        return

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    log("")
    log(
        "================================================"
    )

    log(
        "NEAMATIGHAT DATA FOUND"
    )

    log(
        "================================================"
    )

    log(
        f"Records: {len(df)}"
    )

    log(
        f"First : {df['datetime'].min()}"
    )

    log(
        f"Latest: {df['datetime'].max()}"
    )

    latest = df.iloc[-1]

    log(
        f"Latest water level: "
        f"{latest['water_level_m']:.3f} m"
    )

    log(
        f"Trend: {latest['trend']}"
    )

    log(
        f"Status: {latest['status']}"
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    save_timeseries(
        df
    )

    save_reference_outputs(
        df
    )

    current = build_current_level(
        df
    )

    save_current_level(
        current
    )

    build_dashboard_json(
        df,
        current,
    )

    log("")
    log(
        "================================================"
    )

    log(
        "RIVER PIPELINE COMPLETE"
    )

    log(
        "================================================"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()