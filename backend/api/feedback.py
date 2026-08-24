from fastapi import APIRouter


# Feedback API routes
router = APIRouter(
    prefix="/api/feedback",
    tags=["Feedback"]
)


@router.get("/test")
def test_feedback():
    print("Feedback API test route call")

    return {
        "message": "Feedbackl API is Working!"
    }