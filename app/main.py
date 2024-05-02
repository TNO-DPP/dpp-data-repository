from fastapi import FastAPI

from .api.dpp import dpp_app
from .api.template import dpp_template_app

app = FastAPI()
app.include_router(dpp_app)
app.include_router(dpp_template_app)


# Finally, the catch-all that loads the UI
@app.get("/healthz", tags=["Health"])
def healthcheck():
    return {"status": "running"}
