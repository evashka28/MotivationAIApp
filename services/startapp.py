import logging
import os

#не удалять
if not os.path.exists("tmp"):
    os.makedirs("tmp")

tmp_path = "tmp/"


if not os.path.exists("log"):
    os.makedirs("log")

log_path = "log/"
log = log_path + "log.log"
logging.basicConfig(
    level=logging.INFO,
    filename=log,
    format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
    datefmt="%H:%M:%S",
)


