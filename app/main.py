from fastapi import FastAPI

app = FastAPI(
    title="CareerGraphAI",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "CareerGraphAI is running"}
