from fastapi import APIRouter, Request

router = APIRouter(tags=["openapi"])


@router.get("/openapi.json", include_in_schema=False)
async def get_v1_openapi(request: Request) -> dict:
    """Expose le contrat OpenAPI sous le namespace public versionné."""
    return request.app.openapi()
