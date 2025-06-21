# src/core/schemas.py
"""
Pydantic models for data validation and schema enforcement.
These models can be used for:
- Validating API request/response data.
- Validating data retrieved from databases.
- Ensuring consistent data structures throughout the application.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import datetime

# --- User Schemas ---
class UserPreferences(BaseModel):
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    culture: Optional[str] = None
    caste: Optional[str] = None
    region: Optional[str] = None
    guest_count: Optional[int] = None
    # Add other preference fields as needed

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    wedding_date: Optional[datetime] = None
    wedding_location: Optional[str] = None
    wedding_tradition: Optional[str] = None
    user_type: Optional[str] = "bride_or_groom" # Example default
    preferences: Optional[UserPreferences] = Field(default_factory=UserPreferences)

class UserCreate(UserBase):
    supabase_auth_uid: Optional[str] = None # If you link to Supabase Auth

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    wedding_date: Optional[datetime] = None
    wedding_location: Optional[str] = None
    wedding_tradition: Optional[str] = None
    user_type: Optional[str] = None
    preferences: Optional[UserPreferences] = None # Allow partial updates to preferences

class UserInDB(UserBase):
    user_id: str # Typically UUID
    created_at: datetime
    updated_at: datetime
    supabase_auth_uid: Optional[str] = None

    class Config:
        orm_mode = True # For compatibility with ORM models if used

# --- Budget Schemas ---
class BudgetItemBase(BaseModel):
    item_name: str
    category: str
    amount: float
    vendor_name: Optional[str] = None
    status: Optional[str] = "Pending"

class BudgetItemCreate(BudgetItemBase):
    user_id: str # UUID

class BudgetItemUpdate(BaseModel):
    item_name: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    vendor_name: Optional[str] = None
    status: Optional[str] = None

class BudgetItemInDB(BudgetItemBase):
    item_id: str # UUID
    user_id: str # UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Vendor Schemas ---
class VendorAddress(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None

class VendorBase(BaseModel):
    vendor_name: str
    vendor_category: str # E.g., "Venue", "Catering", "Photography"
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    website: Optional[HttpUrl] = None
    address: Optional[VendorAddress] = Field(default_factory=VendorAddress)
    description: Optional[str] = None
    # Add other common vendor fields

class VendorInDB(VendorBase):
    vendor_id: str # UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Ritual Schemas ---
class RitualBase(BaseModel):
    ritual_name: str
    description: str
    culture: Optional[str] = None # E.g., "South Indian", "Punjabi"
    region: Optional[str] = None
    # Add other ritual-specific fields

class RitualInDB(RitualBase):
    ritual_id: str # Or some other unique identifier
    # Potentially embedding vectors or other search-related fields if managed here
    # For AstraDB vector search, the schema might be more about the data structure
    # you expect back from the search, rather than defining the table itself.

    class Config:
        orm_mode = True


# --- Timeline Schemas ---
class TimelineEventBase(BaseModel):
    event_name: str
    event_date_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None

class TimelineEventCreate(TimelineEventBase):
    user_id: str # UUID

class TimelineEventUpdate(BaseModel):
    event_name: Optional[str] = None
    event_date_time: Optional[datetime] = None
    description: Optional[str] = None
    location: Optional[str] = None

class TimelineEventInDB(TimelineEventBase):
    event_id: str # UUID
    user_id: str # UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Tooling specific Schemas (Example) ---
class SupabaseExecutionResult(BaseModel):
    rows: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    # Could be more specific based on typical Supabase MCP output

# You can add more schemas as needed for different data entities
# or for specific request/response bodies of your tools/services.

if __name__ == "__main__":
    # Example usage:
    user_data = {
        "email": "test@example.com",
        "display_name": "Test User",
        "preferences": {"budget_min": 10000, "culture": "Generic"}
    }
    try:
        user = UserBase(**user_data)
        print("User schema validation successful:")
        print(user.model_dump_json(indent=2))

        invalid_user_data = {"email": "not-an-email"}
        # UserBase(**invalid_user_data) # This would raise a ValidationError
    except Exception as e:
        print(f"Schema validation error: {e}")
