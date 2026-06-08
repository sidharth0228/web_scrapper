"""
enrichment.py
=============
Business Intelligence Enrichment Pipeline.
Adds metadata to scraped company records.
"""

def enrich_data(records: list[dict]) -> list[dict]:
    """
    Takes raw company records and enriches them with:
      - Company Type (Startup / Manufacturer)
      - Geographic Region
      - Technology Tags
      - Estimated Business Category
    """
    enriched = []
    
    for record in records:
        # Create a copy so we don't mutate the original in-place
        r = record.copy()
        
        industry = r.get("Industry / Category", "").lower()
        desc = r.get("Short Description", "").lower()
        loc = r.get("Location", "").lower()
        
        # 1. Company Type
        if "manufactur" in industry or "manufactur" in desc or "robotics" in industry or "automotive" in industry:
            r["Company Type"] = "Manufacturer"
        else:
            r["Company Type"] = "Startup"
            
        # 2. Geographic Region
        if any(c in loc for c in ["usa", "ca", "ny", "ma", "tx", "canada", "united states", "america"]):
            r["Geographic Region"] = "North America"
        elif any(c in loc for c in ["uk", "germany", "france", "london", "berlin", "paris", "europe"]):
            r["Geographic Region"] = "Europe"
        elif any(c in loc for c in ["china", "japan", "india", "singapore", "tokyo", "asia"]):
            r["Geographic Region"] = "Asia"
        else:
            r["Geographic Region"] = "Global"
            
        # 3. Technology Tags
        tags = []
        full_text = industry + " " + desc
        if "ai" in full_text or "machine learning" in full_text: tags.append("AI")
        if "robotic" in full_text: tags.append("Robotics")
        if "saas" in full_text: tags.append("SaaS")
        if "fintech" in full_text or "finance" in full_text: tags.append("FinTech")
        if "iot" in full_text or "internet of things" in full_text: tags.append("IoT")
        if "bio" in full_text or "med" in full_text: tags.append("HealthTech")
        
        r["Technology Tags"] = ", ".join(tags) if tags else "General"
        
        # 4. Estimated Business Category
        if "software" in full_text or "SaaS" in tags:
            r["Estimated Business Category"] = "Software Services"
        elif "Manufacturer" in r["Company Type"]:
            r["Estimated Business Category"] = "Hardware & Production"
        else:
            r["Estimated Business Category"] = "Emerging Tech"
            
        enriched.append(r)
        
    return enriched
