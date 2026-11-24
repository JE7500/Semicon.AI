from typing import Literal

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import settings

app = FastAPI(
    title="Semicon.AI API",
    version="2.0.0-alpha",
    description="API gateway for hardware-aware RTL generation. Verification is a separate pipeline.",
)


class GenerateRequest(BaseModel):
    specification: str = Field(min_length=5, max_length=12000)
    hdl: Literal["verilog", "vhdl"] = "verilog"
    module_name: str | None = Field(default=None, max_length=128)
    constraints: list[str] = Field(default_factory=list, max_length=30)


class GenerateResponse(BaseModel):
    hdl: str
    code: str
    model: str | None = None
    request_id: str | None = None


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "semicon-api",
        "model_configured": bool(settings.model_endpoint),
    }


@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    if not settings.model_endpoint:
        raise HTTPException(
            status_code=503,
            detail="Model inference endpoint is not configured. Configure SEMICON_MODEL_ENDPOINT.",
        )

    headers = {}
    if settings.model_api_token:
        headers["Authorization"] = f"Bearer {settings.model_api_token}"

    payload = {
        "specification": request.specification,
        "hdl": request.hdl,
        "module_name": request.module_name,
        "constraints": request.constraints,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.model_timeout_seconds) as client:
            response = await client.post(
                settings.model_endpoint.rstrip("/") + "/v1/generate",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Model inference timed out.") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Model service returned HTTP {exc.response.status_code}.",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Could not reach model inference service.") from exc

    try:
        return GenerateResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Model service returned an invalid response.") from exc
