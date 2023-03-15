#!/usr/bin/env python
from machine import Timer
import os
import sys

from Config import Config

MB_TO_BYTES = 1000000


class Logger:
    """A Logger class for logging data in various levels: ERROR, INFO, DEBUG.
    The loggger constuctor accepts the log level.
    """
    __instance = None

    _OFF = 0
    _ERROR = 1
    _INFO = 2
    _DEBUG = 3

    _log_level = 2  # see constants above
    _log_file_size = 1  # max log file size in MB
    _logfile = None

    _chrono = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Logger.__instance == None:
            Logger()
        return Logger.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Logger.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logger.__instance = self
            config = Config.get_instance()
            self._log_level = config.log_level
            self._log_file_size = config.log_file_size
            self._chrono = Timer.Chrono()
            self._chrono.reset()
            self._chrono.start()
            if 'sd' in os.listdir('/'):
                self._rotate_log_file()
                self._logfile = open('/sd/log', 'a')

    def _rotate_log_file(self):
        if ('sd' in os.listdir('/')) and ('log' in os.listdir('/sd')):
            file_size = os.stat('/sd/log')[6]
            # '_log_file_size' is in MB, while 'file_size' is in bytes
            if file_size >= self._log_file_size * MB_TO_BYTES:
                os.rename('/sd/log', '/sd/log_old')

    def _print(self, msg, tag, ex=None):
        out_stream = self.get_output_stream()
        log_txt = '{:-10} \t [{}] > {}'.format(self._chrono.read(), tag, msg)
        print(log_txt, file=out_stream)
        if ex is not None:
            sys.print_exception(ex, out_stream)

        # uncomment for development to see log output over serial USB
        # print(log_txt)
        # if ex is not None:
        #     sys.print_exception(ex)
            

    def get_output_stream(self):
        if self._logfile != None:
            return self._logfile
        else:
            return sys.stdout

    def deinit(self):
        if self._logfile:
            self._logfile.close()
            self._logfile = None
        if self._chrono:
            self._chrono.stop()
            self._chrono = None

    def error(self, msg, exception=None):
        if (self._log_level >= self._ERROR):
            self._print(msg, 'E', exception)

    def info(self, msg):
        if (self._log_level >= self._INFO):
            self._print(msg, 'I')

    def debug(self, msg):
        if (self._log_level >= self._DEBUG):
            self._print(msg, 'D')
