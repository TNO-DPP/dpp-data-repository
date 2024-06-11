import json
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import config, format_multiline_log
from app.datastores.utils import import_preseeded_data, initialize_stores

# List of allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost:3006",
    "http://localhost:8001",
    "http://localhost:8000",
    # Add other origins as needed
]


startup_logger = logging.getLogger("startup")

if config["mode"] == "dev":
    logging.getLogger().setLevel(logging.DEBUG)
    startup_logger.log(logging.DEBUG, "Setting log-level to DEBUG")


startup_logger.log(
    logging.DEBUG, format_multiline_log("Config:\n" + json.dumps(config, indent=2))
)

# Startup steps
# 1. Initialize stores of data. Clear if already containing
#   data (not applicable for in-memory storage, also not for file-system storage.)
# 2. Copy pre-seeded content and add to data stores.
# 3. Give some information logs about loaded information.

data_store, attachment_store, credential_store, data_store_statistics = (
    initialize_stores()
)
import_preseeded_data(data_store, attachment_store)


# Common call for API endpoints
def get_datastores():
    return data_store, attachment_store, credential_store, data_store_statistics


from app.api.dpp import dpp_app
from app.api.template import dpp_template_app

app = FastAPI()
app.include_router(dpp_app)
app.include_router(dpp_template_app)

# Add CORSMiddleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Finally, the catch-all that loads the UI
@app.get("/healthz", tags=["Health"])
def healthcheck():
    return {"status": "running"}


@app.post("/import_dataset", tags=["Dev"])
def upload_preseeded_data():
    # Primarily meant for dev purposes, in-memory and filesystem databases.
    return {"status": "Not yet implemented"}


@app.get("/info", tags=["Metadata"])
def metadata():
    return {
        "title": config["system"]["title"],
        "description": config["system"]["subtitle"],
    }


@app.get("/config", tags=["Metadata"])
def getconfig():
    return config
