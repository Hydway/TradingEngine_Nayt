import time
import random
import json
exch_type = ["apple", "banana", "onion"]

def generate_signal():
    data = {}
    data["exch_type"] = exch_type[random.randint(1, 100) % 3]
    data["symbol"] = "000001.SH"
    data["price"] = float(random.randint(1, 20000))
    data["amount"] = 1
    return data