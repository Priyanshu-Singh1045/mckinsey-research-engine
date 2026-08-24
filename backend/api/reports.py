# Importing fast APi
from fastapi import APIRouter


# Reports API routes
router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


@router.get("/test")
def test_reports():
    print("Reports API test route called")

    return {
        "message": "Reports API is Working!"
    }