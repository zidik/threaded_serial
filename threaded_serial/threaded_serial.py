import logging
import queue
import threading
import serial

__author__ = 'Mark Laane'

class ThreadedSerialManager:
    def __init__(self, connection: serial.Serial, callback=lambda x: None):
        self.connection = connection
        self.connection.timeout = 0.1
        self.callback = callback

        self._stop = False
        self._send_queue = queue.Queue()

        self._receiving_thread = threading.Thread(target=self._run_receiving_thread, name="ReceivingThread")
        self._sending_thread = threading.Thread(target=self._run_sending_thread, name="SendingThread")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """
        Start managing serial port
        """
        logging.info("{} {} starting...".format(self.connection.name, type(self).__name__))
        if not self.connection.isOpen():
            logging.info("Connecting to {}".format(self.connection.name))
            self.connection.open()
            logging.info("Connected to {}".format(self.connection.name))
        self._receiving_thread.start()
        self._sending_thread.start()
        logging.info("{} {} started".format(self.connection.name, type(self).__name__))

    def stop(self, timeout=None, close=True):
        """
        Signal threads to stop
        :param timeout: thread join timeout
        :param close: close serial connection
        :return:
        """
        logging.info("{} {} stopping...".format(self.connection.name, type(self).__name__))
        self._stop = True
        if threading.current_thread() is not self._receiving_thread:
            self._receiving_thread.join(timeout)
        if threading.current_thread() is not self._sending_thread:
            self._sending_thread.join(timeout)
        if close:
            self.connection.close()
        logging.info("{} {} stopped".format(self.connection.name, type(self).__name__))

    def send(self, data):
        self._send_queue.put_nowait(data)

    def send_string(self, string, encoding="ascii"):
        self.send(string.encode(encoding))

    def _run_receiving_thread(self):
        """
        Thread that monitors serial port and calls callback function every time it receives a full line.
        """
        logging.debug("{} {} started". format(self.connection.name, threading.current_thread().name))
        try:
            raw_line = bytearray()
            while not self._stop:
                raw_line += self.connection.readline()
                if len(raw_line) < 1:
                    continue
                if raw_line[-1] != 10: # when not ending with "Line feed" (timeout ocurred)
                    continue

                self.callback(raw_line)
                raw_line = bytearray()
        except Exception as e:
            logging.exception(e)
        self._stop = True  # Also bring down the other thread
        logging.debug("{} {} stopped". format(self.connection.name, threading.current_thread().name))

    def _run_sending_thread(self):
        """
        Thread that sends data that has been placed in _send_queue
        """
        logging.debug("{} {} started". format(self.connection.name, threading.current_thread().name))
        try:
            while not self._stop:
                try:
                    data = self._send_queue.get(timeout=0.1)
                except queue.Empty:
                    pass
                else:
                    self.connection.write(data)
        except Exception as e:
            print(type(data))
            logging.exception(e)
        self._stop = True  # Also bring down the other thread
        logging.debug("{} {} stopped". format(self.connection.name, threading.current_thread().name))




