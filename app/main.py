import json
import logging

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.api.dpp import dpp_app
from app.api.template import dpp_template_app
from app.config import config, format_multiline_log
from app.datastores.utils import import_preseeded_data

app = FastAPI()
app.include_router(dpp_app)
app.include_router(dpp_template_app)

startup_logger = logging.getLogger("Startup")
if config["mode"] == "dev":

    logging.getLogger().setLevel(logging.DEBUG)
    startup_logger.log(logging.DEBUG, "Setting log-level to DEBUG")


startup_logger.log(
    logging.DEBUG, format_multiline_log("Config:\n" + json.dumps(config, indent=2))
)

# Startup steps
# 1. Initialize stores of data. Clear if already containing
#   data (not applicable for in-memory storage, also not for file-system storage.)

# import_preseeded_data()

#   - Have data model for Attachment References, Credentials, Templates, DPPs, Events. Update all as needed.
# 2. Copy pre-seeded content and add to data stores.
# 3. Give some information logs about loaded information.


# Shutdown steps
#


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
