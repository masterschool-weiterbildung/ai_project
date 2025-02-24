import json
from pathlib import Path

import logfire
from loguru import logger

logfire.configure()

log_path = Path(__file__).parent.parent / "logs" / "loguru.log"

def serialize(record):
    return json.dumps({
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "message": record["message"],
        "level": record["level"].name,
    })


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger.remove()

logger = logger.patch(patching)

logger.add(
    log_path,
    format="{extra[serialized]}",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    diagnose=True,
    catch=True)

logger.add(logfire.info, format="{message}")


def get_logger():
    return logger