from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import utilization

app = FastAPI(title="MIMIC-FHIR Utilization API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(utilization.router)


@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
