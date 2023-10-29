import exchange
from utils import *

from time import sleep
from abc import ABC, abstractmethod
from functools import wraps, partial

from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process, Manager


def process_orders(exch):
    t_order_executor = ThreadPoolExecutor(max_workers=32)
    while True:
        # 从队列中取出订单
        order = exch.order_q.get()
        if exch.isConnected():
            # 提交订单到交易所
            future = t_order_executor.submit(exch.place_order, *order)
            # 添加回调函数
            future.add_done_callback(partial(handle_result, exch))


def handle_result(exch, future):
    rtn_data = future.result()

    # 统计交易所仓位
    exch.report_q.put(rtn_data)


def save_to_db(exch):
    t_db_executor = ThreadPoolExecutor(max_workers=32)
    while True:
        # 从队列中取出交易所返回信息
        rtn_data = exch.report_q.get()
        exch._position[rtn_data["symbol"]] = exch._position.get(rtn_data["symbol"], 0) + rtn_data["amount"]
        # 写入db
        t_db_executor.submit(save_to_database, *rtn_data)
        print("写入db: ", rtn_data)


def stat(data_pipe):
    while True:
        rtn_data = data_pipe.data_q.get()
        data_pipe.avg_price[rtn_data["symbol"]] = (data_pipe.avg_price.get(rtn_data["symbol"], 0) * data_pipe.all_amount.get(rtn_data["symbol"], 0) + \
                                         rtn_data["amount"] * rtn_data["price"]) / (
                                                    data_pipe.all_amount.get(rtn_data["symbol"], 0) + rtn_data["amount"])
        data_pipe.all_amount[rtn_data["symbol"]] = data_pipe.all_amount.get(rtn_data["symbol"], 0) + rtn_data["amount"]


def retry_on_disconnect(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if str(e) == "network disconnected":
                        print(f"Network disconnected. Retry {retries+1}...")
                        retries += 1
                        time.sleep(delay)
                    else:
                        raise e
            raise Exception("Maximum retries exceeded")
        return wrapper
    return decorator


class Exchange(ABC):
    def __init__(self):
        manager = Manager()
        self._position = manager.dict()
        self.order_q = manager.Queue()
        self.report_q = manager.Queue()


    def isConnected(self, ):
        if random.randint(1, 100) % 10 == 0:
            return False
        else:
            return True

    @abstractmethod
    def place_order(self, *args, **kwargs):
        pass

    @abstractmethod
    def fetch_order(self, *args, **kwargs):
        pass



class Apple(Exchange):
    def __init__(self):
        super().__init__()

    @retry_on_disconnect(max_retries=5, delay=2)
    def place_order(self, orderid:int, price:float, symbol:str):
        return exchange.apple_place_order(orderid, price, symbol)

    def fetch_order(self, orderid:int):
        return exchange.apple_fetch_order(orderid)


class Banana(Exchange):
    def __init__(self):
        super().__init__()

    @retry_on_disconnect(max_retries=5, delay=2)
    def place_order(self, data, limit:int):
        return exchange.banana_place_order(data, limit)

    def fetch_order(self, orderid:int):
        return exchange.banana_fetch_order(orderid)


class Onion(Exchange):
    def __init__(self):
        super().__init__()

    @retry_on_disconnect(max_retries=5, delay=2)
    def place_order(self, data,):
        return exchange.onion_place_order(data,)

    def fetch_order(self, orderid: int):
        return exchange.onion_fetch_order(orderid)


class Data_Pipe():
    def __init__(self):
        manager = Manager()
        self.data_q = manager.Queue()
        self.all_amount = manager.dict()
        self.avg_price = manager.dict()


class DIST_ENGINE():
    def __init__(self, exchanges: list, data_pipe: Data_Pipe):
        self.DIST_ORDER = [Process(target=process_orders, args=(exch,)) for exch in exchanges]
        self.DIST_REPORT = [Process(target=save_to_db, args=(exch,)) for exch in exchanges]
        self.STAT = Process(target=stat, args=(data_pipe,))

    def start(self):
        for engine in self.DIST_ORDER:
            engine.start()
        for engine in self.DIST_REPORT:
            engine.start()
        self.STAT.start()


def main():

    clientid = 1

    apple  = Apple()
    banana = Banana()
    onion  = Onion()
    data_pipe = Data_Pipe()

    engine = DIST_ENGINE([apple, banana, onion], data_pipe)
    engine.start()

    while True:
        # 收到需要报单的数据
        data = generate_signal()

        data["orderid"] = clientid
        clientid = clientid + 1

        data_pipe.data_q.put(data)

        if data["exch_type"] == "apple":

            # 调用交易所api接口发送订单
            apple.order_q.put((data["orderid"], data["price"], data["symbol"]))

            # print("当前apple仓位：", apple._position)

        elif data["exch_type"] == "banana":

            # 调用交易所api接口发送订单
            banana.order_q.put((data, data["price"]))

            # print("当前banana仓位：", banana._position)

        elif data["exch_type"] == "onion":

            # 调用交易所api接口发送订单
            onion.order_q.put((data,))

            # print("当前onion仓位：", onion._position)



if __name__ == '__main__':


    main()