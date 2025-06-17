from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import(
    causas
)

app = FastAPI(
            title="Demo-Causas", 
            description="Backend-API para Demo-Causas",
            version="0.0.1"
        )

app.include_router(causas.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Demo-Causas"}

# Enable CORS
origins = []

regex_origins = r"^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=regex_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)