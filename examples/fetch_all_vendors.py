from config import supabase

# Fetch and print all vendor data from Supabase
try:
    vendor_response = supabase.table("vendors").select("*").execute()
    print("All vendors from Supabase:")
    for vendor in vendor_response.data:
        print(vendor)
except Exception as e:
    print("Error fetching vendors from Supabase:", e)
