# Budget Agent Utility (Supabase)
from typing import Dict, Any, List, Optional
from multi_agent_orchestrator.config import supabase  # Use supabase client from config.py


def set_user_budget(user_id: str, budget_min: str, budget_max: str) -> Dict[str, Any]:
    """
    Update the user's preferences JSONB in users table with budget_min and budget_max.  Handles potential errors.
    """
    try:
        budget_min = float(budget_min)
        budget_max = float(budget_max)
        preferences = {"budget_min": budget_min, "budget_max": budget_max}
        response = supabase.table("users").update({"preferences": preferences}).eq("user_id", user_id).execute()
        return response.data
    except ValueError:
        return {"error": "Invalid budget values. Please provide numbers."}


def get_user_budget(user_id: str) -> Optional[Dict[str, float]]:
    """
    Retrieve the user's budget_min and budget_max from preferences JSONB in users table.
    """
    response = supabase.table("users").select("preferences").eq("user_id", user_id).single().execute()
    if response.data and response.data.get("preferences"):
        return response.data["preferences"]
    return None


def add_budget_item(user_id: str, item_name: str, category: str, amount: float, vendor_name: str = None, status: str = "Pending") -> Dict[str, Any]:
    """
    Add a budget item for the user in budget_items table.
    """
    data = {
        "user_id": user_id,
        "item_name": item_name,
        "category": category,
        "amount": amount,
        "vendor_name": vendor_name,
        "status": status
    }
    response = supabase.table("budget_items").insert(data).execute()
    return response.data


def get_budget_items(user_id: str) -> List[Dict[str, Any]]:
    """
    Retrieve all budget items for a user from budget_items table.
    """
    response = supabase.table("budget_items").select("*").eq("user_id", user_id).execute()
    return response.data or []


def update_budget_item(item_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update a budget item by item_id. kwargs can include item_name, category, amount, vendor_name, status.
    """
    response = supabase.table("budget_items").update(kwargs).eq("item_id", item_id).execute()
    return response.data


def delete_budget_item(item_id: str) -> Dict[str, Any]:
    """
    Delete a budget item by item_id.
    """
    response = supabase.table("budget_items").delete().eq("item_id", item_id).execute()
    return response.data


def suggest_allocations(budget_min: float, budget_max: float) -> Dict[str, float]:
    """
    Suggest default budget allocations by category based on average of min/max.
    """
    total_budget = (budget_min + budget_max) / 2
    categories = ["venue", "catering", "decor", "photography", "entertainment", "attire", "misc"]
    splits = [0.3, 0.2, 0.15, 0.1, 0.1, 0.1, 0.05]
    return {cat: round(total_budget * split, 2) for cat, split in zip(categories, splits)}


# Example usage (for testing):
if __name__ == "__main__":
    user_id = "1b006058-1133-490c-b2de-90c444e56138"
    # Set user budget
    set_user_budget(user_id, 50000, 120000)
    print("User budget:", get_user_budget(user_id))
    # Suggest allocations
    allocations = suggest_allocations(50000, 120000)
    print("Suggested allocations:", allocations)
    # Add budget items
    for cat, amt in allocations.items():
        add_budget_item(user_id, f"{cat.title()} Budget", cat, amt)
    # List budget items
    print("Budget items:", get_budget_items(user_id))
