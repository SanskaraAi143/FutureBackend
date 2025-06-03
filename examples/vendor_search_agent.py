# Vendor Search Agent Utility
from config import supabase
from typing import List, Dict, Any

def search_vendors(
    category: str = None,
    city: str = None,
    min_price: float = None,
    max_price: float = None,
    is_active: bool = True
) -> List[Dict[str, Any]]:
    """
    Search vendors in Supabase by category, city, and price range.
    """
    query = supabase.table("vendors").select("*")
    if category:
        query = query.eq("vendor_category", category)
    if is_active is not None:
        query = query.eq("is_active", is_active)
    if city:
        query = query.filter("address->>city", "eq", city)
    # Price filtering (if pricing_range is present)
    if min_price is not None:
        query = query.filter("pricing_range->>min", ">=", str(min_price))
    if max_price is not None:
        query = query.filter("pricing_range->>max", "<=", str(max_price))
    response = query.execute()
    data = response.data
    if not data:
        return [{"message": "No vendors found matching your criteria."}]
    return data

# Example usage (for testing):
if __name__ == "__main__":
    results = search_vendors(category="Venue", city="f")
    for vendor in results:
        print(vendor)
