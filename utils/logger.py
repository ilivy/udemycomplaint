import os

from constants import LOGS_FOLDER
from datetime import datetime


def write_log(tag: str, message: str):
    """
    Writes log into LOG FOLDER
    :param tag:
    :param message:
    :return:
    """
    filename = datetime.utcnow().strftime("%Y-%m-%d") + ".log"
    curtime = datetime.utcnow().strftime("%H:%M")
    path = os.path.join(LOGS_FOLDER, filename)
    with open(path, "a+") as log:
        log.write(f"{curtime} - {tag} - {message}\n")
