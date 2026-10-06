View at https://tidewindowcalculator.streamlit.app/

**Calculator used to quickly find upcoming time frames when tide will be in the desired range for your spot. Swell data collected from Open Meteorological NCEP GFS wave 16˚ API (https://marine-api.open-meteo.com/v1/marine). Currently supporting continental US. If wave data does not show, simply select a point further offshore.

## Features
- **Daylight Clamping**: Visualizes tide curves strictly between sunrise and sunset.
- **Optimal Window Highlighting**: Filters tide ranges dynamically based on user inputs.
- **Interactive Readout**: Hover crosshairs and real-time cursor values for tide height and time.
- **Data Pipeline**: Integrated with NOAA & Open-Meteo APIs backed by SQLite caching.

## Tech Stack
- **Frontend/UI**: Streamlit, Altair, Folium
- **Data Processing**: Pandas, SQLite, SQL CTEs
- **APIs**: NOAA Tides & Currents, Open-Meteo
