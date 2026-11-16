from src.database.supabase_client import supabase

try:
    response = supabase.table("employees").select("id").limit(1).execute()
    print("Supabase connection successful!")
    print(response.data)

except Exception as e:
    print("Connection failed:", e)