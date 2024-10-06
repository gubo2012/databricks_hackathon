from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

