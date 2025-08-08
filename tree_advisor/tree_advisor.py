from main import (
    normalize_soil_input,
    parse_rainfall_input,
    parse_land_size,
    get_region_ph_and_rainfall,
    rule_based_classify,
    build_recommendation_prompt,
    call_gemini_once,
    API_KEY
)
import json

def run_tree_advisor(tree, soil_raw, rain_raw, region, land_raw, temperature, purpose):
    # Normalize soil
    soil = normalize_soil_input(soil_raw)

    # Parse rainfall
    rainfall_val = parse_rainfall_input(rain_raw) if rain_raw else None

    # Parse temperature
    try:
        temp = float(temperature) if temperature else 25.0
    except:
        temp = 25.0

    # Parse land size
    land_size_val = parse_land_size(land_raw) if land_raw else 200.0

    # Auto-fetch pH/rainfall if region provided
    ph_val = None
    rainfall_from_api = None
    if region:
        ph_val, rainfall_from_api = get_region_ph_and_rainfall(region)

    # Decide final pH
    ph = ph_val if ph_val is not None else 6.5

    # Decide final rainfall
    if rainfall_val is None:
        if rainfall_from_api is not None:
            rainfall_val = rainfall_from_api
        elif rain_raw:
            rainfall_val = parse_rainfall_input(rain_raw) or 800.0
        else:
            rainfall_val = 800.0

    # Final features
    final_features = {
        "tree": tree,
        "soil": soil,
        "soil_raw": soil_raw,
        "region": region,
        "ph": ph,
        "rainfall": float(rainfall_val),
        "temp": float(temp),
        "purpose": purpose,
        "land_size": float(land_size_val)
    }

    # Try LLM first
    llm_result = None
    if API_KEY:
        try:
            prompt = build_recommendation_prompt(final_features)
            resp_text = call_gemini_once(prompt)
            first = resp_text.find("{")
            json_text = resp_text[first:] if first != -1 else resp_text
            parsed = json.loads(json_text)
            parsed.setdefault("priority", "Medium")
            parsed.setdefault("suitability", "Yes")
            parsed.setdefault("reason", "No reason provided.")
            parsed.setdefault("recommendation", "")
            parsed.setdefault("commercial_advice", "")
            llm_result = parsed
        except Exception:
            llm_result = None

    # Fallback
    if llm_result is None:
        rb = rule_based_classify(final_features)
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

    # Format as display string
    output = (
        f"Priority: {llm_result['priority']}\n"
        f"Suitability: {llm_result['suitability']}\n"
        f"Reason: {llm_result['reason']}\n\n"
        f"Recommendations:\n{llm_result['recommendation']}\n\n"
        f"Commercial advice:\n{llm_result['commercial_advice']}"
    )
    return output.strip()

