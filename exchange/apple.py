import random
import time


apple_map = {}
def isConnected():
    if random.randint(1, 100) % 10 == 0:
        return False
    else:
        return True

#place order to exchange
def apple_place_order(orderid:int, price:float, symbol:str):
    time.sleep(0.01)
    if isConnected():
        return {"orderid":orderid, "symbol":symbol, "price":price, "status":"success", "amount":1}
    else:
        apple_map[orderid] = {"orderid":orderid, "symbol":symbol, "price":price, "status":"success", "amount":1}
        raise Exception("network disconnected")

#fetch history orders
def apple_fetch_order(orderid:int):
    return apple_map[orderid]