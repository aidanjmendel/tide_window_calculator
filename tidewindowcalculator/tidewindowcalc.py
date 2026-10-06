from datetime import datetime, timedelta
import math
import sqlite3
import altair as alt
import folium
import numpy as np
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# -------------------------------------------------------------------
# Comprehensive List of Major NOAA Tide Stations (US West, East, Gulf, HI, AK)
# -------------------------------------------------------------------
NOAA_STATIONS = [
    # --- WEST COAST (CA, OR, WA) ---
    {"id": "9410170", "name": "San Diego Bay, CA", "lat": 32.7142, "lng": -117.1736},
    {"id": "9410230", "name": "La Jolla, CA", "lat": 32.8669, "lng": -117.2571},
    {"id": "9410580", "name": "Newport Beach, CA", "lat": 33.6033, "lng": -117.8833},
    {"id": "9410660", "name": "Los Angeles, CA", "lat": 33.7200, "lng": -118.2717},
    {"id": "9410840", "name": "Santa Monica, CA", "lat": 34.0083, "lng": -118.4983},
    {"id": "9411340", "name": "Santa Barbara, CA", "lat": 34.4083, "lng": -119.6850},
    {"id": "9412110", "name": "Port San Luis, CA", "lat": 35.1767, "lng": -120.7600},
    {"id": "9413450", "name": "Monterey, CA", "lat": 36.6050, "lng": -121.8883},
    {"id": "9414290", "name": "San Francisco, CA", "lat": 37.8067, "lng": -122.4650},
    {"id": "9415144", "name": "Port Reyes, CA", "lat": 37.9950, "lng": -122.9750},
    {"id": "9418767", "name": "Humboldt Bay, CA", "lat": 40.7667, "lng": -124.2167},
    {"id": "9432780", "name": "Charleston, OR", "lat": 43.3450, "lng": -124.3217},
    {"id": "9435380", "name": "South Beach, OR", "lat": 44.6250, "lng": -124.0433},
    {"id": "9439040", "name": "Astoria, OR", "lat": 46.2067, "lng": -123.7683},
    {"id": "9440581", "name": "Cape Disappointment, WA", "lat": 46.2783, "lng": -124.0533},
    {"id": "9443090", "name": "Neah Bay, WA", "lat": 48.3700, "lng": -124.6117},
    {"id": "9447130", "name": "Seattle, WA", "lat": 47.6017, "lng": -122.3383},

    # --- EAST COAST (ME to FL) ---
    {"id": "8418150", "name": "Portland, ME", "lat": 43.6567, "lng": -70.2467},
    {"id": "8443970", "name": "Boston, MA", "lat": 42.3550, "lng": -71.0500},
    {"id": "8452660", "name": "Newport, RI", "lat": 41.5050, "lng": -71.3267},
    {"id": "8467150", "name": "Bridgeport, CT", "lat": 41.1733, "lng": -73.1817},
    {"id": "8518750", "name": "The Battery, NYC, NY", "lat": 40.7006, "lng": -74.0142},
    {"id": "8531680", "name": "Sandy Hook, NJ", "lat": 40.4667, "lng": -74.0083},
    {"id": "8534720", "name": "Atlantic City, NJ", "lat": 39.3550, "lng": -74.4183},
    {"id": "8557380", "name": "Lewes, DE", "lat": 38.7817, "lng": -75.1200},
    {"id": "8570283", "name": "Ocean City Inlet, MD", "lat": 38.3283, "lng": -75.0917},
    {"id": "8638863", "name": "Chesapeake Bay Bridge, VA", "lat": 36.9667, "lng": -76.1133},
    {"id": "8651370", "name": "Duck, NC", "lat": 36.1833, "lng": -75.7467},
    {"id": "8658120", "name": "Wilmington, NC", "lat": 34.2267, "lng": -77.9533},
    {"id": "8665530", "name": "Charleston, SC", "lat": 32.7817, "lng": -79.9250},
    {"id": "8670870", "name": "Fort Pulaski, GA", "lat": 32.0333, "lng": -80.9017},
    {"id": "8720030", "name": "Fernandina Beach, FL", "lat": 30.6717, "lng": -81.4650},
    {"id": "8720218", "name": "Mayport, FL", "lat": 30.3967, "lng": -81.4300},
    {"id": "8721604", "name": "Trident Pier, Cape Canaveral, FL", "lat": 28.4150, "lng": -80.5933},
    {"id": "8722670", "name": "Lake Worth Pier, FL", "lat": 26.6133, "lng": -80.0333},
    {"id": "8723214", "name": "Virginia Key, Miami, FL", "lat": 25.7317, "lng": -80.1617},
    {"id": "8724580", "name": "Key West, FL", "lat": 24.5550, "lng": -81.8067},

    # --- GULF COAST ---
    {"id": "8725110", "name": "Naples, FL", "lat": 26.1317, "lng": -81.8083},
    {"id": "8726520", "name": "St. Petersburg, FL", "lat": 27.7600, "lng": -82.6267},
    {"id": "8729840", "name": "Pensacola, FL", "lat": 30.4050, "lng": -87.2117},
    {"id": "8737048", "name": "Mobile State Docks, AL", "lat": 30.7050, "lng": -88.0433},
    {"id": "8761724", "name": "Grand Isle, LA", "lat": 29.2633, "lng": -89.9567},
    {"id": "8770613", "name": "Morgans Point, TX", "lat": 29.6817, "lng": -95.0150},
    {"id": "8771450", "name": "Galveston Pier 21, TX", "lat": 29.3100, "lng": -94.7933},
    {"id": "8775870", "name": "Corpus Christi, TX", "lat": 27.8117, "lng": -97.3883},

    # --- HAWAII ---
    {"id": "1612340", "name": "Honolulu, Oahu, HI", "lat": 21.3067, "lng": -157.8670},
    {"id": "1612480", "name": "Mokuoloe, Kaneohe Bay, HI", "lat": 21.4333, "lng": -157.7900},
    {"id": "1615680", "name": "Kahului, Maui, HI", "lat": 20.8950, "lng": -156.4700},
    {"id": "1617760", "name": "Hilo, Hawaii, HI", "lat": 19.7300, "lng": -155.0600},
    {"id": "1611400", "name": "Nawiliwili, Kauai, HI", "lat": 21.9533, "lng": -159.3567},

    # --- ALASKA ---
    {"id": "9452210", "name": "Juneau, AK", "lat": 58.2983, "lng": -134.4100},
    {"id": "9455920", "name": "Ketchikan, AK", "lat": 55.3317, "lng": -131.6267},
    {"id": "9457292", "name": "Seward, AK", "lat": 60.1200, "lng": -149.4267},
    {"id": "9455500", "name": "Sitka, AK", "lat": 57.0517, "lng": -135.3417},
]


def get_nearest_noaa_station(lat, lon):
    """Finds nearest NOAA station ID from the hardcoded list using Haversine distance."""
    def haversine(lat1, lon1, lat2, lon2):
        r = 3958.8  # radius in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    closest = min(
        NOAA_STATIONS,
        key=lambda s: haversine(lat, lon, s["lat"], s["lng"])
    )
    return closest["id"], closest["name"]


# -------------------------------------------------------------------
# Helper: Circular Mean for Directional Angles
# -------------------------------------------------------------------
def rolling_circular_mean(series, window=3):
    def calc_circ_mean(arr):
        rads = np.radians(arr)
        mean_sin = np.sin(rads).mean()
        mean_cos = np.cos(rads).mean()
        mean_rad = np.arctan2(mean_sin, mean_cos)
        return (np.degrees(mean_rad) + 360) % 360

    return (
        series.rolling(window=window, center=True, min_periods=1)
        .apply(calc_circ_mean, raw=True)
        .round(1)
    )



# -------------------------------------------------------------------
# 1. Fetch APIs & Build SQLite Database
# -------------------------------------------------------------------
@st.cache_resource(show_spinner="Fetching ocean & weather data...")
def fetch_and_prepare_data(lat, lon, station_id, fetch_date_str):
    """
    fetch_date_str ensures cache invalidates automatically when the day changes.
    """
    today = datetime.now()
    begin_date_str = today.strftime("%Y%m%d")
    end_date_str = (today + timedelta(days=3)).strftime("%Y%m%d")
    start_date_iso = today.strftime("%Y-%m-%d")
    end_date_iso = (today + timedelta(days=3)).strftime("%Y-%m-%d")

    # NOAA Tides Datagetter Query
    noaa_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    noaa_params = {
        "begin_date": begin_date_str,
        "end_date": end_date_str,
        "station": station_id,
        "product": "predictions",
        "datum": "MLLW",
        "units": "english",
        "time_zone": "lst_ldt",
        "interval": "6",
        "format": "json",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) SurfWindowFinder/1.0"
    }

    try:
        tide_resp = requests.get(noaa_url, params=noaa_params, headers=headers, timeout=10).json()
    except Exception as e:
        st.error(f"Error communicating with NOAA API: {e}")
        return None

    if "predictions" not in tide_resp:
        st.error("Could not fetch tide predictions. Please verify the NOAA Station ID.")
        return None

    df_tides = pd.DataFrame(tide_resp["predictions"])
    df_tides.rename(columns={"t": "datetime", "v": "tide_height_ft"}, inplace=True)
    df_tides["tide_height_ft"] = df_tides["tide_height_ft"].astype(float)
    df_tides["global_seq"] = range(1, len(df_tides) + 1)

    # Open-Meteo Sun
    meteo_weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["sunrise", "sunset"],
        "timezone": "auto",
        "start_date": start_date_iso,
        "end_date": end_date_iso,
    }
    sun_resp = requests.get(meteo_weather_url, params=weather_params).json()
    df_sun = pd.DataFrame(sun_resp["daily"])
    df_sun["sunrise"] = df_sun["sunrise"].str.replace("T", " ")
    df_sun["sunset"] = df_sun["sunset"].str.replace("T", " ")
    df_sun["date"] = pd.to_datetime(df_sun["time"]).dt.strftime("%Y-%m-%d")

    # Open-Meteo Marine Swell
    meteo_marine_url = "https://marine-api.open-meteo.com/v1/marine"
    marine_params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "swell_wave_height",
            "swell_wave_period",
            "swell_wave_direction",
            "secondary_swell_wave_height",
            "secondary_swell_wave_period",
            "secondary_swell_wave_direction",
        ],
        "models": "ncep_gfswave016",
        "cell_selection": "nearest",
        "timezone": "auto",
        "start_date": start_date_iso,
        "end_date": end_date_iso,
        "length_unit": "imperial",
    }
    marine_resp = requests.get(meteo_marine_url, params=marine_params).json()
    df_swell = pd.DataFrame(marine_resp["hourly"])
    df_swell["datetime"] = df_swell["time"].str.replace("T", " ")

    df_swell.rename(
        columns={
            "swell_wave_height": "swell_height_ft",
            "swell_wave_period": "swell_period_sec",
            "swell_wave_direction": "wave_direction",
            "secondary_swell_wave_height": "secondary_swell_wave_height",
            "secondary_swell_wave_period": "secondary_swell_wave_period",
            "secondary_swell_wave_direction": "secondary_swell_wave_direction",
        },
        inplace=True,
    )

    df_swell["wave_direction"] = rolling_circular_mean(df_swell["wave_direction"], window=3)
    df_swell["secondary_swell_wave_direction"] = rolling_circular_mean(df_swell["secondary_swell_wave_direction"], window=3)

    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df_tides.to_sql("tide_predictions", conn, index=False, if_exists="replace")
    df_sun.to_sql("sun_schedule", conn, index=False, if_exists="replace")
    df_swell.to_sql("swell_forecast", conn, index=False, if_exists="replace")

    return conn
# -------------------------------------------------------------------
# 2. Query Surf Windows
# -------------------------------------------------------------------
def get_surf_windows(conn, min_tide, max_tide):
    if conn is None:
        return pd.DataFrame()

    sql_master_query = """
    WITH TideTrends AS (
        SELECT
            global_seq, datetime, tide_height_ft,
            LAG(tide_height_ft, 1) OVER (ORDER BY global_seq ASC) AS prev_height_ft
        FROM tide_predictions
    ),
    TideDirection AS (
        SELECT
            global_seq, datetime, tide_height_ft,
            CASE WHEN prev_height_ft IS NULL OR tide_height_ft >= prev_height_ft THEN 'Rising' ELSE 'Dropping' END AS tide_trend
        FROM TideTrends
    ),
    FilteredRanges AS (
        SELECT
            global_seq, datetime, tide_height_ft, tide_trend,
            (global_seq - ROW_NUMBER() OVER (PARTITION BY tide_trend ORDER BY global_seq ASC)) AS island_id
        FROM TideDirection
        WHERE tide_height_ft BETWEEN ? AND ?
    ),
    DaylightTideWindows AS (
        SELECT
            tide_trend AS description,
            MIN(datetime) AS raw_window_start,
            MAX(datetime) AS raw_window_end,
            MIN(tide_height_ft) AS min_tide,
            MAX(tide_height_ft) AS max_tide,
            SUBSTR(MIN(datetime), 1, 10) AS window_date
        FROM FilteredRanges
        GROUP BY island_id, tide_trend
        HAVING COUNT(*) > 1
    ),
    FilteredDaylightWindows AS (
        SELECT
            w.description,
            w.min_tide,
            w.max_tide,
            MAX(w.raw_window_start, s.sunrise) AS window_start,
            MIN(w.raw_window_end, s.sunset) AS window_end
        FROM DaylightTideWindows w
        JOIN sun_schedule s ON w.window_date = s.date
        WHERE w.raw_window_start < s.sunset
          AND w.raw_window_end > s.sunrise
          AND MAX(w.raw_window_start, s.sunrise) < MIN(w.raw_window_end, s.sunset)
    )
    SELECT
        w.window_start,
        w.window_end,
        SUBSTR(w.window_start, 6, 5) AS Date,
        w.description AS Tide,
        CASE
            WHEN w.description LIKE '%Rising%' THEN ROUND(w.min_tide, 1) || ' -> ' || ROUND(w.max_tide, 1)
            ELSE ROUND(w.max_tide, 1) || ' -> ' || ROUND(w.min_tide, 1)
        END AS [Range (ft)],
        ROUND(AVG(swell_height_ft), 1) || ' ft' AS [Primary Swell Height],
        ROUND(AVG(swell_period_sec), 1) || ' s' AS [Primary Period],
        CASE
            WHEN AVG(wave_direction) >= 337.5 OR AVG(wave_direction) < 22.5 THEN 'N ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 22.5 AND AVG(wave_direction) < 67.5 THEN 'NE ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 67.5 AND AVG(wave_direction) < 112.5 THEN 'E ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 112.5 AND AVG(wave_direction) < 157.5 THEN 'SE ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 157.5 AND AVG(wave_direction) < 202.5 THEN 'S ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 202.5 AND AVG(wave_direction) < 247.5 THEN 'SW ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 247.5 AND AVG(wave_direction) < 292.5 THEN 'W ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            WHEN AVG(wave_direction) >= 292.5 AND AVG(wave_direction) < 337.5 THEN 'NW ' || CAST(ROUND(AVG(wave_direction), 0) AS INT)
            ELSE 'Unknown'
        END AS [Primary Direction],
        ROUND(AVG(secondary_swell_wave_height), 1) || ' ft' AS [Secondary Swell Height],
        ROUND(AVG(secondary_swell_wave_period), 1) || ' s' AS [Secondary Period],
        CASE
            WHEN AVG(secondary_swell_wave_direction) >= 337.5 OR AVG(secondary_swell_wave_direction) < 22.5 THEN 'N ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 22.5 AND AVG(secondary_swell_wave_direction) < 67.5 THEN 'NE ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 67.5 AND AVG(secondary_swell_wave_direction) < 112.5 THEN 'E ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 112.5 AND AVG(secondary_swell_wave_direction) < 157.5 THEN 'SE ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 157.5 AND AVG(secondary_swell_wave_direction) < 202.5 THEN 'S ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 202.5 AND AVG(secondary_swell_wave_direction) < 247.5 THEN 'SW ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 247.5 AND AVG(secondary_swell_wave_direction) < 292.5 THEN 'W ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            WHEN AVG(secondary_swell_wave_direction) >= 292.5 AND AVG(secondary_swell_wave_direction) < 337.5 THEN 'NW ' || CAST(ROUND(AVG(secondary_swell_wave_direction), 0) AS INT)
            ELSE 'Unknown'
        END AS [Secondary Direction]
    FROM FilteredDaylightWindows w
    JOIN swell_forecast s
      ON SUBSTR(s.datetime, 6, 13) >= SUBSTR(w.window_start, 6, 13)
     AND SUBSTR(s.datetime, 6, 13) <= SUBSTR(w.window_end, 6, 13)
    GROUP BY w.window_start, w.window_end, w.description
    ORDER BY w.window_start ASC;
    """
    df = pd.read_sql_query(sql_master_query, conn, params=(min_tide, max_tide))

    if not df.empty and "window_start" in df.columns:
        df["Start"] = pd.to_datetime(df["window_start"]).dt.strftime("%I:%M %p").str.lstrip("0")
        df["End"] = pd.to_datetime(df["window_end"]).dt.strftime("%I:%M %p").str.lstrip("0")

        df = df.drop(columns=["window_start", "window_end"])

        column_order = [
            "Date", "Start", "End", "Tide", "Range (ft)",
            "Primary Swell Height", "Primary Period", "Primary Direction",
            "Secondary Swell Height", "Secondary Period", "Secondary Direction"
        ]
        df = df[column_order]

    return df


# -------------------------------------------------------------------
# 3. Query Continuous Data for Tide Chart Visualization (with Clamped Highlights)
# -------------------------------------------------------------------
def get_chart_data(conn, min_tide, max_tide):
    """Retrieves full continuous tide predictions with daylight flags and active window highlights (clamped to sunrise/sunset)."""
    if conn is None:
        return pd.DataFrame()

    sql_chart_query = """
    WITH TideTrends AS (
        SELECT
            global_seq, datetime, tide_height_ft,
            LAG(tide_height_ft, 1) OVER (ORDER BY global_seq ASC) AS prev_height_ft
        FROM tide_predictions
    ),
    TideDirection AS (
        SELECT
            global_seq, datetime, tide_height_ft,
            CASE WHEN prev_height_ft IS NULL OR tide_height_ft >= prev_height_ft THEN 'Rising' ELSE 'Dropping' END AS tide_trend
        FROM TideTrends
    ),
    FilteredRanges AS (
        SELECT
            global_seq, datetime, tide_height_ft, tide_trend,
            (global_seq - ROW_NUMBER() OVER (PARTITION BY tide_trend ORDER BY global_seq ASC)) AS island_id
        FROM TideDirection
        WHERE tide_height_ft BETWEEN ? AND ?
    ),
    ValidWindows AS (
        SELECT
            MIN(datetime) AS window_start,
            MAX(datetime) AS window_end
        FROM FilteredRanges
        GROUP BY island_id, tide_trend
        HAVING COUNT(*) > 1
    ),
    DaylightWindows AS (
        SELECT
            MAX(w.window_start, s.sunrise) AS clamped_start,
            MIN(w.window_end, s.sunset) AS clamped_end
        FROM ValidWindows w
        JOIN sun_schedule s ON SUBSTR(w.window_start, 1, 10) = s.date
        WHERE w.window_start < s.sunset
          AND w.window_end > s.sunrise
          AND MAX(w.window_start, s.sunrise) < MIN(w.window_end, s.sunset)
    )
    SELECT
        t.datetime,
        t.tide_height_ft,
        s.sunrise,
        s.sunset,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM DaylightWindows dw
                WHERE t.datetime >= dw.clamped_start AND t.datetime <= dw.clamped_end
            ) THEN t.tide_height_ft
            ELSE NULL
        END AS highlight_tide_ft
    FROM tide_predictions t
    LEFT JOIN sun_schedule s ON SUBSTR(t.datetime, 1, 10) = s.date
    ORDER BY t.global_seq ASC;
    """

    df = pd.read_sql_query(sql_chart_query, conn, params=(min_tide, max_tide))
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df
# -------------------------------------------------------------------
# 4. Streamlit User Interface & Sidebar Map
# -------------------------------------------------------------------
st.set_page_config(page_title="Tide Window Finder", layout="wide")
st.title("Tide Window Finder")

# Session State Setup
if "lat" not in st.session_state:
    st.session_state.lat = 32.83
if "lon" not in st.session_state:
    st.session_state.lon = -117.33
if "station_id" not in st.session_state:
    st.session_state.station_id, st.session_state.station_name = get_nearest_noaa_station(
        st.session_state.lat, st.session_state.lon
    )

# -------------------------------------------------------------------
# Sidebar Setup
# -------------------------------------------------------------------
st.sidebar.header("Location & Map Picker")

# Browser Geolocation Button
if st.sidebar.button("Get My Current Location", use_container_width=True):
    location = get_geolocation()
    if location and "coords" in location:
        st.session_state.lat = round(location["coords"]["latitude"], 4)
        st.session_state.lon = round(location["coords"]["longitude"], 4)
        st.session_state.station_id, st.session_state.station_name = get_nearest_noaa_station(
            st.session_state.lat, st.session_state.lon
        )
        st.sidebar.success(f"Location set to {st.session_state.lat}, {st.session_state.lon}")

# Render Folium Map DIRECTLY in Sidebar
m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=8)
folium.Marker([st.session_state.lat, st.session_state.lon], tooltip="Selected Spot").add_to(m)

with st.sidebar:
    map_data = st_folium(
        m,
        height=280,
        width=None,  # Responsive to sidebar width
        key="sidebar_map",
        returned_objects=["last_clicked"]
    )

# Handle Map Click Events inside Sidebar
if map_data and map_data.get("last_clicked"):
    clicked_lat = round(map_data["last_clicked"]["lat"], 4)
    clicked_lon = round(map_data["last_clicked"]["lng"], 4)
    if clicked_lat != st.session_state.lat or clicked_lon != st.session_state.lon:
        st.session_state.lat = clicked_lat
        st.session_state.lon = clicked_lon
        st.session_state.station_id, st.session_state.station_name = get_nearest_noaa_station(
            clicked_lat, clicked_lon
        )
        st.rerun()

# Numeric Input Fallbacks & Variable Definitions
st.sidebar.subheader("Coordinates & Preferences")
lat = st.sidebar.number_input("Latitude", value=st.session_state.lat, format="%.4f")
lon = st.sidebar.number_input("Longitude", value=st.session_state.lon, format="%.4f")

station_id = st.session_state.station_id
st.sidebar.caption(f"Nearest station: **{st.session_state.station_name}** ({station_id})")

tide_range = st.sidebar.slider(
    "Preferred Tide Range (ft)",
    min_value=-2.0,
    max_value=7.0,
    value=(1.0, 4.0),
    step=0.1,
)
min_tide_val, max_tide_val = tide_range

# NOW lat, lon, station_id, and today_str are all defined!
today_str = datetime.now().strftime("%Y-%m-%d")
conn = fetch_and_prepare_data(lat, lon, station_id, today_str)

df_results = get_surf_windows(conn, min_tide=min_tide_val, max_tide=max_tide_val)

st.subheader(
    f"Optimal Windows for {min_tide_val} ft - {max_tide_val} ft Tide Range ({lat}, {lon}) | Station: {st.session_state.station_name} ({station_id})"
)
st.caption("If swell information is missing try selecting a location further offshore. Source: NOAA GFSwave 0.16° Data Inventory")

if not df_results.empty:
    st.dataframe(df_results, use_container_width=True, hide_index=True)
else:
    st.info("No surf windows matched your selected tide range.")

# -------------------------------------------------------------------
# 5. Continuous Tide Line Chart (Daylight Shading & Dynamic Readout)
# -------------------------------------------------------------------
df_chart = get_chart_data(conn, min_tide_val, max_tide_val)

if not df_chart.empty:
    st.subheader("Chart View")

    # Daylight Spans (Background)
    daylight_spans = (
        df_chart.groupby(df_chart["datetime"].dt.date)
        .agg(sunrise=("sunrise", "first"), sunset=("sunset", "first"))
        .reset_index()
    )
    daylight_spans["sunrise"] = pd.to_datetime(daylight_spans["sunrise"])
    daylight_spans["sunset"] = pd.to_datetime(daylight_spans["sunset"])

    day_bg = (
        alt.Chart(daylight_spans)
        .mark_rect(color="#FFF2C6", opacity=0.25)
        .encode(
            x="sunrise:T",
            x2="sunset:T",
            tooltip=alt.value(None),
        )
    )

    # Hover Selection (Snaps along x-axis)
    hover_select = alt.selection_point(
        name="hover_point",
        fields=["datetime"],
        on="pointerover",
        nearest=True,
        empty=False,
    )

    # Base Tide Line
    base_tide_line = (
        alt.Chart(df_chart)
        .mark_line(color="#708090", opacity=0.5, strokeWidth=1.5)
        .encode(
            x=alt.X(
                "datetime:T",
                title="Time",
                axis=alt.Axis(format="%a %I:%M %p", labelAngle=-45),
            ),
            y=alt.Y("tide_height_ft:Q", title="Tide Height (ft)"),
            tooltip=alt.value(None),
        )
    )

    # Window Highlight Overlay
    window_overlay = (
        alt.Chart(df_chart)
        .mark_line(color="#3366cc", strokeWidth=4)
        .encode(
            x="datetime:T",
            y="highlight_tide_ft:Q",
            tooltip=alt.value(None),
        )
    )

    # Invisible hover target layer
    hover_target = (
        alt.Chart(df_chart)
        .mark_point()
        .encode(
            x="datetime:T",
            opacity=alt.value(0),
            tooltip=alt.value(None),
        )
        .add_params(hover_select)
    )

    # Snapped Vertical Guideline
    hover_rule = (
        alt.Chart(df_chart)
        .mark_rule(color="#ffffff", strokeWidth=1.5, strokeDash=[4, 4])
        .encode(x="datetime:T", tooltip=alt.value(None))
        .transform_filter(hover_select)
    )

    # Snapped Point Marker
    hover_point_marker = (
        alt.Chart(df_chart)
        .mark_circle(size=70, color="#ffffff")
        .encode(
            x="datetime:T",
            y="tide_height_ft:Q",
            tooltip=alt.value(None),
        )
        .transform_filter(hover_select)
    )

    # Readout Text Layer (Unclipped & positioned at top)
    readout_text = (
        alt.Chart(df_chart)
        .mark_text(
            align="center",
            baseline="bottom",
            dy=35,
            fontSize=13,
            fontWeight="normal",
            color="#ffffff",
            clip=False,  # Disables clipping specifically for text
        )
        .encode(
            x="datetime:T",
            y=alt.value(0),
            text="readout_str:N",
            tooltip=alt.value(None),
        )
        .transform_filter(hover_select)
        .transform_calculate(
            readout_str=" timeFormat(datum.datetime, '%I:%M %p') + '  |  Tide: ' + format(datum.tide_height_ft, '.2f') + ' ft'"
        )
    )

    # Composite Chart
    combined_chart = (
        (
            day_bg
            + base_tide_line
            + window_overlay
            + hover_target
            + hover_rule
            + hover_point_marker
            + readout_text
        )
        .properties(width="container", height=420)
        .interactive(bind_y=False)
    )

    st.altair_chart(combined_chart, use_container_width=True)
