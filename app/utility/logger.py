import json
import logfire
from loguru import logger

logfire.configure()


def serialize(record):
    subset = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "message": record["message"],
        "level": record["level"].name,
    }
    return json.dumps(subset)


def patching(record):
    record["extra"]["serialized"] = serialize(record)


logger.remove(0)

logger = logger.patch(patching)
logger.add("logs\\loguru.log", format="{extra[serialized]}")
logger.add(logfire.info, format="{message}")

def get_logger():
    return logger
