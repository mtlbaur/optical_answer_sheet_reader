import logging
import logging.handlers

from time import sleep
from threading import Thread
from multiprocessing import Queue, Process

from oasr.cfg import logging_level
from oasr.utility import trace


class LoggingHandler(logging.Handler):
    def __init__(self, manager, record_f, level: int | str = 0) -> None:
        super().__init__(level)

        self.manager = manager
        self.record_f = record_f

    def emit(self, record):
        if not self.manager.shutdown:
            self.record_f(record)


def worker_process(queue, *, function, args=[], kwargs={}):
    # this handler will forward to the queue
    handler = logging.handlers.QueueHandler(queue)

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging_level)

    function(*args, **kwargs)


def listener_thread(queue):
    while True:
        record = queue.get()

        if record is None:
            break

        logging.getLogger(record.name).handle(record)


def handle(manager, task):
    queue = Queue()

    listener = Thread(target=listener_thread, args=(queue,))
    listener.start()

    worker = Process(target=worker_process, args=(queue,), kwargs=task)
    worker.start()

    while worker.is_alive():
        if manager.kill_worker:
            break

        sleep(manager.sleep_duration)

    if worker.is_alive():
        worker.terminate()

    worker.join()

    queue.put_nowait(None)

    listener.join()


class Manager:
    def __init__(self) -> None:
        self.task_thread = None
        self.kill_worker = False
        self.sleep_duration = 0.1
        self.shutdown = False

    def execute(self, task={"function": None, "args": [], "kwargs": {}}):
        self.terminate()

        self.task_thread = Thread(target=handle, args=[self, task])
        self.task_thread.start()

    def terminate(self):
        if self.task_thread and self.task_thread.is_alive():
            trace("terminate")

            self.kill_worker = True
            self.task_thread.join()
            self.task_thread = None
            self.kill_worker = False
