from exchange import *
from utils import *
from time import sleep

# 各个交易所的仓位
apple_position = {}
banana_position = {}
onion_position = {}

all_amount = {}
avg_price = {}
clientid = 1

while True:
    #收到需要报单的数据
    data = generate_signal()

    data["orderid"] = clientid
    clientid = clientid + 1

    if data["exch_type"] == "apple":

        print(data)
        #调用交易所api接口发送订单
        rtn_data = apple_place_order(data["orderid"], data["price"], data["symbol"])

        #统计apple交易所仓位
        apple_position[rtn_data["symbol"]] = apple_position.get(rtn_data["symbol"], 0) + rtn_data["amount"]
        print(apple_position)

        #统计所有交易所该品种的价格的均价
        avg_price[rtn_data["symbol"]] = (avg_price.get(rtn_data["symbol"], 0) * all_amount.get(rtn_data["symbol"], 0) + rtn_data["amount"] * rtn_data["price"]) / (all_amount.get(rtn_data["symbol"], 0) + rtn_data["amount"])
        all_amount[rtn_data["symbol"]] = all_amount.get(rtn_data["symbol"], 0) + rtn_data["amount"]

        #保存数据到后端数据库
        save_to_database(rtn_data)

        # sleep(0.1)