from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        # Validate the token with Supabase Auth
        user = supabase.auth.get_user(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        return user.user
    except Exception:
        raise HTTPException(status_code=401, detail="Unauthorized")