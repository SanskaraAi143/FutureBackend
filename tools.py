# tools.py - Custom tools for ADK agents to interact with Supabase and Astra DB

from typing import List, Dict, Any, Optional
from .config import supabase, astra_db # Import configured clients
import json

# --- Supabase Tools ---

# coustom query for interacting with Supabase
def get_user_id(email: str) -> Dict[str, Any]:
    """
    Retrieves user_id from the 'users' table by email.

    Args:
        email (str): The email address of the user.

    Returns:
        Dict[str, Any]: A dictionary containing user_id if found, otherwise an error message.
    """
    try:
        response = supabase.table("users").select("user_id").eq("email", email).single().execute()
        if hasattr(response, "data") and response.data:
            return response.data
        else:
            return {"error": "User not found."}
    except Exception as e:
        return {"error": f"Error fetching user_id: {e}"}
    
def get_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves user data from the 'users' table by user_id.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing user data if found, otherwise None.  Returns an error message if there's an issue with the database query.
    """
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).single().execute()
        if hasattr(response, "data") and response.data:
            return response.data
        else:
            return None # User not found
    except Exception as e:
        return {"error": f"Error fetching user data: {e}"}


def update_user_data(user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Updates user data in the 'users' table. Handles merging preferences. Automatically moves non-schema fields into preferences."""
    """users table schema:  
    TABLE users (
        user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        supabase_auth_uid UUID UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        display_name TEXT,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now(),
        wedding_date DATE,
        wedding_location TEXT,
        wedding_tradition TEXT,
        preferences JSONB DEFAULT '{}',
        user_type TEXT CHECK (user_type IN ('couple', 'vendor', 'guest')) DEFAULT 'couple'
        );"""
    # List of top-level columns in the users table
    USERS_TABLE_COLUMNS = {
        "user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at",
        "wedding_date", "wedding_location", "wedding_tradition", "preferences", "user_type"
    }
    # Separate out fields that are not top-level columns (should go in preferences)
    preferences_update = data.pop("preferences", None) or {}
    extra_prefs = {k: data.pop(k) for k in list(data.keys()) if k not in USERS_TABLE_COLUMNS}
    if extra_prefs:
        preferences_update.update(extra_prefs)
    if preferences_update:
        response = supabase.table("users").select("preferences").eq("user_id", user_id).single().execute()
        current_prefs = response.data.get("preferences") if response and hasattr(response, "data") else {}
        if not isinstance(current_prefs, dict):
            current_prefs = {}
        current_prefs.update(preferences_update)
        data["preferences"] = current_prefs
    try:
        response = supabase.table("users").update(data).eq("user_id", user_id).execute()
        if hasattr(response, "data") and response.data:
            return response.data[0]
        else:
            return {"error": "Update failed. No data returned."}
    except Exception as e:
        return {"error": f"Error updating user data: {e}"}


def list_vendors(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Lists vendors, applying filters if provided."""
    """vendors table schema:
    TABLE vendors (
    vendor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_name VARCHAR(255) NOT NULL,
    vendor_category VARCHAR(100) NOT NULL, -- 'Venue', 'Photographer', etc.
    contact_email VARCHAR(255),
    phone_number VARCHAR(50),
    website_url TEXT,
    address JSONB, -- {"full_address": "", "city": "", ...}
    pricing_range JSONB, -- {"min": 5000, "max": 15000, ...}
    rating FLOAT CHECK (rating >= 0 AND rating <= 5),
    description TEXT,
    details JSONB, -- Additional details 
    portfolio_image_urls TEXT[], -- URLs to Supabase Storage
    is_active BOOLEAN DEFAULT true,
    supabase_auth_uid UUID UNIQUE NULL REFERENCES auth.users(id), -- Supabase Auth ID of primary vendor owner/admin
    is_verified BOOLEAN DEFAULT false, -- For platform admins to verify vendors
    commission_rate DECIMAL(5,2) DEFAULT 0.05, -- Platform's commission rate for this vendor
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
); """
    query = supabase.table("vendors").select("*")
    if filters:
        for key, value in filters.items():
            if key == "address->>'city'":
                query = query.ilike("address->>city", f"%{value}%")
            else:
                query = query.ilike(key, f"%{value}%")
    try:
        response = query.execute()
        return response.data or []
    except Exception as e:
        return {"error": f"Error listing vendors: {e}"}



def get_vendor_details(vendor_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves vendor details by vendor_id."""
    """vendors table schema:
    TABLE vendors (
    vendor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_name VARCHAR(255) NOT NULL,
    vendor_category VARCHAR(100) NOT NULL, -- 'Venue', 'Photographer', etc.
    contact_email VARCHAR(255),
    phone_number VARCHAR(50),
    website_url TEXT,
    address JSONB, -- {"full_address": "", "city": "", ...}
    pricing_range JSONB, -- {"min": 5000, "max": 15000, ...}
    rating FLOAT CHECK (rating >= 0 AND rating <= 5),
    description TEXT,
    details JSONB, -- Additional details 
    portfolio_image_urls TEXT[], -- URLs to Supabase Storage
    is_active BOOLEAN DEFAULT true,
    supabase_auth_uid UUID UNIQUE NULL REFERENCES auth.users(id), -- Supabase Auth ID of primary vendor owner/admin
    is_verified BOOLEAN DEFAULT false, -- For platform admins to verify vendors
    commission_rate DECIMAL(5,2) DEFAULT 0.05, -- Platform's commission rate for this vendor
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    try:
        response = supabase.table("vendors").select("*").eq("vendor_id", vendor_id).single().execute()
        if hasattr(response, "data") and response.data:
            return response.data
        else:
            return None # Vendor not found
    except Exception as e:
        return {"error": f"Error fetching vendor details: {e}"}


def add_budget_item(user_id: str, item: Dict[str, Any], vendor_name: Optional[str] = None, status: str = "Pending") -> Dict[str, Any]:
    """Adds a budget item."""
    """budget_items table schema:
    TABLE budget_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    vendor_name TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    data = {
        "user_id": user_id,
        "item_name": item.get("item"),
        "category": item.get("category"),
        "amount": item.get("amount"),
        "vendor_name": vendor_name,
        "status": status
    }
    try:
        response = supabase.table("budget_items").insert(data).execute()
        if hasattr(response, "data") and response.data:
            return response.data[0]
        else:
            return {"error": "Adding budget item failed. No data returned."}
    except Exception as e:
        return {"error": f"Error adding budget item: {e}"}


def get_budget_items(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all budget items for a user."""
    """budget_items table schema:
    TABLE budget_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    vendor_name TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    try:
        response = supabase.table("budget_items").select("*").eq("user_id", user_id).execute()
        return response.data or []
    except Exception as e:
        return {"error": f"Error getting budget items: {e}"}


def update_budget_item(item_id: str, **kwargs) -> Dict[str, Any]:
    """Updates a budget item."""
    """TABLE budget_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    vendor_name TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    try:
        response = supabase.table("budget_items").update(kwargs).eq("item_id", item_id).execute()
        if hasattr(response, "data") and response.data:
            return response.data[0]
        else:
            return {"error": "Updating budget item failed. No data returned."}
    except Exception as e:
        return {"error": f"Error updating budget item: {e}"}


def delete_budget_item(item_id: str) -> Dict[str, Any]:
    """Deletes a budget item."""
    """budget_items table schema:
    TABLE budget_items (
    item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    vendor_name TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);"""
    try:
        response = supabase.table("budget_items").delete().eq("item_id", item_id).execute()
        return {"status": "success"} if hasattr(response, "data") and response.data else {"error": "Deletion failed."}
    except Exception as e:
        return {"error": f"Error deleting budget item: {e}"}


# --- Astra DB Tools ---

def search_rituals(question: str) -> List[Dict[str, Any]]:
    """
    Searches for rituals in Astra DB using vector search.  Returns top 3 most relevant documents.  Handles CollectionExceptions.
    """
    """ input: question - a string containing the user's query about rituals"""
    try:
        ritual_data = astra_db.get_collection("ritual_data")
        result = ritual_data.find(
            projection={"$vectorize": True},
            sort={"$vectorize": question},
            limit=3
            
        )
        contexts = [doc for doc in result]
        return contexts
    except Exception as e:
        return {"error": f"An unexpected error occurred during ritual search: {e}"}



# Example usage (for testing):
if __name__ == "__main__":
    # Replace with real IDs and data for testing
    test_user_id = "1b006058-1133-490c-b2de-90c444e56138"
    test_vendor_id = "4b32c609-eb0a-4129-9f4f-a4a76b214cbe"
    test_budget_item_id = "ca42fe02-ac69-450b-952b-e9674a475697"
    test_question = "Describe the Haldi ceremony"
    test_user_uuid="1b006058-1133-490c-b2de-90c444e56138"
    test_vector_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] # Replace with a real embedding
    # print("Testing get_user_id...")
    email = "kpuneeth714@gmail.com"
    print(get_user_id(email))
    # print("Testing get_user_data...")
    # print(get_user_data(test_user_id))

    test_user_uuid="1b006058-1133-490c-b2de-90c444e56138"
    print("\nTesting update_user_data...")
    print(update_user_data(test_user_id, {
        "display_name": "Test User",
        "wedding_date": "2024-12-31",
        "wedding_location": "Test Location",
        "wedding_tradition": "Test Tradition",
        "preferences": {
            "vendor_preferences": {
                "Venue": ["Test Venue"],
                "Catering": ["Test Catering"]
            }
        }
    }))

    # print("\nTesting list_vendors...")
    # print(list_vendors({"vendor_category": "Venue"}))

    # print("\nTesting get_vendor_details...")
    # print(get_vendor_details(test_vendor_id))

    # print("\nTesting add_budget_item...")
    # print(add_budget_item(test_user_id, "Test Item", "Decor", 1000))

    # print("\nTesting get_budget_items...")
    # print(get_budget_items(test_user_id))

    # print("\nTesting update_budget_item...")
    # print(update_budget_item(test_budget_item_id, amount=1500))

    # print("\nTesting delete_budget_item...")
    # print(delete_budget_item(test_budget_item_id))

    # print("\nTesting search_rituals...")
    # print(search_rituals(test_question))

    print("\nTesting custom query...")
    #custom_query = "SELECT * FROM users where email = 'kpuneeth714@gmail.com'"
    #print(coustom_query(custom_query))
