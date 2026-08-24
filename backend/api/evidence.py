from fastapi import APIRouter


# Evidence API routes
router = APIRouter(
    prefix="/api/evidence",
    tags=["Evidence"]
)


@router.get("/test")
def test_evidence():
    print("Evidence API test route called")

    return {
        "message": "Evidence API is working!"
    }