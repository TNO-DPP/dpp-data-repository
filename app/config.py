import logging
import os
from typing import Any

import yaml

config_cache: dict[str, Any] = dict()
# config_filename = os.getenv("PYC_CONFIG", "/config/application.yaml")
logger = logging.getLogger("config")
logger.debug("Looking for config.")
CONFIG_PATH = "/config.yaml"
if not os.path.isfile(CONFIG_PATH):
    CONFIG_PATH = "./workdir/appconfig.yaml"
    logger.debug("Dev config found at " + CONFIG_PATH)
else:
    logger.debug("Config found at " + CONFIG_PATH)

config_filename = os.getenv("PYC_CONFIG", CONFIG_PATH)
with open(config_filename, "r") as stream:
    config = yaml.safe_load(stream)


def format_multiline_log(log_message: str, indent: str = "\t" * 6) -> str:
    lines = log_message.split("\n")
    formatted_lines = [lines[0]]  # Keep the first line as it is
    formatted_lines.extend(
        f">{indent}{line}" for line in lines[1:]
    )  # Indent subsequent lines
    return "\n".join(formatted_lines)
