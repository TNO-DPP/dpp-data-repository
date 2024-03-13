from fastapi import FastAPI

app = FastAPI()


# Finally, the catch-all that loads the UI
@app.get("/healthz")
def healthcheck():
    return {"status": "running"}
