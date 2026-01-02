# gateway/main.py (обновлённая версия)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STUDENT_SERVICE = "http://student_service:8001"
GRADE_SERVICE = "http://grade_service:8002"
REPORT_SERVICE = "http://report_service:8003"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, path: str):
    clean_path = path.lstrip("/")

    client = httpx.AsyncClient(timeout=10.0)

    if clean_path.startswith("students") or clean_path.startswith("groups"):
        target_url = f"{STUDENT_SERVICE}/{clean_path}"
    elif clean_path.startswith("grades"):
        target_url = f"{GRADE_SERVICE}/{clean_path}"
    elif clean_path.startswith("report"):
        target_url = f"{REPORT_SERVICE}/{clean_path}"
    else:
        await client.aclose()
        return JSONResponse({"error": "Not found"}, status_code=404)

    try:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=await request.body()
        )
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as e:
        return JSONResponse(
            {"error": f"Service unavailable: {str(e)}"},
            status_code=503
        )
    finally:
        await client.aclose()