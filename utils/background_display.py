import time
import random
import json

def save_to_database(data):
    assert data["symbol"] == "000001.SH"
    time.sleep(0.2)
    return