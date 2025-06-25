from typing import List, Dict, Any, Optional
from multi_agent_orchestrator.multi_agent_orchestrator.shared_libraries.helpers import execute_supabase_sql, sql_quote_value

async def list_vendors(filters: Optional[dict] = None) -> List[Dict[str, Any]]:
    """
    List all vendors, optionally filtered by category, city, or other fields.
    Args:
        filters (Optional[dict]): Filter fields (e.g., {"vendor_category": "Venue"}).
    Returns:
        list: List of vendor dicts, or an error dict.
    """
    sql = "SELECT * FROM vendors"
    params = {}
    if filters:
        where_clauses = []
        param_idx = 0
        for key, value in filters.items():
            param_name = f"val{param_idx}"
            param_idx += 1
            if key == "address->>'city'": # Special handling for JSONB query
                where_clauses.append(f"address->>'city' ILIKE :{param_name}")
                params[param_name] = f"%{value}%"
            else:
                # For other keys, ensure they are valid column names to prevent SQL injection
                # This example assumes direct column names; adjust if more complex keys are used.
                # A whitelist of filterable columns would be safer.
                safe_key = "".join(c if c.isalnum() or c == '_' else '' for c in key)
                if not safe_key: continue # Skip if key becomes empty after sanitizing

                where_clauses.append(f"{safe_key} ILIKE :{param_name}")
                params[param_name] = f"%{value}%"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

    result = await execute_supabase_sql(sql, params)
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and "error" in result: # Propagate error from execute_supabase_sql
        return result
    # If result is something else (e.g. unexpected dict), treat as empty or error
    # print(f"Unexpected result from list_vendors: {result}")
    return [] # Default to empty list if no error but not a list

async def get_vendor_details(vendor_id: str) -> Dict[str, Any]:
    """
    Get all details for a vendor by vendor_id.
    Args:
        vendor_id (str): The vendor's UUID.
    Returns:
        dict: Vendor data or {"error": <str>}
    """
    sql = "SELECT * FROM vendors WHERE vendor_id = :vendor_id LIMIT 1;"
    result = await execute_supabase_sql(sql, {"vendor_id": vendor_id})
    if isinstance(result, list) and result:
        return result[0]
    elif isinstance(result, dict) and "vendor_id" in result: # If it's already the flat dict
        return result
    return {"error": f"Vendor not found or unexpected result. Vendor ID: {vendor_id}. Result: {result}"}

async def search_vendors(
    category: Optional[str] = None,
    location: Optional[str] = None,
    budget_range: Optional[dict] = None,
    ratings: Optional[float] = None,
    keywords: Optional[list] = None,
) -> List[Dict[str, Any]]:
    """
    Search vendors based on various criteria, including full-text search.
    Args:
        category (str, optional): Vendor category.
        location (str, optional): Vendor location (city).
        budget_range (dict, optional): Budget range ({"min": float, "max": float}).
        ratings (float, optional): Minimum vendor rating.
        keywords (list, optional): List of keywords for full-text search.
    Returns:
        list: List of vendor dicts matching the criteria, or an error dict.
    """
    sql = "SELECT * FROM vendors" # Start with a base query
    params = {}
    where_clauses = []
    param_idx = 0

    def add_param(value: Any) -> str:
        nonlocal param_idx
        p_name = f"p{param_idx}"
        params[p_name] = value
        param_idx += 1
        return p_name

    if category:
        where_clauses.append(f"vendor_category ILIKE :{add_param(f'%{category}%')}")
    if location:
        # Assuming 'location' refers to city stored in address->>'city'
        where_clauses.append(f"address->>'city' ILIKE :{add_param(f'%{location}%')}")
    if budget_range:
        if "min" in budget_range and budget_range["min"] is not None:
            where_clauses.append(f"price >= :{add_param(budget_range['min'])}")
        if "max" in budget_range and budget_range["max"] is not None:
            where_clauses.append(f"price <= :{add_param(budget_range['max'])}")
    if ratings is not None: # Check for None explicitly for float
        where_clauses.append(f"rating >= :{add_param(ratings)}")

    # Full-text search using keywords
    if keywords:
        # Assuming keywords is a list of strings.
        # Ensure keywords are sanitized if they come directly from user input for to_tsquery
        # For simplicity, this example joins them. Consider tsvector on the column and plainto_tsquery for safety.
        keywords_str = " & ".join(k.strip() for k in keywords if k.strip())
        if keywords_str:
             where_clauses.append(f"fts_data @@ to_tsquery('english', :{add_param(keywords_str)})")

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    else: # No filters, select all (already default)
        pass

    result = await execute_supabase_sql(sql, params)
    if isinstance(result, list):
        return result
    elif isinstance(result, dict) and "error" in result:
        return result
    # print(f"Unexpected result from search_vendors: {result}")
    return []
