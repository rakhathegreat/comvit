import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

async def supabase():
    """Initialize and return the Supabase client."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("Supabase URL or Key not found in environment variables.")
        
        # Initialize the Supabase client
        client: Client = create_client(url, key)
        if client:
            return client
        else:
            raise Exception("Failed to create Supabase client.")
    
    except ValueError as ve:
        print(f"Error: {ve}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None