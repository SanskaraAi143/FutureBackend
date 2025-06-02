# Onboarding Agent Utility (Supabase)
from typing import Dict, Any
import os

# Import Supabase config from config.py
from config import supabase  # Use supabase client from config.py

def onboard_user(user_id: str, onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing user record in the users table with onboarding data.
    IMPORTANT: Only write to the following top-level fields: display_name, wedding_date, wedding_location, wedding_tradition, user_type. All other user attributes (e.g., caste, culture, region, budget, guest count, etc.) must be stored inside the preferences dictionary. Do NOT attempt to write any other fields at the top level.
    """
    # --- Agent-side validation: move non-schema fields to preferences ---
    USERS_TABLE_COLUMNS = {"user_id", "supabase_auth_uid", "email", "display_name", "created_at", "updated_at", "wedding_date", "wedding_location", "wedding_tradition", "preferences", "user_type"}
    preferences_update = onboarding_data.pop("preferences", None) or {}
    extra_prefs = {k: onboarding_data.pop(k) for k in list(onboarding_data.keys()) if k not in USERS_TABLE_COLUMNS}
    if extra_prefs:
        preferences_update.update(extra_prefs)
    if preferences_update:
        user_resp = supabase.table("users").select("preferences").eq("user_id", user_id).single().execute()
        current_prefs = user_resp.data.get("preferences") if user_resp and hasattr(user_resp, "data") else None
        if not isinstance(current_prefs, dict):
            current_prefs = {}
        current_prefs.update(preferences_update)
        onboarding_data["preferences"] = current_prefs
    response = supabase.table("users").update(onboarding_data).eq("user_id", user_id).execute()
    print(response)
    # The response is an APIResponse object, and response.data contains the updated row(s)
    if hasattr(response, "data") and response.data:
        return response.data[0]  # Return the updated user record
    else:
        raise Exception(f"Failed to update user onboarding data: {getattr(response, 'data', response)}")

# Example usage (for testing):
if __name__ == "__main__":
    user_id = "1b006058-1133-490c-b2de-90c444e56138"  # Replace with a real user_id from your users table
    onboarding_data = {
        "display_name": "Puneeth",
        "email": "kpuneeth714@gmail.com",
        "wedding_date": "2025-12-10",
        "wedding_location": "Bangalore",
        "wedding_tradition": "Traditional",
        "preferences": {"preferred_rituals": ["Haldi", "Mehendi", "Sangeet"]}
    }
    user_record = onboard_user(user_id, onboarding_data)
    print("User onboarded/updated:", user_record)
