from network import Bluetooth
from machine import Timer
import ustruct
import ubinascii
import gc

from model import ExternalSensor


class RuuviUtil:

    RUUVI_TAG_MAN_ID = b"\x99\x04"

    def __init__(self, log, timeout, ruuvi_mac):
        self.chrono = Timer.Chrono()

        self.timeout = timeout
        self.timeout_status = True

        self.log = log
        self.ruuvi_mac = ruuvi_mac

    def _decode_data_format_2and4(self, data):
        """RuuviTag URL decoder"""
        data = data.encode()
        identifier = None
        if len(data) > 8:
            identifier = data[8]
            data = data[:8]
        decoded = ubinascii.a2b_base64(data)

        data_format = decoded[0]
        humidity = decoded[1] / 2
        temperature = (decoded[2] & 127) + decoded[3] / 100
        pressure = ((decoded[4] << 8) + decoded[5]) + 50000

        return (data_format, humidity, temperature, pressure, identifier)

    def _decode_data_format_3(self, data):
        """RuuviTag RAW 1 decoder"""
        humidity = data[3] / 2

        temperature = data[4] + data[5] / 100
        if temperature > 128:
            temperature -= 128
            temperature = round(0 - temperature, 2)

        pressure = ustruct.unpack("!H", data[6:8])[0] + 50000

        acceleration_x = ustruct.unpack("!h", data[8:10])[0]
        acceleration_y = ustruct.unpack("!h", data[10:12])[0]
        acceleration_z = ustruct.unpack("!h", data[12:14])[0]

        battery_voltage = ustruct.unpack("!H", data[14:16])[0]

        return (
            3,
            humidity,
            temperature,
            pressure,
            acceleration_x,
            acceleration_y,
            acceleration_z,
            battery_voltage,
        )

    def _decode_data_format_5(self, data):
        """RuuviTag RAW 2 decoder"""
        temperature = ustruct.unpack("!h", data[3:5])[0] * 0.005

        humidity = ustruct.unpack("!H", data[5:7])[0] * 0.0025

        pressure = ustruct.unpack("!H", data[7:9])[0] + 50000

        acceleration_x = ustruct.unpack("!h", data[9:11])[0]
        acceleration_y = ustruct.unpack("!h", data[11:13])[0]
        acceleration_z = ustruct.unpack("!h", data[13:15])[0]

        power_bin = bin(ustruct.unpack("!H", data[15:17])[0])[2:]
        battery_voltage = int(power_bin[:11], 2) + 1600
        tx_power = int(power_bin[11:], 2) * 2 - 40

        movement_counter = data[18]

        measurement_sequence = ustruct.unpack("!H", data[18:20])[0]

        return (
            5,
            humidity,
            temperature,
            pressure,
            acceleration_x,
            acceleration_y,
            acceleration_z,
            battery_voltage,
            tx_power,
            movement_counter,
            measurement_sequence,
        )

    def _parse_data(self, adv_data, mac):
        self.log.debug("Ruuvi data format: {}".format(str(adv_data[2])))

        if adv_data[2] == 3:  # data format is 3
            d = self._decode_data_format_3(adv_data)
            return ExternalSensor(humidity=str(d[1]), temperature=str(d[2]), pressure=str(d[3]),
                 acceleration_x=str(d[4]), acceleration_y=str(d[5]), acceleration_z=str(d[6]),
                 battery_voltage=str(d[7]), uid=mac)
        elif adv_data[2] == 5:  # data format is 5
            d = self._decode_data_format_5(adv_data)
            return ExternalSensor(humidity=str(d[1]), temperature=str(d[2]), pressure=str(d[3]),
                 acceleration_x=str(d[4]), acceleration_y=str(d[5]), acceleration_z=str(d[6]),
                 battery_voltage=str(d[7]), tx_power=str(d[8]), movement_counter=str(d[9]),
                 measurement_sequence=str(d[10]), uid=mac)

    def get_sensor_data(self):
        data = ExternalSensor()  # empty data

        if self.timeout is not None:
            self.chrono.reset()
            self.chrono.start()

        bt = Bluetooth()
        # starts scanning indefinitely until bluetooth.stop_scan() is called
        bt.start_scan(-1)
        self.log.debug('Scanning for Ruuvi with MAC=[{}]'.format(self.ruuvi_mac))

        found = False
        while not found:
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                self.log.debug('Ruuvi scan timed out')
                break

            devices = bt.get_advertisements()

            for d in devices:
                adv_data = bt.resolve_adv_data(
                    d.data, Bluetooth.ADV_MANUFACTURER_DATA)
                if adv_data != None and adv_data[:2] == self.RUUVI_TAG_MAN_ID:

                    mac = ubinascii.hexlify(d.mac).decode('ascii').upper()
                    self.log.debug('Found Ruuvi [{}]'.format(mac))
                    if self.ruuvi_mac == 'FFFFFFFFFFFF':
                        # return first found tag
                        data = self._parse_data(adv_data, mac)
                        found = True
                        break
                    elif self.ruuvi_mac == mac:
                        # return tag with same mac as ruuvi_mac
                        data = self._parse_data(adv_data, mac)
                        found = True
                        break

        bt.stop_scan()

        return data
