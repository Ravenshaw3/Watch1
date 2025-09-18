"""
Simple FastAPI application without complex models
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Watch1 Media Server - Simple Version")

@app.get("/")
async def root():
    return {"message": "Watch1 Media Server is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Watch1 Media Server"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
