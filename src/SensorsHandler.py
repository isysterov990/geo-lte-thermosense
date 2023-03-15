from TMP117 import *
from Logger import Logger
import time


class SensorsHandler:

    _temp_1 = None
    _temp_2 = None
    _temp_3 = None
    _temp_4 = None

    def __init__(self, log):
        self._log = log
        # try and init all the four possible temperature sensors
        try:
            self._temp_1 = TMP117(device_addr=TMP117_I2CADDR_GND)
        except Exception as ex:
            self._log.debug(
                'Failed to init temperature sensor 1: {}'.format(ex))

        try:
            self._temp_2 = TMP117(device_addr=TMP117_I2CADDR_VCC)
        except Exception as ex:
            self._log.debug(
                'Failed to init temperature sensor 2: {}'.format(ex))

        try:
            self._temp_3 = TMP117(device_addr=TMP117_I2CADDR_SDA)
        except Exception as ex:
            self._log.debug(
                'Failed to init temperature sensor 3: {}'.format(ex))

        try:
            self._temp_4 = TMP117(device_addr=TMP117_I2CADDR_SCL)
        except Exception as ex:
            self._log.debug(
                'Failed to init temperature sensor 4: {}'.format(ex))

        if not self._temp_1 and not self._temp_2 and not self._temp_3 and not self._temp_4:
            self._log.error('No temperature sensors!')

    def _read_temp_sensor(self, sensor):
        """Read the temperature from the given sensor as a string.
        Return an empty string if sensor is unavailable"""

        t = ''
        if sensor:
            count = 0  # avoid infinite loop
            while not sensor.data_ready() and count < 10:
                time.sleep(0.1)
                count += 1
            t = str(sensor.read_temp_c())
        return t

    def get_temperatures(self):
        """Returns a tuple with 4 values (strings) for each temp sensors.
        The value will be an empty string for each unavailable sensor."""

        t1 = self._read_temp_sensor(self._temp_1)
        t2 = self._read_temp_sensor(self._temp_2)
        t3 = self._read_temp_sensor(self._temp_3)
        t4 = self._read_temp_sensor(self._temp_4)

        return (t1, t2, t3, t4)

    # this only works for the first sensor: _temp_1 because we can use only 1 interrupt pin
    def setup_alert(self, low_limit, high_limit):
        if self._temp_1:
            self._temp_1.set_continuous_conversion_mode()
            # self._temp_1.set_alert_pin_polarity(ALERT_POL_ACTIVE_HIGH)
            self._temp_1.set_alert_function_mode(ALERT_MODE_ALERT)
            self._temp_1.set_low_limit(low_limit)
            self._temp_1.set_high_limit(high_limit)

    def clear_alert(self):
        """ clears the alert only if it was raised by reseting the sensor.
        Returns 1 if alert was raised"""
        if self._temp_1:
            low_alert, high_alert = self._temp_1.get_low_and_high_alert()
            if low_alert or high_alert:
                self._temp_1.soft_reset()
                time.sleep_ms(3) # it takes 2 ms for the sensor to reset, wait 3 ms to be safe
                return 1
        
        return 0
    