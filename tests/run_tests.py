import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sanskara.tools import *

test_email = "test@example.com"
test_user_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
test_vendor_id = "f0e9d8c7-b6a5-4433-2211-009988776655"
test_item = {"item": "Test Item", "category": "Test Category", "amount": 100.00}
test_item_id = "11223344-5566-7788-9900-aabbccddeeff"
test_question = "What is a wedding?"

print(f"Testing get_user_id with email: {test_email}")
print(get_user_id(test_email))

print(f"\nTesting get_user_data with user_id: {test_user_id}")
print(get_user_data(test_user_id))

print(f"\nTesting update_user_data with user_id: {test_user_id}")
print(update_user_data(test_user_id, {"display_name": "Test User"}))

print(f"\nTesting list_vendors")
print(list_vendors({"vendor_category": "Venue"}))

print(f"\nTesting get_vendor_details with vendor_id: {test_vendor_id}")
print(get_vendor_details(test_vendor_id))

print(f"\nTesting add_budget_item with user_id: {test_user_id}")
print(add_budget_item(test_user_id, test_item))

print(f"\nTesting get_budget_items with user_id: {test_user_id}")
print(get_budget_items(test_user_id))

print(f"\nTesting update_budget_item with item_id: {test_item_id}")
print(update_budget_item(test_item_id, amount=200.00))

print(f"\nTesting delete_budget_item with item_id: {test_item_id}")
print(delete_budget_item(test_item_id))

print(f"\nTesting search_rituals with question: {test_question}")
print(search_rituals(test_question))
