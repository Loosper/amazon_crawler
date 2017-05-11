import threading
import queue
import time
# ship abandoned. Using asyncio for now


class getter_handler:
    def __init__(self, callback):
        self.__call__ = callback
        # is this legal?


def amazon_handler():
    while True:
        request = api_queue.get()
        response = request.send_request()
        api_queue.task_done()

        response_queue.put(response)
        time.sleep(0.9)


api_queue = queue.Queue()
response_queue = queue.Queue()

threading.thread(target=amazon_handler)
