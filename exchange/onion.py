import time
import random

onion_map = {}
def isConnected():
    if random.randint(1, 100) % 10 == 0:
        return False
    else:
        return True

#place order to exchange
def onion_place_order(data):
    time.sleep(0.1)
    if isConnected():
        return data
    else:
        onion_map[data["orderid"]] = data
        raise Exception('network disconnected')

#fetch history orders
def onion_fetch_order(orderid):
    return onion_map[orderid]