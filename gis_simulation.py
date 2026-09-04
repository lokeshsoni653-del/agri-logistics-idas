import math
import time
import requests
import pandas as pd

# 1. Haversine Formula for Straight-Line Distance (km)
def calculate_haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# 2. OSRM API Target for True-Road Metrics (Distance in km, Duration in minutes)
def get_true_road_metrics(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    try:
        start_t = time.time()
        response = requests.get(url, timeout=10).json()
        latency_ms = (time.time() - start_t) * 1000
        if 'routes' in response and len(response['routes']) > 0:
            dist_km = response['routes'][0]['distance'] / 1000.0
            duration_min = response['routes'][0]['duration'] / 60.0
            return dist_km, duration_min, latency_ms
    except Exception as e:
        print(f"OSRM Request failed: {e}")
    return None, None, None

# 3. Define Agricultural Corridors in Sindh
routes = [
    {"route_id": "R01", "route_name": "Mithi Farm A to Mithi Market", "lat1": 24.7436, "lon1": 69.8000, "lat2": 24.7310, "lon2": 69.7950},
    {"route_id": "R02", "route_name": "Mithi Depot to Naukot Junction", "lat1": 24.7436, "lon1": 69.7961, "lat2": 24.8580, "lon2": 69.5011},
    {"route_id": "R03", "route_name": "Naukot Belt to Digri Market", "lat1": 24.8580, "lon1": 69.5011, "lat2": 25.1023, "lon2": 69.0125},
    {"route_id": "R04", "route_name": "Digri Tomato Belt to Matli Hub", "lat1": 25.1023, "lon1": 69.0125, "lat2": 25.1378, "lon2": 68.9145},
    {"route_id": "R05", "route_name": "Matli Market to Hyderabad Processing Hub", "lat1": 25.1378, "lon1": 68.9145, "lat2": 25.3960, "lon2": 68.3578},
    {"route_id": "R06", "route_name": "Mithi to Hyderabad Full Corridor (NH-8)", "lat1": 24.7436, "lon1": 69.7961, "lat2": 25.3960, "lon2": 68.3578},
    {"route_id": "R07", "route_name": "Diplo Pastoral Route to Mithi Market", "lat1": 24.4667, "lon1": 69.5833, "lat2": 24.7436, "lon2": 69.7961},
    {"route_id": "R08", "route_name": "Tando Ghulam Ali to Tando Jam SAU Hub", "lat1": 25.1225, "lon1": 68.8876, "lat2": 25.4285, "lon2": 68.5365}
]

def run_gis_simulation():
    print("=========================================================")
    print("  Agri-Logistics IDAS - GIS Routing Simulation Engine")
    print("=========================================================\n")

    records = []
    for r in routes:
        h_dist = calculate_haversine(r["lat1"], r["lon1"], r["lat2"], r["lon2"])
        o_dist, o_time, latency = get_true_road_metrics(r["lat1"], r["lon1"], r["lat2"], r["lon2"])

        if o_dist is not None:
            pct_underestimate = ((o_dist - h_dist) / o_dist) * 100.0
            print(f"[{r['route_id']}] {r['route_name']}")
            print(f"   - Haversine Distance:  {h_dist:.2f} km")
            print(f"   - OSRM True-Road Dist: {o_dist:.2f} km")
            print(f"   - Haversine Error:     {pct_underestimate:.1f}% underestimation")
            print(f"   - Estimated Road Time: {o_time:.1f} mins ({o_time/60:.2f} hrs)")
            print(f"   - API Latency:         {latency:.1f} ms\n")

            records.append({
                "route_id": r["route_id"],
                "route_name": r["route_name"],
                "origin_lat": r["lat1"],
                "origin_lon": r["lon1"],
                "dest_lat": r["lat2"],
                "dest_lon": r["lon2"],
                "haversine_dist_km": round(h_dist, 2),
                "osrm_road_dist_km": round(o_dist, 2),
                "distance_delta_km": round(o_dist - h_dist, 2),
                "haversine_error_pct": round(pct_underestimate, 2),
                "estimated_duration_min": round(o_time, 1),
                "osrm_api_latency_ms": round(latency, 1)
            })

    df = pd.DataFrame(records)
    csv_filename = "agri_logistics_metrics.csv"
    df.to_csv(csv_filename, index=False)
    print(f"[SUCCESS] GIS Simulation dataset generated successfully: '{csv_filename}' ({len(df)} routes processed)")
    return df

if __name__ == "__main__":
    run_gis_simulation()
