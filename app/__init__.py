from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import(
    causas,
    bot_whatsapp,
    socket
)

app = FastAPI(
            title="Demo-Causas", 
            description="Backend-API para Demo-Causas",
            version="0.0.1"
        )

app.include_router(causas.router)
app.include_router(bot_whatsapp.router)
app.include_router(socket.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Demo-Causas"}

# Enable CORS
origins = ["https://demo-causas.netlify.app"]

regex_origins = r"^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=regex_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)