from fastapi import Header, HTTPException

from backend.db.supabase_client import supabase


# Get the logged=in user from the authorization token

def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header.",
        )

    token = authorization.split(" ", 1)[1].strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token.",
        )

    try:
        result = supabase.auth.get_user(token)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please sign in again.",
        )

    user = getattr(result, "user", None)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please sign in again.",
        )

    print(f"User authenticated: {user.id}")

    return user