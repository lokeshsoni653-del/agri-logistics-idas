"""
routing.py — Agri-Logistics IDAS
=================================
Production-grade routing module for the Intelligent Driver Assistance System.

Author      : Lokesh Kumar
Student ID  : 2k22-SE-42
Email       : 2K22-SE-42@student.sau.edu.pk
Institution : Sindh Agriculture University, Tandojam

Public API
----------
  get_osrm_route(start_coords, end_coords)
      Calls the free OSRM Routing API and returns route geometry
      (as a list of lat/lon points), human-readable turn-by-turn
      instructions, and summary metrics (distance_km, duration_min).

  plot_route_on_map(route_geometry, start_coords, end_coords, ...)
      Renders the returned geometry on an interactive Folium map
      and displays it inside a Streamlit app via streamlit-folium.
      Returns the Folium map_data dict from st_folium.

  plot_fallback_map(start_coords, end_coords, ...)
      Renders a minimal marker-only Folium map when the OSRM API
      is unreachable. Keeps the UI functional during network outages.

Default test coordinates
------------------------
  Start : Mithi      (24.7436 N, 69.7971 E)
  End   : Hyderabad  (25.3960 N, 68.3578 E)

Dependencies
------------
  pip install requests folium streamlit-folium streamlit
"""

import requests
import folium
import streamlit as st
from streamlit_folium import st_folium

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────

# Public OSRM demo server — no API key required.
# Swap the base URL for a self-hosted OSRM instance in production
# (e.g. "http://localhost:5000") to avoid rate limits.
OSRM_BASE_URL = "http://router.project-osrm.org"

# Request timeout in seconds — keep generous for slow rural networks
REQUEST_TIMEOUT = 15

# Default test coordinates (lat, lon)
MITHI_COORDS     = (24.7436, 69.7971)
HYDERABAD_COORDS = (25.3960, 68.3578)

# Human-readable labels for OSRM maneuver types
# Reference: https://project-osrm.org/docs/v5.24.0/api/#step-object
MANEUVER_VERB = {
    "depart":      "Head",
    "arrive":      "Arrive at destination",
    "turn":        "Turn",
    "continue":    "Continue",
    "new name":    "Continue onto",
    "merge":       "Merge onto",
    "on ramp":     "Take ramp onto",
    "off ramp":    "Take exit onto",
    "fork":        "Take fork onto",
    "end of road": "At end of road, turn",
    "roundabout":  "Enter roundabout",
    "rotary":      "Enter roundabout",
    "notification":"Note:",
}

# Human-readable labels for OSRM modifier values
MODIFIER_LABEL = {
    "straight":    "straight",
    "left":        "left",
    "right":       "right",
    "slight left": "slight left",
    "slight right":"slight right",
    "sharp left":  "sharp left",
    "sharp right": "sharp right",
    "uturn":       "U-turn",
}

# Map colours
ROUTE_LINE_COLOR   = "#2D5016"   # Dark agri-green for the route polyline
START_MARKER_COLOR = "green"     # Folium named colour for departure pin
END_MARKER_COLOR   = "red"       # Folium named colour for destination pin


# ─────────────────────────────────────────────────────────────────
# HELPER — format a distance float into a readable string
# ─────────────────────────────────────────────────────────────────

def _format_distance(metres: float) -> str:
    """Return a compact distance string: '350 m' or '12.4 km'."""
    if metres < 1000:
        return f"{round(metres)} m"
    return f"{round(metres / 1000, 1)} km"


# ─────────────────────────────────────────────────────────────────
# HELPER — build one English instruction string from an OSRM step
# ─────────────────────────────────────────────────────────────────

def _build_instruction(step: dict) -> str:
    """
    Convert a single OSRM step dict into a plain-English sentence.

    OSRM step keys used:
      - maneuver.type     : category of movement (turn, depart, arrive, …)
      - maneuver.modifier : direction qualifier (left, right, straight, …)
      - name              : road / street name at this step
      - distance          : metres to travel before the next step
    """
    maneuver  = step.get("maneuver", {})
    m_type    = maneuver.get("type", "continue")
    m_mod     = maneuver.get("modifier", "")
    road_name = step.get("name", "").strip()
    distance  = step.get("distance", 0)

    # "Arrive" is a terminal step — no distance label needed
    if m_type == "arrive":
        return "Arrive at destination"

    # Build the sentence in parts
    parts = []

    # 1. Action verb (Head / Turn / Continue / …)
    parts.append(MANEUVER_VERB.get(m_type, "Continue"))

    # 2. Direction modifier if present (left / right / straight / …)
    if m_mod:
        parts.append(MODIFIER_LABEL.get(m_mod, m_mod))

    # 3. Road name (phrased differently for "depart" vs mid-route steps)
    if road_name:
        if m_type == "depart":
            parts.append(f"on {road_name}")
        else:
            parts.append(f"onto {road_name}")

    # 4. Distance until the next step
    parts.append(f"({_format_distance(distance)})")

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────────
# FUNCTION 1 — get_osrm_route
# ─────────────────────────────────────────────────────────────────

def get_osrm_route(
    start_coords: tuple = MITHI_COORDS,
    end_coords:   tuple = HYDERABAD_COORDS,
) -> dict:
    """
    Call the OSRM driving-route API and return parsed route data.

    Parameters
    ----------
    start_coords : (lat, lon)  — departure point, e.g. (24.7436, 69.7971)
    end_coords   : (lat, lon)  — destination,     e.g. (25.3960, 68.3578)

    Returns
    -------
    dict with keys:
        "success"       : bool   — False if the API call or parsing failed
        "error"         : str    — human-readable error message (on failure)
        "distance_km"   : float  — total route distance in kilometres
        "duration_min"  : float  — estimated driving time in minutes
        "geometry"      : list[tuple[float,float]]
                          Ordered list of (lat, lon) points that form
                          the full route polyline.  Ready for Folium.
        "instructions"  : list[str]
                          Human-readable turn-by-turn directions.

    Notes
    -----
    - OSRM uses (lon, lat) in its URL and response; we convert to
      (lat, lon) internally so callers always work in standard order.
    - The `overview=full` parameter requests the complete polyline
      (not simplified), which is important for accurate map rendering
      on winding rural roads in Sindh.
    - `steps=true` asks OSRM to include turn-by-turn step data inside
      each leg of the route.
    - `geometries=geojson` returns coordinates as a GeoJSON LineString,
      which is easier to parse than the default encoded polyline.
    """

    # --- Unpack and validate coordinates ---
    start_lat, start_lon = start_coords
    end_lat,   end_lon   = end_coords

    for name, lat, lon in [("start", start_lat, start_lon), ("end", end_lat, end_lon)]:
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return {
                "success": False,
                "error":   f"Invalid {name} coordinates: ({lat}, {lon})",
            }

    # --- Build OSRM URL ---
    # OSRM coordinate order in the URL is  lon,lat;lon,lat
    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        f"?overview=full&geometries=geojson&steps=true&annotations=false"
    )

    # --- Make HTTP request ---
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "AgriLogisticsIDAS/3.0 (SAU Tandojam Research)"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()          # raises on 4xx / 5xx
        data = response.json()

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error":   "Cannot reach OSRM server. Check your internet connection.",
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error":   f"OSRM request timed out after {REQUEST_TIMEOUT} s.",
        }
    except requests.exceptions.HTTPError as exc:
        return {
            "success": False,
            "error":   f"OSRM HTTP error: {exc}",
        }
    except Exception as exc:
        return {
            "success": False,
            "error":   f"Unexpected error contacting OSRM: {exc}",
        }

    # --- Validate OSRM response ---
    if data.get("code") != "Ok":
        osrm_msg = data.get("message", "Unknown OSRM error")
        return {
            "success": False,
            "error":   f"OSRM returned code '{data.get('code')}': {osrm_msg}",
        }

    routes = data.get("routes", [])
    if not routes:
        return {
            "success": False,
            "error":   "OSRM returned no routes for these coordinates.",
        }

    # --- Extract primary route (OSRM returns best route first) ---
    route = routes[0]

    # Distance and duration
    distance_km  = round(route["distance"] / 1000, 2)
    duration_min = round(route["duration"] / 60, 1)

    # --- Extract geometry ---
    # OSRM GeoJSON geometry: { "type": "LineString", "coordinates": [[lon, lat], ...] }
    # We flip each pair to (lat, lon) for Folium compatibility.
    raw_coords = route["geometry"]["coordinates"]   # list of [lon, lat]
    geometry   = [(c[1], c[0]) for c in raw_coords] # list of (lat, lon)

    # --- Extract turn-by-turn instructions ---
    # A route has one or more legs (one per waypoint gap).
    # Each leg has steps; each step describes one maneuver.
    instructions = []
    for leg in route.get("legs", []):
        for step in leg.get("steps", []):
            instruction = _build_instruction(step)
            instructions.append(instruction)

    return {
        "success":      True,
        "error":        None,
        "distance_km":  distance_km,
        "duration_min": duration_min,
        "geometry":     geometry,       # list of (lat, lon) tuples
        "instructions": instructions,   # list of plain-English strings
    }


# ─────────────────────────────────────────────────────────────────
# FUNCTION 2 — plot_route_on_map
# ─────────────────────────────────────────────────────────────────

def plot_route_on_map(
    route_geometry:  list,
    start_coords:    tuple = MITHI_COORDS,
    end_coords:      tuple = HYDERABAD_COORDS,
    start_label:     str   = "Mithi (Departure)",
    end_label:       str   = "Hyderabad (Destination)",
    map_height_px:   int   = 460,
    key:             str   = None,
) -> dict:
    """
    Render a Folium map with the OSRM route polyline inside Streamlit.

    Parameters
    ----------
    route_geometry  : Ordered list of (lat, lon) tuples from get_osrm_route().
    start_coords    : (lat, lon) of the departure point.
    end_coords      : (lat, lon) of the destination.
    start_label     : Popup / tooltip label for the departure marker.
    end_label       : Popup / tooltip label for the destination marker.
    map_height_px   : Height of the rendered map in pixels.
    key             : Unique key for st_folium.

    Returns
    -------
    dict — the raw st_folium output (contains last_clicked, center, zoom).
    """
    if not route_geometry or len(route_geometry) < 2:
        st.error("Route geometry must contain at least two points.")
        return {}

    # --- Compute map centre (midpoint of the bounding box) ---
    lats = [p[0] for p in route_geometry]
    lons = [p[1] for p in route_geometry]
    centre_lat = (min(lats) + max(lats)) / 2
    centre_lon = (min(lons) + max(lons)) / 2

    # --- Estimate a sensible initial zoom level ---
    lat_span = max(lats) - min(lats)
    lon_span = max(lons) - min(lons)
    span     = max(lat_span, lon_span)

    if   span > 10:  zoom = 6
    elif span > 3:   zoom = 8
    elif span > 1:   zoom = 10
    elif span > 0.3: zoom = 11
    else:            zoom = 13

    # --- Initialise Folium map with OpenStreetMap tiles ---
    fmap = folium.Map(
        location=[centre_lat, centre_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",   # free, no API key
        control_scale=True,      # shows a distance scale bar
    )

    # --- Draw the route as a polyline ---
    folium.PolyLine(
        locations=route_geometry,
        color=ROUTE_LINE_COLOR,
        weight=5,
        opacity=0.85,
        tooltip="Route: Mithi → Hyderabad",
    ).add_to(fmap)

    # --- Departure marker (green pin) ---
    folium.Marker(
        location=list(start_coords),
        popup=folium.Popup(start_label, max_width=200),
        tooltip=start_label,
        icon=folium.Icon(color=START_MARKER_COLOR, icon="truck", prefix="fa"),
    ).add_to(fmap)

    # --- Destination marker (red pin) ---
    folium.Marker(
        location=list(end_coords),
        popup=folium.Popup(end_label, max_width=200),
        tooltip=end_label,
        icon=folium.Icon(color=END_MARKER_COLOR, icon="flag", prefix="fa"),
    ).add_to(fmap)

    # --- Fit the map view to the full route extent ---
    fmap.fit_bounds(
        [[min(lats), min(lons)], [max(lats), max(lons)]],
        padding=(30, 30),
    )

    # --- Render inside Streamlit ---
    map_data = st_folium(
        fmap,
        use_container_width=True,
        height=map_height_px,
        returned_objects=["last_clicked", "center", "zoom"],
        key=key,
    )

    return map_data


# ─────────────────────────────────────────────────────────────────
# FUNCTION 3 — plot_fallback_map  (NEW — Phase 3 addition)
# ─────────────────────────────────────────────────────────────────

def plot_fallback_map(
    start_coords:  tuple = MITHI_COORDS,
    end_coords:    tuple = HYDERABAD_COORDS,
    start_label:   str   = "Mithi (Departure)",
    end_label:     str   = "Hyderabad (Destination)",
    map_height_px: int   = 460,
    key:           str   = None,
) -> dict:
    """
    Render a minimal Folium map showing only the two endpoint markers
    when the OSRM API is unreachable.

    This keeps the UI functional during network outages. The map shows
    the departure and destination pins on an OpenStreetMap basemap without
    a route polyline, and displays a warning inside the map popup.

    Parameters
    ----------
    start_coords  : (lat, lon) of the departure point.
    end_coords    : (lat, lon) of the destination.
    start_label   : Tooltip/popup for the departure marker.
    end_label     : Tooltip/popup for the destination marker.
    map_height_px : Height of the rendered map in pixels.
    key           : Unique key for st_folium.

    Returns
    -------
    dict — the raw st_folium output.
    """
    start_lat, start_lon = start_coords
    end_lat,   end_lon   = end_coords

    # Centre the map between the two points
    centre_lat = (start_lat + end_lat) / 2
    centre_lon = (start_lon + end_lon) / 2

    fmap = folium.Map(
        location=[centre_lat, centre_lon],
        zoom_start=9,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Departure marker
    folium.Marker(
        location=[start_lat, start_lon],
        popup=folium.Popup(
            f"{start_label}<br><em>Route unavailable — OSRM offline</em>",
            max_width=220,
        ),
        tooltip=start_label,
        icon=folium.Icon(color=START_MARKER_COLOR, icon="truck", prefix="fa"),
    ).add_to(fmap)

    # Destination marker
    folium.Marker(
        location=[end_lat, end_lon],
        popup=folium.Popup(
            f"{end_label}<br><em>Route unavailable — OSRM offline</em>",
            max_width=220,
        ),
        tooltip=end_label,
        icon=folium.Icon(color=END_MARKER_COLOR, icon="flag", prefix="fa"),
    ).add_to(fmap)

    # Dashed straight-line between points as a visual hint
    folium.PolyLine(
        locations=[[start_lat, start_lon], [end_lat, end_lon]],
        color="#B0A890",
        weight=2,
        opacity=0.6,
        dash_array="8 4",
        tooltip="Estimated straight-line path (no road data)",
    ).add_to(fmap)

    # Fit bounds to include both markers
    fmap.fit_bounds(
        [
            [min(start_lat, end_lat), min(start_lon, end_lon)],
            [max(start_lat, end_lat), max(start_lon, end_lon)],
        ],
        padding=(40, 40),
    )

    map_data = st_folium(
        fmap,
        use_container_width=True,
        height=map_height_px,
        returned_objects=["last_clicked", "center", "zoom"],
        key=key,
    )

    return map_data


# ─────────────────────────────────────────────────────────────────
# FUNCTION 4 — get_route_map_html  (Driver View — no st_folium)
# ─────────────────────────────────────────────────────────────────

def get_route_map_html(
    route_geometry:  list,
    start_coords:    tuple = MITHI_COORDS,
    end_coords:      tuple = HYDERABAD_COORDS,
    start_label:     str   = "Mithi (Departure)",
    end_label:       str   = "Hyderabad (Destination)",
    map_height_px:   int   = 290,
) -> str:
    """
    Build a Folium route map and return it as a raw HTML string.

    Unlike plot_route_on_map() which uses st_folium(), this function
    uses folium's own _repr_html_() renderer, completely bypassing the
    streamlit-folium component.  This avoids all duplicate-key errors
    when two maps are rendered in the same Streamlit session.

    Returns
    -------
    str — self-contained HTML string that can be embedded with
          st.components.v1.html(html_str, height=map_height_px).
    """
    if not route_geometry or len(route_geometry) < 2:
        return "<p style='color:red;'>Route geometry is empty.</p>"

    # Convert stored geometry safely: supports both tuples and lists
    coords = [(float(p[0]), float(p[1])) for p in route_geometry]

    lats = [p[0] for p in coords]
    lons = [p[1] for p in coords]
    centre_lat = (min(lats) + max(lats)) / 2
    centre_lon = (min(lons) + max(lons)) / 2

    lat_span = max(lats) - min(lats)
    lon_span = max(lons) - min(lons)
    span     = max(lat_span, lon_span)

    if   span > 10:  zoom = 6
    elif span > 3:   zoom = 8
    elif span > 1:   zoom = 10
    elif span > 0.3: zoom = 11
    else:            zoom = 13

    fmap = folium.Map(
        location=[centre_lat, centre_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap",
        control_scale=True,
        width="100%",
        height=map_height_px,
    )

    folium.PolyLine(
        locations=coords,
        color=ROUTE_LINE_COLOR,
        weight=5,
        opacity=0.85,
        tooltip="Route: Mithi → Hyderabad",
    ).add_to(fmap)

    folium.Marker(
        location=list(start_coords),
        popup=folium.Popup(start_label, max_width=200),
        tooltip=start_label,
        icon=folium.Icon(color=START_MARKER_COLOR, icon="truck", prefix="fa"),
    ).add_to(fmap)

    folium.Marker(
        location=list(end_coords),
        popup=folium.Popup(end_label, max_width=200),
        tooltip=end_label,
        icon=folium.Icon(color=END_MARKER_COLOR, icon="flag", prefix="fa"),
    ).add_to(fmap)

    fmap.fit_bounds(
        [[min(lats), min(lons)], [max(lats), max(lons)]],
        padding=(20, 20),
    )

    return fmap._repr_html_()


# ─────────────────────────────────────────────────────────────────
# FUNCTION 5 — get_fallback_map_html  (Driver View — no st_folium)
# ─────────────────────────────────────────────────────────────────

def get_fallback_map_html(
    start_coords:  tuple = MITHI_COORDS,
    end_coords:    tuple = HYDERABAD_COORDS,
    start_label:   str   = "Mithi (Departure)",
    end_label:     str   = "Hyderabad (Destination)",
    map_height_px: int   = 290,
) -> str:
    """
    Build a marker-only fallback Folium map and return it as raw HTML.
    Used in the Driver View when OSRM routing is unavailable.
    """
    start_lat, start_lon = start_coords
    end_lat,   end_lon   = end_coords
    centre_lat = (start_lat + end_lat) / 2
    centre_lon = (start_lon + end_lon) / 2

    fmap = folium.Map(
        location=[centre_lat, centre_lon],
        zoom_start=9,
        tiles="OpenStreetMap",
        control_scale=True,
        width="100%",
        height=map_height_px,
    )

    folium.Marker(
        location=[start_lat, start_lon],
        popup=folium.Popup(f"{start_label}<br><em>Route unavailable</em>", max_width=220),
        tooltip=start_label,
        icon=folium.Icon(color=START_MARKER_COLOR, icon="truck", prefix="fa"),
    ).add_to(fmap)

    folium.Marker(
        location=[end_lat, end_lon],
        popup=folium.Popup(f"{end_label}<br><em>Route unavailable</em>", max_width=220),
        tooltip=end_label,
        icon=folium.Icon(color=END_MARKER_COLOR, icon="flag", prefix="fa"),
    ).add_to(fmap)

    folium.PolyLine(
        locations=[[start_lat, start_lon], [end_lat, end_lon]],
        color="#B0A890",
        weight=2,
        opacity=0.6,
        dash_array="8 4",
    ).add_to(fmap)

    fmap.fit_bounds(
        [
            [min(start_lat, end_lat), min(start_lon, end_lon)],
            [max(start_lat, end_lat), max(start_lon, end_lon)],
        ],
        padding=(30, 30),
    )

    return fmap._repr_html_()


# ─────────────────────────────────────────────────────────────────
# STANDALONE TEST — run `streamlit run routing.py` to demo
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    st.set_page_config(
        page_title="IDAS Routing — Test",
        page_icon="🗺️",
        layout="wide",
    )

    st.title("🗺️ Agri-Logistics IDAS — Routing Module Test")
    st.caption(
        "Tests `get_osrm_route()` and `plot_route_on_map()` "
        "with the default Mithi → Hyderabad corridor."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("🟢 Departure")
        s_lat = st.number_input("Start Latitude",  value=MITHI_COORDS[0],      format="%.4f")
        s_lon = st.number_input("Start Longitude", value=MITHI_COORDS[1],      format="%.4f")
    with col_b:
        st.subheader("🔴 Destination")
        e_lat = st.number_input("End Latitude",    value=HYDERABAD_COORDS[0],  format="%.4f")
        e_lon = st.number_input("End Longitude",   value=HYDERABAD_COORDS[1],  format="%.4f")

    if st.button("🚚 Get Route", type="primary", use_container_width=True):

        with st.spinner("Calling OSRM API …"):
            result = get_osrm_route(
                start_coords=(s_lat, s_lon),
                end_coords=(e_lat, e_lon),
            )

        if not result["success"]:
            st.warning("OSRM routing failed — showing fallback map.")
            st.error(f"Reason: {result['error']}")
            plot_fallback_map(
                start_coords=(s_lat, s_lon),
                end_coords=(e_lat, e_lon),
            )
            st.stop()

        m1, m2, m3 = st.columns(3)
        m1.metric("Distance",      f"{result['distance_km']} km")
        m2.metric("Est. Duration", f"{result['duration_min']} min")
        m3.metric("Route points",  len(result["geometry"]))

        st.divider()

        col_map, col_steps = st.columns([1.6, 1])

        with col_map:
            st.subheader("🗺️ Route Map")
            plot_route_on_map(
                route_geometry=result["geometry"],
                start_coords=(s_lat, s_lon),
                end_coords=(e_lat, e_lon),
                start_label=f"Departure ({s_lat:.4f}, {s_lon:.4f})",
                end_label=f"Destination ({e_lat:.4f}, {e_lon:.4f})",
            )

        with col_steps:
            st.subheader("📋 Turn-by-Turn Directions")
            for i, step in enumerate(result["instructions"], start=1):
                if i == 1:
                    st.success(f"**{i}.** {step}")
                elif "Arrive" in step:
                    st.info(f"**{i}.** {step}")
                else:
                    st.write(f"**{i}.** {step}")

    else:
        st.info("👆 Set coordinates above and click **Get Route** to test.")
