import pytest
import uuid
from datetime import date, datetime
from sanskara.tools import vendor_tools
from sanskara.config import supabase

VENDOR_ID_1 = "64d89e91-c21e-4941-85c6-b03ed6d45b86"
VENDOR_ID_2 = "d506933a-af60-4d6e-a168-1f319ba7e106"

@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """
    Sets up the database with test data and cleans up after the module is finished.
    """
    # Load test data
    with open("utils/vendor_tools_test_data.sql", "r") as f:
        sql_commands = f.read()
    try:
        await execute_sql(sql_commands)
        yield  # This allows the tests to run
    finally:
        # Teardown: Clean up test data
        await execute_sql(f"""
            DELETE FROM public.vendor_availability WHERE vendor_id IN ('{VENDOR_ID_1}', '{VENDOR_ID_2}');
            DELETE FROM public.vendors WHERE vendor_id IN ('{VENDOR_ID_1}', '{VENDOR_ID_2}');
        """)

async def execute_sql(sql_commands: str):
    """
    Executes SQL commands against the Supabase database.
    """
    try:
        result = await supabase.from_("vendors").select("*").execute()
        # Execute raw SQL command
        res = await supabase.from_("vendors").supabase.postgrest.query(sql_commands, head=False, count=None)
        if res.status >= 400:
            raise Exception(f"SQL Error: {res.status} - {res.error}")
        return {"status": "success"}
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "error": str(e)}

@pytest.mark.asyncio
async def test_get_vendor_availability():
    """
    Tests the get_vendor_availability function.
    """
    result = await vendor_tools.get_vendor_availability(VENDOR_ID_1)
    assert result["status"] == "success"
    availability_data = result["data"]
    assert len(availability_data) == 3
    assert availability_data[0]["available_date"] == "2024-07-01"
    assert availability_data[0]["status"] == "available"
    assert availability_data[1]["available_date"] == "2024-07-02"
    assert availability_data[1]["status"] == "booked_tentative"
    assert availability_data[2]["available_date"] == "2024-07-03"
    assert availability_data[2]["status"] == "available"

@pytest.mark.asyncio
async def test_check_vendor_availability():
    """
    Tests the check_vendor_availability function.
    """
    # First, get the availability data
    availability_result = await vendor_tools.get_vendor_availability(VENDOR_ID_1)
    assert availability_result["status"] == "success"
    availability_data = availability_result["data"]

    # Test with an available date
    result = await vendor_tools.check_vendor_availability(VENDOR_ID_1, "2024-07-01", availability_data)
    assert result["status"] == "success"
    assert result["data"] is True

    # Test with a booked date
    result = await vendor_tools.check_vendor_availability(VENDOR_ID_1, "2024-07-02", availability_data)
    assert result["status"] == "success"
    assert result["data"] is False

    # Test with a date not in the list (should default to available)
    result = await vendor_tools.check_vendor_availability(VENDOR_ID_1, "2024-07-04", availability_data)
    assert result["status"] == "success"
    assert result["data"] is True

    # Test with an invalid date format
    result = await vendor_tools.check_vendor_availability(VENDOR_ID_1, "20240701", availability_data)
    assert result["status"] == "error"
    assert "Invalid date format" in result["error"]

    # Test with an invalid vendor ID
    result = await vendor_tools.check_vendor_availability("invalid-uuid", "2024-07-01", availability_data)
    assert result["status"] == "error"
    assert "Invalid vendor_id format" in result["error"]
