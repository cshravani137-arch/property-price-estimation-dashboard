"""Regenerate the synthetic multi-city dataset used by the dashboard.

This creates educational demo rows, not genuine historic property transactions.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "data" / "raw" / "india_property_sample.csv"

CITY_CONFIG = {
    "Mumbai": {"rate": 15500, "cities": {"Premium": ["Bandra West", "Powai", "Andheri West"], "Mid-Range": ["Kharghar", "Thane West", "Goregaon East"], "Affordable": ["Mira Road", "Virar", "Panvel"]}},
    "Delhi": {"rate": 7800, "cities": {"Premium": ["Vasant Kunj", "Dwarka Sector 10", "Greater Kailash"], "Mid-Range": ["Rohini", "Mayur Vihar", "Janakpuri"], "Affordable": ["Uttam Nagar", "Burari", "Narela"]}},
    "Bengaluru": {"rate": 8500, "cities": {"Premium": ["Indiranagar", "Whitefield", "Koramangala"], "Mid-Range": ["Yelahanka", "Hebbal", "Electronic City"], "Affordable": ["Hoskote", "Kengeri", "Bommasandra"]}},
    "Hyderabad": {"rate": 7600, "cities": {"Premium": ["Banjara Hills", "Gachibowli", "Jubilee Hills"], "Mid-Range": ["Miyapur", "Kondapur", "Manikonda"], "Affordable": ["Kompally", "LB Nagar", "Uppal"]}},
    "Chennai": {"rate": 7200, "cities": {"Premium": ["Adyar", "Anna Nagar", "OMR"], "Mid-Range": ["Velachery", "Porur", "Sholinganallur"], "Affordable": ["Avadi", "Poonamallee", "Tambaram"]}},
    "Pune": {"rate": 7400, "cities": {"Premium": ["Koregaon Park", "Baner", "Viman Nagar"], "Mid-Range": ["Wakad", "Hinjawadi", "Kharadi"], "Affordable": ["Chakan", "Moshi", "Undri"]}},
    "Ahmedabad": {"rate": 5200, "cities": {"Premium": ["Satellite", "Bodakdev", "Prahlad Nagar"], "Mid-Range": ["Chandkheda", "Bopal", "Vastrapur"], "Affordable": ["Naroda", "Nikol", "Vatva"]}},
    "Kolkata": {"rate": 5200, "cities": {"Premium": ["Ballygunge", "Salt Lake", "New Town"], "Mid-Range": ["Behala", "Dum Dum", "Rajarhat"], "Affordable": ["Barasat", "Sonarpur", "Joka"]}},
    "Jaipur": {"rate": 4600, "cities": {"Premium": ["Malviya Nagar", "Vaishali Nagar", "Jagatpura"], "Mid-Range": ["Mansarovar", "Ajmer Road", "Sirsi Road"], "Affordable": ["Sanganer", "Kalwar Road", "Vidhyadhar Nagar"]}},
    "Chandigarh": {"rate": 6500, "cities": {"Premium": ["Sector 8", "Sector 9", "Sector 17"], "Mid-Range": ["Sector 44", "Sector 49", "Zirakpur"], "Affordable": ["Kharar", "Landran", "Dera Bassi"]}},
}
CITY_MULT = {"Mumbai": 1.40, "Delhi": 1.15, "Bengaluru": 1.08, "Hyderabad": 1.00, "Chennai": .96, "Pune": .98, "Ahmedabad": .88, "Kolkata": .86, "Jaipur": .82, "Chandigarh": 1.00}
LOCALITY_MULT = {"Premium": 1.52, "Mid-Range": 1.0, "Affordable": .72}
PROPERTY_MULT = {"Apartment": 1.0, "Independent House": 1.06, "Villa": 1.24, "Builder Floor": 1.03}
FURNISH_MULT = {"Unfurnished": 1.0, "Semi-Furnished": 1.035, "Furnished": 1.075}


def main():
    rng = np.random.default_rng(20261014)
    rows = []
    for city, config in CITY_CONFIG.items():
        for _ in range(140):
            tier = str(rng.choice(["Premium", "Mid-Range", "Affordable"], p=[.22, .48, .30]))
            locality = str(rng.choice(config["cities"][tier]))
            area = int(np.clip(rng.normal(1050, 420), 300, 3200) // 10 * 10)
            bhk = int(np.clip(round(area / 520 + rng.normal(0, .45)), 1, 6))
            bathrooms = int(np.clip(bhk + rng.choice([-1, 0, 0, 1]), 1, 5))
            age = int(rng.integers(0, 26))
            year = int(rng.integers(2018, 2027))
            property_type = str(rng.choice(["Apartment", "Independent House", "Villa", "Builder Floor"], p=[.65, .17, .10, .08]))
            furnishing = str(rng.choice(["Unfurnished", "Semi-Furnished", "Furnished"], p=[.38, .42, .20]))
            parking = int(rng.choice([0, 1], p=[.28, .72]))
            lift = int(property_type in ["Apartment", "Builder Floor"] and rng.choice([0, 1], p=[.18, .82]))
            gated = int(rng.choice([0, 1], p=[.43, .57]))
            gym = int(rng.choice([0, 1], p=[.55, .45]))
            pool = int(rng.choice([0, 1], p=[.77, .23]))
            amenities = parking + lift + gated + gym + pool
            amenity_mult = 1 + parking*.025 + lift*.018 + gated*.03 + gym*.012 + pool*.018
            age_mult = max(.77, 1 - .008*age)
            year_mult = 1 + (year - 2020)*.055
            rate = config["rate"] * CITY_MULT[city] * LOCALITY_MULT[tier]
            price_inr = area * rate * PROPERTY_MULT[property_type] * FURNISH_MULT[furnishing] * amenity_mult * age_mult * year_mult * rng.normal(1.0, .10)
            rows.append({
                "record_id": f"DEMO-{len(rows)+1:05d}", "city": city, "locality": locality, "locality_tier": tier,
                "property_type": property_type, "area_sqft": area, "bhk": bhk, "bathrooms": bathrooms,
                "age_years": age, "sale_year": year, "furnishing_status": furnishing, "parking": parking,
                "lift": lift, "gated_community": gated, "gym": gym, "swimming_pool": pool,
                "amenities_count": amenities, "price_lakhs": round(float(np.clip(price_inr/100000, 12, 950)), 2),
                "data_type": "Synthetic demo record",
            })
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(TARGET, index=False)
    print(f"Created {len(rows):,} synthetic demo records across {len(CITY_CONFIG)} cities: {TARGET}")
    print("Reminder: these are educational mock records, not actual transactions.")


if __name__ == "__main__":
    main()
