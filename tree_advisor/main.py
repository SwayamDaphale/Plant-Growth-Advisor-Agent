#!/usr/bin/env python3
"""
Tree Advisor (terminal)
- Auto-fetches soil pH from region using geocoding + SoilGrids (best-effort)
- Accepts Marathi transliteration soil names (e.g., 'lal mati') and normalizes them
- Uses Gemini via REST if GOOGLE_API_KEY is present; otherwise uses rule-based fallback
- After main recommendation, offers chat/Q&A loop (terminates on 'no')
"""

import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")  # optional
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
TIMEOUT = 25  # seconds for HTTP calls

# --- Simple transliteration/soil mapping (expand as needed)
SOIL_MAP = {
    "lal mati": "red soil",
    "lal maati": "red soil",
    "lalmatti": "red soil",
    "kali mati": "black soil",
    "kalimati": "black soil",
    "regadi": "sandy soil",
    "balukamati": "sandy soil",
    "balukamatti": "sandy soil",
    "retimati": "sandy soil",
    "loamy": "loamy soil",
    "loam": "loamy soil",
    "loamy soil": "loamy soil",
    "sandy": "sandy soil",
    "clay": "clay soil",
    "clayey": "clay soil",
    "black soil": "black soil",
    "red soil": "red soil",
    "alluvial": "alluvial soil",
}

# rainfall categories -> mm (representative)
RAINFALL_MAP = {
    "low": 300.0,
    "moderate": 700.0,
    "medium": 700.0,
    "high": 1200.0
}

# --- Helpers for geocoding + soil pH (best-effort)
def geocode_region(region_name: str):
    """Use Open-Meteo geocoding to get lat/lon from a region name (best-effort)."""
    try:
        q = region_name.strip()
        if not q:
            return None
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": q, "count": 1, "language": "en"}
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        j = r.json()
        if "results" in j and j["results"]:
            res = j["results"][0]
            return float(res["latitude"]), float(res["longitude"])
    except Exception:
        return None
    return None

def query_soilgrids_ph(lat: float, lon: float):
    """
    Query SoilGrids (rest.soilgrids.org) for pH. The API sometimes returns scaled values.
    Return pH float or None on failure.
    """
    try:
        url = f"https://rest.soilgrids.org/query"
        params = {"lon": lon, "lat": lat}
        r = requests.get(url, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        j = r.json()
        # The SoilGrids response can vary; attempt common keys
        # Try properties -> phh2o -> mean
        props = j.get("properties", {})
        ph_val = None

        # Try various possible nested locations
        if "phh2o" in props:
            ph_info = props["phh2o"]
            # some responses: phh2o -> mean (value scaled by 10)
            if isinstance(ph_info, dict) and "mean" in ph_info:
                ph_val = ph_info["mean"]
        # other possible key naming:
        if ph_val is None and "PHIHOX" in props:
            # Older formats – attempt multiple attempts (best effort)
            ph_val = props.get("PHIHOX", {}).get("phh2o_mean")

        # If still None try scanning the JSON for numbers that look like pH
        if ph_val is None:
            # fallback: attempt to find phh2o in nested dicts
            def search_for_ph(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(k, str) and "ph" in k.lower() and isinstance(v, (int, float)):
                            return v
                        found = search_for_ph(v)
                        if found is not None:
                            return found
                elif isinstance(obj, list):
                    for item in obj:
                        found = search_for_ph(item)
                        if found is not None:
                            return found
                return None
            ph_val = search_for_ph(props)

        if ph_val is None:
            return None

        # ph_val might be scaled (e.g., pH*10), convert if necessary
        # valid pH range ~ 0 - 14 (we expect 3-9 commonly)
        p = float(ph_val)
        if p > 14:
            p = p / 10.0
        # final sanity clamp
        if 0 < p < 14:
            return round(p, 2)
    except Exception:
        return None
    return None

def get_region_ph_and_rainfall(region: str):
    """Given a region string, attempt to return (ph, avg_rainfall_mm).
       If rainfall not available, return None for rainfall."""
    # 1) Geocode
    coords = geocode_region(region)
    if not coords:
        return None, None
    lat, lon = coords
    # 2) Query SoilGrids
    ph = query_soilgrids_ph(lat, lon)
    # 3) For rainfall we can use Open-Meteo climate API to get mean annual precipitation
    rainfall = None
    try:
        # Open-Meteo Climate Data — Climate API (monthly averages); use climate normals endpoint
        # We'll use the "climate" endpoint for monthly precipitation sum estimation (best-effort).
        climate_url = "https://climate-api.open-meteo.com/v1/climate"
        params = {"latitude": lat, "longitude": lon}
        r = requests.get(climate_url, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            cj = r.json()
            # try to compute annual rainfall from monthly means if available
            monthly = cj.get("monthly", {}).get("precipitation_sum", [])
            if monthly and len(monthly) >= 12:
                try:
                    annual = sum(float(x) for x in monthly[:12])
                    rainfall = float(round(annual, 1))
                except Exception:
                    rainfall = None
    except Exception:
        rainfall = None

    return ph, rainfall

# --- LLM call using REST to Gemini (X-Goog-Api-Key)
def call_gemini_once(prompt: str) -> str:
    """Call Gemini generateContent REST endpoint. Returns a text string or raises."""
    if not API_KEY:
        raise RuntimeError("No GOOGLE_API_KEY (Gemini) configured in .env.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    # allow non-200 to raise for clearer messages
    r.raise_for_status()
    resp = r.json()
    # Common structure: resp["candidates"][0]["content"] or resp["candidates"][0]["content"]["parts"][0]["text"]
    if "candidates" in resp and isinstance(resp["candidates"], list) and resp["candidates"]:
        cand = resp["candidates"][0]
        # try different shapes
        cont = cand.get("content")
        if isinstance(cont, dict) and "parts" in cont and isinstance(cont["parts"], list):
            return cont["parts"][0].get("text", "").strip()
        # sometimes content itself is a string
        if isinstance(cont, str):
            return cont.strip()
    # fallback: return raw json text
    return json.dumps(resp)

# --- Simple rule-based classifier as fallback
def rule_based_classify(features: dict) -> dict:
    soil = features.get("soil", "").lower()
    ph = features.get("ph", 6.5)
    rainfall = features.get("rainfall", 800.0)
    temp = features.get("temp", 25.0)

    preferred = ["loamy", "loamy soil", "loam", "clay", "sandy loam", "red soil", "black soil"]
    score = 0
    if any(p in soil for p in preferred):
        score += 1
    if 5.5 <= ph <= 7.5:
        score += 2
    elif 5.0 <= ph < 5.5 or 7.5 < ph <= 8.0:
        score += 1
    if rainfall >= 900:
        score += 2
    elif 500 <= rainfall < 900:
        score += 1
    if 10 <= temp <= 35:
        score += 1

    if score >= 5:
        priority = "High"
    elif score >= 3:
        priority = "Medium"
    else:
        priority = "Low"

    reason = f"Soil='{soil}', pH={ph}, rainfall={rainfall}mm"
    return {"priority": priority, "reason": reason, "recommendation": "", "commercial_advice": ""}

# --- Prompt builder for main recommendation (asks LLM to return JSON)
def build_recommendation_prompt(features: dict) -> str:
    prompt = f"""
You are an expert agronomist. Produce only valid JSON (no extra text) with keys:
- priority: one of "High","Medium","Low"
- suitability: "Yes" or "No"
- reason: one-sentence explanation
- recommendation: short bullet-list string of practical steps
- commercial_advice: short commercial tips (or empty)

User data:
Tree: {features.get('tree')}
Soil: {features.get('soil')}
Estimated soil pH: {features.get('ph')}
Estimated annual rainfall (mm): {features.get('rainfall')}
Average temperature (C): {features.get('temp')}
Purpose: {features.get('purpose')}
Land size (sq m): {features.get('land_size')}

Rules:
- Loamy/loam/clay and pH 5.5-7.5 favor planting.
- Rainfall >=900 mm increases suitability; <300 mm is low.
- If purpose is commercial and land_size >= 1000, include commercial tips.
Return only JSON.
"""
    return prompt.strip()

# --- Chat prompt wrapper (simple)
def build_chat_prompt(history: list, question: str) -> str:
    # history is a list of (user, assistant) tuples - we simply concatenate for a one-shot prompt
    chat = ""
    for u, a in history[-6:]:
        chat += f"User: {u}\nAssistant: {a}\n"
    chat += f"User: {question}\nAssistant:"
    return chat

# --- Input utilities
def normalize_soil_input(text: str) -> str:
    t = text.strip().lower()
    return SOIL_MAP.get(t, t)

def parse_rainfall_input(text: str):
    t = text.strip().lower()
    if not t:
        return None
    # if numeric mm
    try:
        # allow input like "1200", "1200 mm"
        num = float("".join(c for c in t if (c.isdigit() or c=='.')))
        return num
    except Exception:
        # map categories
        return RAINFALL_MAP.get(t, None)

def parse_land_size(text: str):
    t = text.strip().lower()
    if not t:
        return None
    try:
        if t.endswith("ac"):
            acres = float(t[:-2])
            return acres * 4046.86
        if t.endswith("ha"):
            ha = float(t[:-2])
            return ha * 10000.0
        # assume sq meters
        return float("".join(c for c in t if (c.isdigit() or c=='.')))
    except:
        return None

# --- Terminal UI & main flow
def collect_user_input():
    print("🌱 Tree Advisor — enter the details (press Enter to skip/use defaults)\n")
    tree = input("Tree name (e.g., Mango): ").strip() or "Mango"
    soil_raw = input("Soil type (e.g., 'lal mati', 'sandy', 'loamy'): ").strip() or "loamy"
    soil = normalize_soil_input(soil_raw)
    region = input("Region/City (e.g., Pune, India) — used to auto-fetch pH/rainfall if possible: ").strip()
    rainfall_raw = input("Annual rainfall (mm or 'low'/'moderate'/'high'): ").strip()
    rainfall_val = parse_rainfall_input(rainfall_raw) if rainfall_raw else None
    temp_raw = input("Average temperature (C) (optional): ").strip()
    try:
        temp = float(temp_raw) if temp_raw else 25.0
    except:
        temp = 25.0
    purpose = input("Purpose ('Personal' or 'Commercial'): ").strip() or "Personal"
    land_size_raw = input("Land size (sq meters or '2ac' for 2 acres): ").strip()
    land_size_val = parse_land_size(land_size_raw) if land_size_raw else None

    return {
        "tree": tree,
        "soil": soil,
        "soil_raw": soil_raw,
        "region": region,
        "rainfall_input": rainfall_raw,
        "rainfall": rainfall_val,
        "temp": temp,
        "purpose": purpose,
        "land_size": land_size_val
    }

def pretty_print_result(features: dict, result: dict):
    print("\n==== Tree Advisor Result ====")
    print(f"Tree: {features.get('tree')}")
    print(f"Soil (input): {features.get('soil_raw')} -> normalized: {features.get('soil')}")
    print(f"Region: {features.get('region')}")
    print(f"Estimated pH: {features.get('ph')}")
    print(f"Estimated annual rainfall (mm): {features.get('rainfall')}")
    print(f"Average temp (C): {features.get('temp')}")
    print(f"Purpose: {features.get('purpose')}")
    print(f"Land size (sq m): {features.get('land_size')}")
    print(f"\nPriority: {result.get('priority')}")
    print(f"Suitability: {result.get('suitability', 'N/A')}")
    print(f"Reason: {result.get('reason')}")
    print("\nRecommendations:")
    print(result.get('recommendation', '- None provided'))
    if result.get('commercial_advice'):
        print("\nCommercial advice:")
        print(result.get('commercial_advice'))
    print("=============================\n")

def main():
    features = collect_user_input()

    # If region provided and pH or rainfall missing, attempt to fetch
    ph_val = None
    rainfall_from_api = None
    if features.get("region"):
        print("\n🔎 Looking up location to auto-detect pH and rainfall (this may take a few seconds)...")
        coords = geocode_region(features["region"])
        if coords:
            lat, lon = coords
            print(f"Found coordinates: lat={lat:.4f}, lon={lon:.4f} — querying soil/climate data...")
            ph_val, rainfall_from_api = get_region_ph_and_rainfall(features["region"])
            if ph_val is not None:
                print(f"✔️ Estimated soil pH (from data): {ph_val}")
            else:
                print("⚠️ Could not determine pH from external data for this region.")
            if rainfall_from_api is not None:
                print(f"✔️ Estimated annual rainfall (mm): {rainfall_from_api}")
            else:
                print("⚠️ Could not determine rainfall from external data for this region.")
        else:
            print("⚠️ Could not geocode the region name. We'll use user inputs / defaults.")

    # Decide final pH and rainfall numeric values
    # If user provided explicit rainfall number, use it; else try API; else map category or default
    rainfall = features.get("rainfall")
    if rainfall is None:
        if rainfall_from_api is not None:
            rainfall = rainfall_from_api
        else:
            # If user typed 'low'/'medium' etc earlier, parse_rainfall_input would have filled it, but here final fallback:
            if features.get("rainfall_input"):
                rainfall = parse_rainfall_input(features.get("rainfall_input")) or 800.0
            else:
                rainfall = 800.0

    ph = ph_val if ph_val is not None else 6.5

    # fill missing land size default
    land_size = features.get("land_size") or 200.0

    # finalize features dict for model/prompt
    final_features = {
        "tree": features.get("tree"),
        "soil": features.get("soil"),
        "soil_raw": features.get("soil_raw"),
        "region": features.get("region"),
        "ph": ph,
        "rainfall": float(rainfall),
        "temp": float(features.get("temp", 25.0)),
        "purpose": features.get("purpose"),
        "land_size": float(land_size)
    }

    # Attempt LLM-based recommendation if API key available
    llm_result = None
    if API_KEY:
        try:
            prompt = build_recommendation_prompt(final_features)
            print("\n✨ Calling LLM for a tailored recommendation (Gemini)...")
            resp_text = call_gemini_once(prompt)
            # Attempt to extract JSON from the response text
            first = resp_text.find("{")
            if first != -1:
                json_text = resp_text[first:]
            else:
                json_text = resp_text
            parsed = json.loads(json_text)
            # ensure keys exist - fill defaults
            parsed.setdefault("priority", parsed.get("priority", "Medium"))
            parsed.setdefault("suitability", parsed.get("suitability", "Yes"))
            parsed.setdefault("reason", parsed.get("reason", "No reason provided."))
            parsed.setdefault("recommendation", parsed.get("recommendation", ""))
            parsed.setdefault("commercial_advice", parsed.get("commercial_advice", ""))
            llm_result = parsed
            print("✅ LLM returned a result.")
        except Exception as e:
            print(f"⚠️ LLM call failed or returned unexpected data: {e}")
            llm_result = None

    # If no LLM result, use rule-based fallback
    if llm_result is None:
        print("\n🔧 Using rule-based fallback to provide recommendation...")
        rb = rule_based_classify(final_features)
        # craft simple textual recs based on priority
        if rb["priority"] == "High":
            rec_text = "• Prepare land (clear weeds, loosen soil)\n• Plant during rainy season\n• Use mulch and monitor irrigation for 6 months"
            comm_text = "For commercial use, plan irrigation, adopt spacing for high yield, and research markets."
        elif rb["priority"] == "Medium":
            rec_text = "• Add compost and organic matter\n• Consider partial shade or agroforestry mix"
            comm_text = "Medium-scale possible with amendments and good management."
        else:
            rec_text = "• Consider more drought-tolerant species or soil improvement before planting."
            comm_text = "Low commercial viability; consider alternative crops or irrigation."

        llm_result = {
            "priority": rb["priority"],
            "suitability": "Yes" if rb["priority"] != "Low" else "No",
            "reason": rb["reason"],
            "recommendation": rec_text,
            "commercial_advice": comm_text
        }

    # Print final result
    pretty_print_result(final_features, llm_result)

   

if __name__ == "__main__":
    main()
