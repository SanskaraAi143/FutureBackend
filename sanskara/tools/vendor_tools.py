import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from typing import List, Dict, Any, Optional
from google.adk.tools import  ToolContext, LongRunningFunctionTool
from sanskara.config import supabase
import uuid
from datetime import datetime, date
from sanskara.tools import execute_supabase_sql

async def get_vendor_availability(vendor_id: str, context: ToolContext = None) -> dict:
    """
    Gets all availability data for a vendor after today's date.

    Args:
        vendor_id (str): The UUID of the vendor.
        context (ToolContext): The tool execution context.

    Returns:
        dict: A dictionary with status and data or error.
    """
    try:
        # Validate input
        try:
            uuid.UUID(vendor_id)  # Will raise ValueError if not a valid UUID
        except ValueError:
            return {"status": "error", "error": "Invalid vendor_id format."}

        # Get today's date
        today = date.today()

        # Construct the SQL query
        sql = """
            SELECT available_date, status
            FROM vendor_availability
            WHERE vendor_id = :vendor_id AND available_date >= :today
            ORDER BY available_date;
        """

        params = {
            "vendor_id": vendor_id,
            "today": today.isoformat()
        }

        result = await execute_supabase_sql(sql, params)

        if result["status"] == "success":
            availability_list = []
            for item in result["data"]:
                availability_list.append({
                    "available_date": item["available_date"],
                    "status": item["status"]
                })
            return {"status": "success", "data": availability_list}
        else:
            return result  # Propagate error from execute_supabase_sql

    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "error": str(e)}


async def check_vendor_availability(vendor_id: str, date: str, availability_data: list, context: ToolContext = None) -> dict:
    """
    Checks if a vendor is available on a specific date, using pre-fetched availability data.

    Args:
        vendor_id (str): The UUID of the vendor.
        date (str): The date to check availability for (YYYY-MM-DD).
        availability_data (list): A list of dictionaries with availability data.
        context (ToolContext): The tool execution context.

    Returns:
        dict: A dictionary with status and data or error.
    """
    try:
        # Validate inputs
        try:
            uuid.UUID(vendor_id)  # Will raise ValueError if not a valid UUID
        except ValueError:
            return {"status": "error", "error": "Invalid vendor_id format."}

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"status": "error", "error": "Invalid date format. Use YYYY-MM-DD."}

        if not isinstance(availability_data, list):
            return {"status": "error", "error": "availability_data must be a list."}

        # Search for the date in the availability data
        for item in availability_data:
            if item["available_date"] == date:
                if item["status"] == "available":
                    return {"status": "success", "data": True}
                else:
                    return {"status": "success", "data": False}

        # If the date is not found, assume available
        return {"status": "success", "data": True}

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "error": str(e)}
