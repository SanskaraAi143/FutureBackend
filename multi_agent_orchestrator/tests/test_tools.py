import pytest
import asyncio
import json

from multi_agent_orchestrator.tools.budget_tools import add_budget_item, get_budget_items, update_budget_item, delete_budget_item, execute_supabase_sql
from multi_agent_orchestrator.tools.timeline_tools import create_timeline_event, update_timeline_event, get_timeline_events
from multi_agent_orchestrator.tools.vendor_tools import list_vendors, get_vendor_details
from multi_agent_orchestrator.tools.user_tools import get_user_id, get_user_data,update_user_data


import uuid
from datetime import datetime, timezone



# Test config (replace with real test data as needed)
TEST_EMAIL = "kpuneeth714@gmail.com"
TEST_USER_ID = "fca04215-2af3-4a4e-bcfa-c27a4f54474c"
TEST_VENDOR_ID = "d1788d53-89db-4e8f-b616-a9ab5e2da723"

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
    updated = await update_budget_item(item_id, data={"amount": 4321})
    assert updated.get("data", {}).get("amount") in (4321, "4321.00", "4321")
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

@pytest.mark.asyncio
async def test_create_timeline_event():
    user_id = TEST_USER_ID
    event_data = {
        "event_name": "Sangeet",
        "event_date_time": "2024-08-03T18:00:00",
        "description": "Pre-wedding musical night",
        "location": "Grand Ballroom"
    }

    # Test successful event creation
    result = await create_timeline_event(user_id=user_id, event=event_data)
    assert result.get("status") == "success"
    assert result.get("data").get("event_name") == "Sangeet"
    assert result.get("data").get("description") == "Pre-wedding musical night"
    assert result.get("data").get("location") == "Grand Ballroom"

    # Test error handling - missing user_id
    result = await create_timeline_event(user_id="", event=event_data)
    assert result.get("status") == "error"
    assert "User ID is required" in result.get("error")

    # Test error handling - missing event_name
    event_data_missing_name = {
        "event_date_time": "2024-08-03T18:00:00",
        "description": "Pre-wedding musical night",
        "location": "Grand Ballroom"
    }
    result = await create_timeline_event(user_id=user_id, event=event_data_missing_name)
    assert result.get("status") == "error"
    assert "Missing required fields for timeline event." in result.get("error")

    # Test error handling - invalid event data type
    result = await create_timeline_event(user_id=user_id, event="not a dict")
    assert result.get("status") == "error"
    assert "Event data must be a dictionary" in result.get("error")

@pytest.mark.asyncio
async def test_update_timeline_event():
    # Create a test event first
    user_id = TEST_USER_ID
    event_data = {
        "event_name": "Test Event",
        "event_date_time": "2024-08-05T10:00:00",
        "description": "Test description",
        "location": "Test Location"
    }
    create_result = await create_timeline_event(user_id=user_id, event=event_data)
    assert create_result.get("status") == "success"
    event_id = create_result.get("data").get("event_id")
    print(f"Created event with ID: {event_id}")
    # Now update the event
    updates = {"event_name": "Updated Event Name", "description": "Updated description"}
    update_result = await update_timeline_event(event_id=event_id, updates=updates)
    print(f"Update result: {update_result}")
    assert update_result.get("status") == "success"
    assert update_result.get("data").get("event_name") == "Updated Event Name"
    assert update_result.get("data").get("description") == "Updated description"

    # Test updating event_date_time
    new_event_date_time = "2024-08-06T12:00:00"
    updates = {"event_date_time": new_event_date_time}
    update_result = await update_timeline_event(event_id=event_id, updates=updates)
    assert update_result.get("status") == "success"

    # Convert new_event_date_time to the expected format with timezone
    expected_event_date_time = datetime.fromisoformat(new_event_date_time).replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S+00")

    # Compare the event_date_time from the database result with the expected value
    actual_event_date_time = update_result.get("data").get("event_date_time")
    print(f"Actual event_date_time: {actual_event_date_time}")
    print(f"Expected event_date_time: {expected_event_date_time}")
    assert actual_event_date_time == expected_event_date_time

    # Test error handling - invalid event_id
    invalid_event_id = str(uuid.uuid4())
    updates = {"event_name": "Attempted Update"}
    update_result = await update_timeline_event(event_id=invalid_event_id, updates=updates)
    assert update_result.get("status") == "error"
    assert "Event not found or update failed." in update_result.get("error")
    print(f"Update result for invalid event ID: {update_result}")
    # Test error handling - missing event_id
    updates = {"event_name": "Attempted Update"}
    update_result = await update_timeline_event(event_id="", updates=updates)
    assert update_result.get("status") == "error"
    assert "Event ID is required." in update_result.get("error")
    print(f"Update result for missing event ID: {update_result}")
    # # Clean up the test event (optional, but good practice)
    # delete_sql = "DELETE FROM timeline_events WHERE event_id = :event_id;"
    # await execute_supabase_sql(delete_sql, {"event_id": event_id})


# asyncio.run(test_update_timeline_event())

@pytest.mark.asyncio
async def test_get_timeline_events():
    # Create a test event first
    user_id = TEST_USER_ID
    event_data = {
        "event_name": "Test Event",
        "event_date_time": "2024-08-05T10:00:00",
        "description": "Test description",
        "location": "Test Location"
    }
    create_result = await create_timeline_event(user_id=user_id, event=event_data)
    assert create_result.get("status") == "success"

    # Get the timeline events for the user
    events = await get_timeline_events(user_id=user_id)
    assert isinstance(events, list)
    assert len(events) > 0

    # Check if at least one event has the correct user_id and event_name
    found = False
    for event in events:
        if event.get("user_id") == user_id and event.get("event_name") == "Test Event":
            found = True
            break
    assert found, "No event with the correct user_id and event_name found."

    # Test error handling - missing user_id
    events = await get_timeline_events(user_id="")
    assert isinstance(events, dict)
    assert events.get("status") == "error"
    assert "User ID is required." in events.get("error")

    # Clean up the test event (optional, but good practice)
    event_id = create_result.get("data").get("event_id")
    delete_sql = "DELETE FROM timeline_events WHERE event_id = :event_id;"
    await execute_supabase_sql(delete_sql, {"event_id": event_id})
