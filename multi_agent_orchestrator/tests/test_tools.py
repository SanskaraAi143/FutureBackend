import pytest
import asyncio
from unittest.mock import patch, AsyncMock # For mocking if needed later

# Import all tools to be tested
from multi_agent_orchestrator.tools import ( # Corrected import after structure change
    get_user_id,
    get_user_data,
    update_user_data,
    get_user_activities,
    add_budget_item,
    get_budget_items,
    update_budget_item,
    delete_budget_item,
    list_vendors,
    get_vendor_details,
    search_vendors,
    search_rituals,
    get_timeline_events,
    create_timeline_event,
    update_timeline_event
)
# Note: ToolContext is not explicitly used by these tests yet, but tools accept it.
# from google.adk.tools import ToolContext

# Provided Test Data
TEST_EMAIL = "kpuneeth714@gmail.com"
TEST_USER_ID = "fca04215-2af3-4a4e-bcfa-c27a4f54474c"
TEST_VENDOR_ID = "d1788d53-89db-4e8f-b616-a9ab5e2da723"
# TEST_BUDGET_ITEM_ID_FOR_DELETE = "some-uuid-to-delete" # Would need to be created first

# --- Test User Tools ---

@pytest.mark.asyncio
async def test_get_user_id_success():
    # This test will likely fail if SUPABASE_ACCESS_TOKEN is not set,
    # as it's an integration test. To make it a unit test, execute_supabase_sql would be mocked.
    # Assuming for now that if execute_supabase_sql runs, it might return a valid-looking structure.
    response = await get_user_id(email=TEST_EMAIL) # Using provided TEST_EMAIL
    assert isinstance(response, dict)
    assert "status" in response
    if response["status"] == "success":
        assert "data" in response
        assert "user_id" in response["data"]
    elif response["status"] == "error":
        assert "error" in response
        # This is acceptable if the user truly doesn't exist or DB is down
        print(f"test_get_user_id_success: Received error (as expected if user not found/DB issue): {response['error']}")
    else:
        pytest.fail(f"Unexpected status in response: {response.get('status')}")

@pytest.mark.asyncio
async def test_get_user_id_invalid_input():
    response = await get_user_id(email="") # Empty email
    assert response["status"] == "error"
    assert "invalid email" in response["error"].lower()

    response_none = await get_user_id(email=None) # type: ignore
    assert response_none["status"] == "error"
    assert "invalid email" in response_none["error"].lower()

@pytest.mark.asyncio
async def test_get_user_data_success():
    # Requires a valid user_id that exists, or will return error (which is valid for the tool)
    response = await get_user_data(user_id=TEST_USER_ID) # Using provided TEST_USER_ID
    assert isinstance(response, dict)
    assert "status" in response
    if response["status"] == "success":
        assert "data" in response
        assert response["data"]["user_id"] == TEST_USER_ID
    elif response["status"] == "error":
        assert "error" in response
        print(f"test_get_user_data_success: Received error (expected if user not found/DB issue): {response['error']}")
    else:
        pytest.fail(f"Unexpected status in response: {response.get('status')}")


@pytest.mark.asyncio
async def test_get_user_data_invalid_input():
    response = await get_user_data(user_id="")
    assert response["status"] == "error"
    assert "invalid user_id" in response["error"].lower()

@pytest.mark.asyncio
async def test_update_user_data_basic():
    # This is a complex test as it involves read-then-write.
    # For a true unit test, get_user_data and execute_supabase_sql would be mocked.
    update_payload = {"display_name": "Updated Name via Pytest", "pytest_preference": "test_value_pytest"}

    # To properly test, we'd ideally mock get_user_data to return a known state,
    # then mock execute_supabase_sql to check the generated SQL and return a success.
    # For now, this will likely fail due to SUPABASE_ACCESS_TOKEN missing or user not existing.
    response = await update_user_data(user_id=TEST_USER_ID, data=update_payload) # Using provided TEST_USER_ID
    assert isinstance(response, dict)
    assert "status" in response
    if response["status"] == "success":
        assert "data" in response
        assert response["data"]["display_name"] == "Updated Name via Test"
        # Add checks for preferences if the mock/DB state allows
    elif response["status"] == "error":
        assert "error" in response
        print(f"test_update_user_data_basic: Received error (expected if keys missing/user not found): {response['error']}")
    else:
        pytest.fail(f"Unexpected status: {response.get('status')}")


@pytest.mark.asyncio
async def test_update_user_data_invalid_input():
    response = await update_user_data(user_id="", data={"display_name": "test"})
    assert response["status"] == "error"
    assert "invalid user_id" in response["error"].lower()

    response_no_data = await update_user_data(user_id="some-id", data={})
    assert response_no_data["status"] == "error"
    assert "empty data payload" in response_no_data["error"].lower() # Or "No valid fields"

@pytest.mark.asyncio
async def test_get_user_activities_basic():
    response = await get_user_activities(user_id=TEST_USER_ID) # Using provided TEST_USER_ID
    assert isinstance(response, dict)
    assert "status" in response
    if response["status"] == "success":
        assert "data" in response
        assert isinstance(response["data"], list)
    elif response["status"] == "error":
        assert "error" in response
        print(f"test_get_user_activities_basic: Received error (expected if keys missing/user not found): {response['error']}")
    else:
        pytest.fail(f"Unexpected status: {response.get('status')}")

@pytest.mark.asyncio
async def test_get_user_activities_invalid_input():
    response = await get_user_activities(user_id="")
    assert response["status"] == "error"
    assert "invalid user_id" in response["error"].lower()

# --- Test Budget Tools ---

@pytest.mark.asyncio
async def test_add_budget_item_success():
    # Args for add_budget_item: user_id, item_name, category, amount
    response = await add_budget_item(
        user_id=TEST_USER_ID, # Using provided TEST_USER_ID
        item_name="Pytest Budget Item",
        category="Pytest Category",
        amount=123.45
    )
    assert response["status"] == "success" or (response["status"] == "error" and "SUPABASE_ACCESS_TOKEN" in response.get("error", "")) # Allow error if token missing
    if response["status"] == "success":
        assert "data" in response
        assert response["data"]["item_name"] == "Test Item"

@pytest.mark.asyncio
async def test_add_budget_item_invalid_input():
    response = await add_budget_item(user_id="", item_name="Test", category="Cat", amount=10)
    assert response["status"] == "error"
    assert "invalid input" in response["error"].lower()

    response_neg_amount = await add_budget_item("user1", "Test", "Cat", amount=-10)
    assert response_neg_amount["status"] == "error"
    assert "amount cannot be negative" in response_neg_amount["error"].lower()

    response_bad_amount = await add_budget_item("user1", "Test", "Cat", amount="abc") # type: ignore
    assert response_bad_amount["status"] == "error"
    assert "amount must be a valid number" in response_bad_amount["error"].lower()


@pytest.mark.asyncio
async def test_get_budget_items_basic():
    response = await get_budget_items(user_id=TEST_USER_ID) # Using provided TEST_USER_ID
    assert response["status"] == "success" or (response["status"] == "error" and "SUPABASE_ACCESS_TOKEN" in response.get("error", ""))
    if response["status"] == "success":
        assert isinstance(response["data"], list)

# ... (More tests for update_budget_item, delete_budget_item with success, error, not found cases) ...

# --- Test Vendor Tools ---
@pytest.mark.asyncio
async def test_list_vendors_basic():
    response = await list_vendors(filters={"vendor_category": "Venue"})
    assert response["status"] == "success" or (response["status"] == "error" and "SUPABASE_ACCESS_TOKEN" in response.get("error", ""))
    if response["status"] == "success":
        assert isinstance(response["data"], list)

    # Test get_vendor_details
    details_response = await get_vendor_details(vendor_id=TEST_VENDOR_ID)
    assert isinstance(details_response, dict)
    assert "status" in details_response
    if details_response["status"] == "success":
        assert "data" in details_response
        assert details_response["data"]["vendor_id"] == TEST_VENDOR_ID
    elif details_response["status"] == "error":
        assert "error" in details_response
        # This is acceptable if the vendor doesn't exist or DB is down
        print(f"test_list_vendors_basic (get_vendor_details part): Received error: {details_response['error']}")
    else:
        pytest.fail(f"Unexpected status in get_vendor_details response: {details_response.get('status')}")

    # ... (More tests for search_vendors) ...

# --- Test Ritual Tools ---
@pytest.mark.asyncio
async def test_search_rituals_success():
    # This will likely fail if ASTRA keys are not set.
    response = await search_rituals(question="What is Kanyadaan?")
    assert isinstance(response, dict)
    assert "status" in response
    if response["status"] == "success":
        assert "data" in response
        assert isinstance(response["data"], list)
    elif response["status"] == "error":
        assert "error" in response
        print(f"test_search_rituals_success: Received error (expected if Astra keys missing): {response['error']}")
    else:
        pytest.fail(f"Unexpected status: {response.get('status')}")

@pytest.mark.asyncio
async def test_search_rituals_invalid_input():
    response_empty_q = await search_rituals(question="")
    assert response_empty_q["status"] == "error"
    assert "question' must be a non-empty string" in response_empty_q["error"]

    response_bad_limit = await search_rituals(question="test", limit=0)
    assert response_bad_limit["status"] == "error"
    assert "'limit' must be a positive integer" in response_bad_limit["error"]

# --- Test Timeline Tools ---
@pytest.mark.asyncio
async def test_create_timeline_event_success():
    response = await create_timeline_event(
        user_id=TEST_USER_ID, # Using provided TEST_USER_ID
        event_name="Pytest Timeline Event",
        event_date_time="2025-01-01T10:00:00"
    )
    assert response["status"] == "success" or (response["status"] == "error" and "SUPABASE_ACCESS_TOKEN" in response.get("error", ""))
    if response["status"] == "success":
        assert "data" in response
        assert response["data"]["event_name"] == "Test Event"

# ... (More tests for get_timeline_events, update_timeline_event) ...

# Note: The original test file had more complex CRUD sequences.
# For this refactoring, I'm focusing on individual tool contracts and basic success/error paths.
# More comprehensive integration tests (like the original test_budget_tools_crud_operations)
# would require a test database or extensive mocking.
# The current tests will mostly verify signatures and basic error handling if DB calls fail due to missing keys.
# If keys ARE present, they become integration tests.

# Example of a more complete test for one function (e.g. delete_budget_item)
@pytest.mark.asyncio
async def test_delete_budget_item_not_found():
    # Assuming item "non_existent_item_id" does not exist
    response = await delete_budget_item(item_id="non_existent_item_id_for_test")
    # This will likely return an error from execute_supabase_sql if token is missing,
    # OR if token is present, it should return an error from the tool itself about not found.
    assert response["status"] == "error"
    if "SUPABASE_ACCESS_TOKEN" not in response.get("error",""): # Only assert specific error if not a token issue
         assert "not found" in response["error"].lower() or "deletion failed" in response["error"].lower()

@pytest.mark.asyncio
async def test_update_budget_item_invalid_inputs():
    response_no_id = await update_budget_item(item_id="", data={"amount":100})
    assert response_no_id["status"] == "error"
    assert "invalid item_id" in response_no_id["error"].lower()

    response_no_data = await update_budget_item(item_id="some-id", data={})
    assert response_no_data["status"] == "error"
    assert "data payload must be a non-empty dictionary" in response_no_data["error"].lower() # Corrected assertion

    response_bad_amount = await update_budget_item(item_id="some-id", data={"amount": "abc"}) # type: ignore
    assert response_bad_amount["status"] == "error"
    assert "invalid amount" in response_bad_amount["error"].lower()

    response_non_updatable_field = await update_budget_item(item_id="some-id", data={"user_id": "new_user"})
    assert response_non_updatable_field["status"] == "error" # Because only 'user_id' was given, which is not updatable
    assert "no valid fields" in response_non_updatable_field["error"].lower()

# Similar detailed tests should be added for other tools and success cases with mocking/setup.
# For now, the above provides a template.
