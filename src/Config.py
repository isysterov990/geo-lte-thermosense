#!/usr/bin/env python

import os
import sys

import pycom
import ujson
from machine import SD


class Config:
    __instance = None

    _config_file_loaded = False

    # CONFIGURATION VARIABLES
    # Each variable is initialized with the default value below.
    # If a 'config.json' file is present on the SD card, these variables will
    # be overriden with the matching values in the config file.

    log_level = 2  # 0=OFF, 1=ERROR, 2=INFO, 3=DEBUG
    log_file_size = 1  # megabytes
    server_address = 'trackensure.com'
    server_port = 8883
    server_use_ssl = 0  # 0=OFF, 1=ON
    server_timeout = 10  # seconds
    sleep_seconds = 30
    sleep_gps_on = 1  # 0=OFF, 1=ON, keep gps module ON during deep sleep
    gps_timeout = 15  # seconds
    apn = 'iot.aer.net'
    lte_timeout = 10  # seconds
    ruuvi_enabled = 0
    ruuvi_timeout = 5  # seconds
    # MAC address of the ruuvi tag to read data from. If set to 'FFFFFFFFFFFF' then will read from the first ruuvi device found
    ruuvi_mac = 'FFFFFFFFFFFF'
    temp_alert_enabled = 0  # 0=OFF, 1=ON
    temp_alert_low = -10.0
    temp_alert_high = 50.0
    ota_server_address = 'trackensure.com'
    ota_server_port = 8884
    acc_alert_enabled = 0  # 0=OFF, 1=ON
    acc_alert_threshold = 200  # mg (mili g-force units)
    acc_alert_duration = 300  # milliseconds

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Config.__instance == None:
            Config()
        return Config.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Config.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Config.__instance = self
            self._load_config_file()

    def _load_config_file(self):
        try:
            config_file = None
            if 'sd' in os.listdir('/') and 'config.json' in os.listdir('/sd'):
                config_file = open('/sd/config.json', 'r')
                j = ujson.loads(config_file.read())

                # TODO use reflection

                if 'log_level' in j:
                    self.log_level = j['log_level']

                if 'log_file_size' in j:
                    self.log_file_size = j['log_file_size']

                if 'server_address' in j:
                    self.server_address = j['server_address']

                if 'server_port' in j:
                    self.server_port = j['server_port']

                if 'server_use_ssl' in j:
                    self.server_use_ssl = j['server_use_ssl']

                if 'server_timeout' in j:
                    self.server_timeout = j['server_timeout']

                if 'sleep_seconds' in j:
                    self.sleep_seconds = j['sleep_seconds']

                if 'sleep_gps_on' in j:
                    self.sleep_gps_on = j['sleep_gps_on']

                if 'gps_timeout' in j:
                    self.gps_timeout = j['gps_timeout']

                if 'apn' in j:
                    self.apn = j['apn']

                if 'lte_timeout' in j:
                    self.lte_timeout = j['lte_timeout']

                if 'ruuvi_enabled' in j:
                    self.ruuvi_enabled = j['ruuvi_enabled']

                if 'ruuvi_timeout' in j:
                    self.ruuvi_timeout = j['ruuvi_timeout']

                if 'ruuvi_mac' in j:
                    self.ruuvi_mac = j['ruuvi_mac']

                if 'ota_server_address' in j:
                    self.ota_server_address = j['ota_server_address']

                if 'ota_server_port' in j:
                    self.ota_server_port = j['ota_server_port']

                if 'temp_alert_low' in j:
                    self.temp_alert_low = j['temp_alert_low']

                if 'temp_alert_high' in j:
                    self.temp_alert_high = j['temp_alert_high']

                if 'temp_alert_enabled' in j:
                    self.temp_alert_enabled = j['temp_alert_enabled']
                
                if 'acc_alert_enabled' in j:
                    self.acc_alert_enabled = j['acc_alert_enabled']
                
                if 'acc_alert_threshold' in j:
                    self.acc_alert_threshold = j['acc_alert_threshold']
                
                if 'acc_alert_duration' in j:
                    self.acc_alert_duration = j['acc_alert_duration']

                self._config_file_loaded = True
        except Exception as ex:
            print('load_config_file ERROR:', ex)
        finally:
            print('config_file_loaded =', self._config_file_loaded)
            if config_file is not None:
                config_file.close()

    def did_load_config_file(self):
        return self._config_file_loaded

    def _mk_int(self, s):
        s = s.strip()
        return int(s) if s else ""

    def _mk_empty(self, s, config_val):
        if(s == ""):
            return config_val
        else:
            return s

    def write_config_json(self, frame):
        frame_wcf = frame
        # print(frame_wcf)
        file_path = '/sd/{}'.format('config.json')
        if 'sd' in os.listdir('/'):
            with open(file_path, 'w') as f:
                ujson.dump({
                    'log_level': self._mk_empty(self._mk_int(frame_wcf[1]), self.log_level),
                    'log_file_size': self._mk_empty(self._mk_int(frame_wcf[2]), self.log_file_size),
                    'sleep_seconds': self._mk_empty(self._mk_int(frame_wcf[3]), self.sleep_seconds),
                    'sleep_gps_on': self._mk_empty(self._mk_int(frame_wcf[4]), self.sleep_gps_on),
                    'server_address': self._mk_empty(frame_wcf[5], self.server_address),
                    'server_port': self._mk_empty(self._mk_int(frame_wcf[6]), self.server_port),
                    'server_use_ssl': self._mk_empty(self._mk_int(frame_wcf[7]), self.server_use_ssl),
                    'server_timeout': self._mk_empty(self._mk_int(frame_wcf[8]), self.server_timeout),
                    'apn': self._mk_empty(frame_wcf[9], self.apn),
                    'lte_timeout': self._mk_empty(self._mk_int(frame_wcf[10]), self.lte_timeout),
                    'gps_timeout': self._mk_empty(self._mk_int(frame_wcf[11]), self.gps_timeout),
                    'ruuvi_enabled': self._mk_empty(self._mk_int(frame_wcf[12]), self.ruuvi_enabled),
                    'ruuvi_mac': self._mk_empty(frame_wcf[13], self.ruuvi_mac),
                    'ruuvi_timeout': self._mk_empty(self._mk_int(frame_wcf[14]), self.ruuvi_timeout),
                    'temp_alert_low': self._mk_empty(self._mk_int(frame_wcf[15]), self.temp_alert_low),
                    'temp_alert_high': self._mk_empty(self._mk_int(frame_wcf[16]), self.temp_alert_high),
                    'temp_alert_enabled': self._mk_empty(self._mk_int(frame_wcf[17]), self.temp_alert_enabled),
                    'acc_alert_enabled': self._mk_empty(self._mk_int(frame_wcf[18]), self.acc_alert_enabled),
                    'acc_alert_threshold': self._mk_empty(self._mk_int(frame_wcf[19]), self.acc_alert_threshold),
                    'acc_alert_duration': self._mk_empty(self._mk_int(frame_wcf[20]), self.acc_alert_duration)}, f)

    def read_config_file(self):

        log_level = self.log_level
        log_file_size = self.log_file_size
        sleep_seconds = self.sleep_seconds
        sleep_gps_on = self.sleep_gps_on
        server_address = self.server_address
        server_port = self.server_port
        server_use_ssl = self.server_use_ssl
        server_timeout = self.server_timeout
        apn = self.apn
        lte_timeout = self.lte_timeout
        gps_timeout = self.gps_timeout
        ruuvi_enabled = self.ruuvi_enabled
        ruuvi_mac = self.ruuvi_mac
        ruuvi_timeout = self.ruuvi_timeout
        temp_alert_low = self.temp_alert_low
        temp_alert_high = self.temp_alert_high
        temp_alert_enabled = self.temp_alert_enabled
        acc_alert_enabled = self.acc_alert_enabled
        acc_alert_threshold = self.acc_alert_threshold
        acc_alert_duration = self.acc_alert_duration

        config_file = None
        if 'sd' in os.listdir('/') and 'config.json' in os.listdir('/sd'):
            config_file = open('/sd/config.json', 'r')
            j = ujson.loads(config_file.read())

            if 'log_level' in j:
                log_level = j['log_level'],

            if 'log_file_size' in j:
                log_file_size = j['log_file_size']

            if 'sleep_seconds' in j:
                sleep_seconds = j['sleep_seconds']

            if 'sleep_gps_on' in j:
                sleep_gps_on = j['sleep_gps_on']

            if 'server_address' in j:
                server_address = j['server_address']

            if 'server_port' in j:
                server_port = j['server_port']

            if 'server_use_ssl' in j:
                server_use_ssl = j['server_use_ssl']

            if 'server_timeout' in j:
                server_timeout = j['server_timeout']

            if 'sleep_seconds' in j:
                sleep_seconds = j['sleep_seconds']

            if 'gps_timeout' in j:
                gps_timeout = j['gps_timeout']

            if 'apn' in j:
                apn = j['apn']

            if 'lte_timeout' in j:
                lte_timeout = j['lte_timeout']

            if 'ruuvi_enabled' in j:
                ruuvi_enabled = j['ruuvi_enabled']

            if 'ruuvi_timeout' in j:
                ruuvi_timeout = j['ruuvi_timeout']

            if 'ruuvi_mac' in j:
                ruuvi_mac = j['ruuvi_mac']

            if 'temp_alert_low' in j:
                temp_alert_low = j['temp_alert_low']

            if 'temp_alert_high' in j:
                temp_alert_high = j['temp_alert_high']

            if 'temp_alert_enabled' in j:
                temp_alert_enabled = j['temp_alert_enabled']
            
            if 'acc_alert_enabled' in j:
                acc_alert_enabled = j['acc_alert_enabled']
            
            if 'acc_alert_threshold' in j:
                acc_alert_threshold = j['acc_alert_threshold']
            
            if 'acc_alert_duration' in j:
                acc_alert_duration = j['acc_alert_duration']

        frame = '@CFG,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(
            log_level,
            log_file_size,
            sleep_seconds,
            sleep_gps_on,
            server_address,
            server_port,
            server_use_ssl,
            server_timeout,
            apn,
            lte_timeout,
            gps_timeout,
            ruuvi_enabled,
            ruuvi_mac,
            ruuvi_timeout,
            temp_alert_low,
            temp_alert_high,
            temp_alert_enabled,
            acc_alert_enabled,
            acc_alert_threshold,
            acc_alert_duration)

        return frame
