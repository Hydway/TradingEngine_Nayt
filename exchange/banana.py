import time
import random

banana_map = {}
def isConnected():
    if random.randint(1, 100) % 10 == 0:
        return False
    else:
        return True

#place order to exchange
def banana_place_order(data, limit:int):
    time.sleep(0.3)
    if isConnected():
        return data
    else:
        banana_map[data["orderid"]] = data
        raise Exception('network disconnected')

#fetch history orders
def banana_fetch_order(orderid:int):
    return banana_map[orderid]