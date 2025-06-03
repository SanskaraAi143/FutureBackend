import pytest
import asyncio
from .tools import (
    get_user_id, get_user_data, update_user_data, list_vendors, get_vendor_details,
    add_budget_item, get_budget_items, update_budget_item, delete_budget_item,execute_supabase_sql,
)

# Test config (replace with real test data as needed)
TEST_EMAIL = "kpuneeth714@gmail.com"
TEST_USER_ID = "1b006058-1133-490c-b2de-90c444e56138"
TEST_VENDOR_ID = "4b32c609-eb0a-4129-9f4f-a4a76b214cbe"

@pytest.mark.asyncio
async def test_get_user_id():
    result = await get_user_id(TEST_EMAIL)
    assert "user_id" in result

@pytest.mark.asyncio
async def test_get_user_data():
    result = await get_user_data(TEST_USER_ID)
    assert result.get("user_id") == TEST_USER_ID

@pytest.mark.asyncio
async def test_update_user_data():
    update = {"display_name": "Pytest User", "preferences": {"pytest": True}}
    result = await update_user_data(TEST_USER_ID, update)
    assert result.get("display_name") == "Pytest User"
    assert result.get("preferences", {}).get("pytest") is True

@pytest.mark.asyncio
async def test_list_vendors():
    vendors = await list_vendors({"vendor_category": "Venue"})
    assert isinstance(vendors, list)
    assert any("vendor_name" in v for v in vendors)

@pytest.mark.asyncio
async def test_get_vendor_details():
    vendor = await get_vendor_details(TEST_VENDOR_ID)
    assert vendor.get("vendor_id") == TEST_VENDOR_ID

@pytest.mark.asyncio
async def test_budget_item_crud():
    # Add
    item = {"item": "Pytest Item", "category": "Decor", "amount": 1234}
    added = await add_budget_item(TEST_USER_ID, item)
    assert added.get("item_name") == "Pytest Item"
    item_id = added.get("item_id")
    # List
    items = await get_budget_items(TEST_USER_ID)
    assert any(i["item_id"] == item_id for i in items)
    # Update
    updated = await update_budget_item(item_id, amount=4321)
    assert updated.get("amount") in (4321, "4321.00", "4321")
    # Delete
    deleted = await delete_budget_item(item_id)
    assert deleted.get("status") == "success"

@pytest.mark.asyncio
async def test_custom_query():
    sql = f"SELECT * FROM users WHERE user_id = '{TEST_USER_ID}'"
    result = await execute_supabase_sql(sql)
    if isinstance(result, dict) and result.get("rows"):
        assert any(r["user_id"] == TEST_USER_ID for r in result["rows"])
    elif isinstance(result, list):
        assert any(r["user_id"] == TEST_USER_ID for r in result)
    else:
        pytest.fail("custom_query did not return expected result")
