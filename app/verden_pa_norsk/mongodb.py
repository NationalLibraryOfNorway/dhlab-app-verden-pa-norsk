from configparser import ConfigParser
from pymongo import MongoClient
import os

DB = "nasjonalbibliografien4_test"
COLLECTION = "records"


def connect(db=DB, collection=COLLECTION):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, "config.cfg")
    config = ConfigParser()
    # config.read("verden_pa_norsk/config.cfg")
    config.read(config_path)

    client = MongoClient(
        config["fulltekst_api"]["host"],
        username=config["fulltekst_api"]["username"],
        password=config["fulltekst_api"]["pwd"],
        authSource=config["fulltekst_api"]["authSource"],
    )

    return client[db][collection]
