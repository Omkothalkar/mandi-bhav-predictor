from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.endpoints import router as api_router

app = FastAPI(
    title="Agmarknet Forecasting API",
    description="API for historical agricultural prices, forecasts, and mandi comparisons.",
    version="1.0.0",
)

# CORS configuration for local and deployed frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mandi-bhav-predictor.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Mandi Bhav Predictor API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
