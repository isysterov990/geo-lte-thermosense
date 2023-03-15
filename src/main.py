#!/usr/bin/env python

import socket
import ssl
import sys
import time

import pycom
import ubinascii
import uos
from network import Bluetooth
from pytrack import Pytrack
from pycoproc import *
from L76GNSV4 import L76GNSS
from LIS2HH12 import LIS2HH12
from Config import Config
from Logger import Logger
from LTEUtil import LTEUtil
from RuuviUtil import RuuviUtil
from ServerUtil import ServerUtil
from model import ExternalSensor, Position
from SensorsHandler import SensorsHandler


def mount_sd_card():
    if 'sd' in os.listdir('/'):
        # already mounted
        return True
    try:
        print('Mounting SD card...')
        sd = machine.SD()
        os.mount(sd, '/sd')
        return True
    except Exception as ex:
        print('Failed to mount SD: ', ex)

    return False


def read_position_data(py: Pytrack):
    log = Logger.get_instance()
    try:
        config = Config.get_instance()
        L76 = L76GNSS(pytrack=py, timeout=config.gps_timeout)
        L76.setAlwaysOn()
        # L76.setPeriodicMode(2,30000,20000,60000,60000)
        lat = ''
        lng = ''
        datetime = ''
        speed = ''
        cog = ''

        chrono = machine.Timer.Chrono()
        chrono.reset()
        chrono.start()
        fixed = L76.get_fix()
        if fixed:
            chrono.stop()
            log.debug('GPS fixed in {} seconds'.format(chrono.read()))
            coords = L76.coordinates()
            lat = coords['latitude']
            lng = coords['longitude']

            s = L76.get_speed()
            speed = s['speed']
            cog = s['COG']
        else:
            log.debug('GPS failed to fix within {} seconds'.format(
                config.gps_timeout))

        datetime = L76.getUTCDateTime()
        if datetime is None:
            datetime = ''

        log.debug('{},{},{},{},{}'.format(datetime, lat, lng, speed, cog))

        return Position(lat, lng, datetime, speed, cog)
    except Exception as ex:
        log.error('Failed to read_position_data!', ex)

    return Position()


def read_temperature_and_setup_alert():
    log = Logger.get_instance()
    config = Config.get_instance()
    temp_data = ('0', '', '', '', '')
    try:
        sensors = SensorsHandler(log)
        temps = sensors.get_temperatures()

        # it's very important that the setup_alert() is called after the clear_alert() and not before!
        # the alert will be cleared only if it is raised
        temp_alert = sensors.clear_alert()

        if config.temp_alert_enabled:
            sensors.setup_alert(config.temp_alert_low, config.temp_alert_high)

        temp_data = (str(temp_alert), temps[0], temps[1], temps[2], temps[3])
    except Exception as ex:
        log.error('Failed to read temp sensors!', ex)
    finally:
        log.debug('Temp sensors: {}'.format(temp_data))

    return temp_data


def read_accelerometer_and_setup_alert():
    log = Logger.get_instance()
    config = Config.get_instance()
    acc_data = (0, 0, 0, 0, 0)
    try:
        accelerometer = LIS2HH12()
        acc = accelerometer.acceleration()
        roll = accelerometer.roll()
        pitch = accelerometer.pitch()

        acc_data = (acc[0], acc[1], acc[2], roll, pitch)

        if config.acc_alert_enabled:
            accelerometer.enable_activity_interrupt(
                threshold=config.acc_alert_threshold, duration=config.acc_alert_duration)
    except Exception as ex:
        log.error('Failed to read accelerometer!', ex)
    finally:
        log.debug('Accelerometer: {}'.format(acc_data))

    return acc_data


def read_external_sensor():
    log = Logger.get_instance()
    config = Config.get_instance()
    ex_sensor = ExternalSensor()  # empty object
    try:
        if config.ruuvi_enabled == 1:
            ruuvi = RuuviUtil(log, config.ruuvi_timeout, config.ruuvi_mac)
            ex_sensor = ruuvi.get_sensor_data()
    except Exception as ex:
        log.error('Failed to read external sensor', ex)

    return ex_sensor


GREEN = 0x007f00
RED = 0x7f0000
BLUE = 0x00007f
YELLOW = 0x7f7f00


def flash_LED(count=1, speed=400, color=GREEN):
    for i in range(count):
        pycom.rgbled(color)
        time.sleep_ms(speed)
        pycom.rgbled(0)
        time.sleep_ms(speed)


RESET_CAUSE_DICT = {
    '0': 'PWRON_RESET',
    '1': 'HARD_RESET',
    '2': 'WDT_RESET',
    '3': 'DEEPSLEEP_RESET',
    '4': 'SOFT_RESET',
    '5': 'BROWN_OUT_RESET'
}

WAKE_REASON_DICT = {
    '1': 'ACCELEROMETER',
    '2': 'PUSH_BUTTON',
    '4': 'TIMER',
    '8': 'INT_PIN'
}


def run():
    flash_LED(2, 180)
    pytrack = Pytrack()
    mount_sd_card()
    log = None
    config = None
    try:
        config = Config.get_instance()  # init and read config file
        log = Logger.get_instance()

        log.info('------ WAKEUP')
        time.sleep(1)

        reset_cause = machine.reset_cause()
        reset_cause_s = RESET_CAUSE_DICT[str(reset_cause)]
        wake_reason = pytrack.get_wake_reason()
        wake_reason_s = WAKE_REASON_DICT[str(wake_reason)]

        log.info('reset_cause: {}'.format(reset_cause_s))
        log.info('wake_reason: {}'.format(wake_reason_s))

        # read battery voltage
        batt_voltage = pytrack.read_battery_voltage()
        log.debug('Battery voltage: {}'.format(batt_voltage))

        temp_data = read_temperature_and_setup_alert()
        acc_activity_alert = 1 if wake_reason == WAKE_REASON_ACCELEROMETER else 0
        acc_data = read_accelerometer_and_setup_alert()
        ex_sensor = read_external_sensor()  # ruuvi
        position = read_position_data(pytrack)

        serverUtil = ServerUtil(log, config)
        # construct the new TEL frame
        new_tel_frame = serverUtil.create_tel_frame(
            batt_voltage, position, acc_activity_alert, acc_data, temp_data, ex_sensor)

        serverUtil.add_frame_to_file(new_tel_frame)  # add to queue

        lte = LTEUtil(log, config.apn, timeout=config.lte_timeout)
        try:
            lte.connect()
            serverUtil.init()  # init communications with backend server
        except Exception as ex:
            log.error('Exception occured!', ex)
        finally:
            lte.disconnect()

    except Exception as ex:
        log.error('Exception occured!', ex)
    finally:
        if log != None:
            log.info('------ DEEP SLEEP ({} seconds)'.format(config.sleep_seconds))
            log.deinit()
            machine.idle()
            flash_LED(2, 180, YELLOW)
            if config.temp_alert_enabled:
                # Setup interrupt for temp sensor
                # Pass 'False' means interrupt on falling edge
                pytrack.setup_int_pin_wake_up(False)
            if config.acc_alert_enabled:
                # Setup interrupt for accelerometer activity
                # Pass `True, False` means interrupt on activity, and do not intterupt on inactivity
                pytrack.setup_int_wake_up(True, False)
            pytrack.setup_sleep(config.sleep_seconds)
            keep_gps_on = (config.sleep_gps_on == 1)
            pytrack.go_to_sleep(gps=keep_gps_on)
            # machine.deepsleep(config.sleep_seconds*1000)  # milliseconds
        else:
            # super edge case where config and logger failed
            machine.reset()


run()
