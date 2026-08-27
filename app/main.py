from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {
        "message": "FastAPI Backend is running"
    }