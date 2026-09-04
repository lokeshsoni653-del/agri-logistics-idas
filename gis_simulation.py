import math
import time
import requests
import pandas as pd

# Constants for Economic & Operational Modeling
FUEL_PRICE_PKR_PER_LITER = 282.0  # Current average Pakistan diesel price in PKR
AVERAGE_FLEET_FUEL_EFFICIENCY_KMPL = 8.0  # Rural transport truck efficiency: 8 km per liter
NOMINAL_SPEED_KMH = 60.0  # Hypothetical speed used in straight-line naive calculations

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

# 3. Define Key Sindh Agricultural Corridors
routes = [
    {"route_id": "R01", "route_name": "Mithi Farm A to Mithi Market", "crop": "Millet/Grain", "lat1": 24.7436, "lon1": 69.8000, "lat2": 24.7310, "lon2": 69.7950},
    {"route_id": "R02", "route_name": "Mithi Depot to Naukot Junction", "crop": "Mixed Produce", "lat1": 24.7436, "lon1": 69.7961, "lat2": 24.8580, "lon2": 69.5011},
    {"route_id": "R03", "route_name": "Naukot Belt to Digri Market", "crop": "Chili/Grain", "lat1": 24.8580, "lon1": 69.5011, "lat2": 25.1023, "lon2": 69.0125},
    {"route_id": "R04", "route_name": "Digri Tomato Belt to Matli Hub", "crop": "Perishable Tomatoes", "lat1": 25.1023, "lon1": 69.0125, "lat2": 25.1378, "lon2": 68.9145},
    {"route_id": "R05", "route_name": "Matli Market to Hyderabad Processing Hub", "crop": "Vegetables/Onions", "lat1": 25.1378, "lon1": 68.9145, "lat2": 25.3960, "lon2": 68.3578},
    {"route_id": "R06", "route_name": "Mithi to Hyderabad Full Corridor (NH-8)", "crop": "Supply Chain Arterial", "lat1": 24.7436, "lon1": 69.7961, "lat2": 25.3960, "lon2": 68.3578},
    {"route_id": "R07", "route_name": "Diplo Pastoral Route to Mithi Market", "crop": "Dairy/Livestock", "lat1": 24.4667, "lon1": 69.5833, "lat2": 24.7436, "lon2": 69.7961},
    {"route_id": "R08", "route_name": "Tando Ghulam Ali to Tando Jam SAU Hub", "crop": "Research Research Cargo", "lat1": 25.1225, "lon1": 68.8876, "lat2": 25.4285, "lon2": 68.5365}
]

def run_gis_simulation():
    print("=======================================================================")
    print("  Agri-Logistics IDAS - GIS Routing & Economic Discrepancy Simulation")
    print("=======================================================================\n")

    records = []
    for r in routes:
        h_dist = calculate_haversine(r["lat1"], r["lon1"], r["lat2"], r["lon2"])
        o_dist, o_time, latency = get_true_road_metrics(r["lat1"], r["lon1"], r["lat2"], r["lon2"])

        if o_dist is not None:
            # Distance error
            dist_delta = o_dist - h_dist
            pct_underestimate = (dist_delta / o_dist) * 100.0
            
            # Estimated naive time vs True-road time
            h_time_min = (h_dist / NOMINAL_SPEED_KMH) * 60.0
            time_delta_min = o_time - h_time_min

            # Fuel calculations
            h_fuel_liters = h_dist / AVERAGE_FLEET_FUEL_EFFICIENCY_KMPL
            o_fuel_liters = o_dist / AVERAGE_FLEET_FUEL_EFFICIENCY_KMPL
            fuel_delta_liters = o_fuel_liters - h_fuel_liters

            # Economic cost (PKR)
            h_cost_pkr = h_fuel_liters * FUEL_PRICE_PKR_PER_LITER
            o_cost_pkr = o_fuel_liters * FUEL_PRICE_PKR_PER_LITER
            cost_delta_pkr = o_cost_pkr - h_cost_pkr

            print(f"[{r['route_id']}] {r['route_name']} ({r['crop']})")
            print(f"   - Straight-Line (Haversine): {h_dist:.2f} km | Est. Fuel: {h_fuel_liters:.2f} L | Cost: Rs. {h_cost_pkr:.0f}")
            print(f"   - True-Road (OSRM):          {o_dist:.2f} km | Real Fuel: {o_fuel_liters:.2f} L | Cost: Rs. {o_cost_pkr:.0f}")
            print(f"   - Unbudgeted Discrepancy:    +{dist_delta:.2f} km (+{pct_underestimate:.1f}%) | +{fuel_delta_liters:.2f} L (+Rs. {cost_delta_pkr:.0f})")
            print(f"   - Time Discrepancy:          Naive: {h_time_min:.1f} min vs Real: {o_time:.1f} min (+{time_delta_min:.1f} min)")
            print(f"   - OSRM Query Latency:        {latency:.1f} ms\n")

            records.append({
                "route_id": r["route_id"],
                "route_name": r["route_name"],
                "primary_cargo": r["crop"],
                "haversine_dist_km": round(h_dist, 2),
                "osrm_road_dist_km": round(o_dist, 2),
                "distance_underest_km": round(dist_delta, 2),
                "error_percentage": round(pct_underestimate, 2),
                "haversine_est_time_min": round(h_time_min, 1),
                "osrm_actual_time_min": round(o_time, 1),
                "time_delay_min": round(time_delta_min, 1),
                "haversine_fuel_liters": round(h_fuel_liters, 2),
                "osrm_fuel_liters": round(o_fuel_liters, 2),
                "unbudgeted_fuel_liters": round(fuel_delta_liters, 2),
                "haversine_cost_pkr": round(h_cost_pkr, 2),
                "osrm_actual_cost_pkr": round(o_cost_pkr, 2),
                "unbudgeted_cost_pkr": round(cost_delta_pkr, 2),
                "api_latency_ms": round(latency, 1)
            })

    df = pd.DataFrame(records)
    csv_filename = "agri_logistics_metrics.csv"
    df.to_csv(csv_filename, index=False)
    print(f"[SUCCESS] Comprehensive GIS & Economic Dataset generated: '{csv_filename}'")
    
    # Summary Insights
    avg_error = df["error_percentage"].mean()
    total_unbudgeted_fuel = df["unbudgeted_fuel_liters"].sum()
    total_unbudgeted_cost = df["unbudgeted_cost_pkr"].sum()
    print("\n========================= EMPIRICAL SUMMARY =========================")
    print(f"Mean Road Distance Underestimation: {avg_error:.2f}%")
    print(f"Cumulative Unbudgeted Fuel Across Corridors: {total_unbudgeted_fuel:.2f} Liters")
    print(f"Cumulative Hidden Economic Expense: Rs. {total_unbudgeted_cost:,.2f} PKR")
    print("=====================================================================")
    return df

if __name__ == "__main__":
    run_gis_simulation()
