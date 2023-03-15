import os
import socket
import ssl
import sys
import json
import machine
import ubinascii

from model import *

# TODO Send firmware version in +HRT frame and add support for handling $OTA requests


class ServerUtil:

    PROTOCOL_VERSION = 1
    QUEUED_FRAMES_FILE = 'queued_frames'
    queued_frames = []  # list of the queued frame to be sent

    def __init__(self, log, config):
        self._log = log
        self._server_address = config.server_address
        self._server_port = config.server_port
        self._server_timeout = config.server_timeout
        self._use_ssl = config.server_use_ssl
        self._config = config

    def _concat_log(self):
        if ('sd' in os.listdir('/')):
            if ('log_old' in os.listdir('/sd') and 'log' in os.listdir('/sd')):
                with open('/sd/log_old', 'r') as file:
                    data_log_old = file.read().replace('\n', '')
                with open('/sd/log', 'r') as file:
                    data_log = file.read().replace('\n', '')
                concat_log = data_log + data_log_old
            elif ('log' in os.listdir('/sd')):
                with open('/sd/log', 'r') as file:
                    data_log = file.read().replace('\n', '')
                concat_log = data_log
        return concat_log

    def _log_file_size(self):
        if ('sd' in os.listdir('/')):
            if ('log_old' in os.listdir('/sd') and 'log' in os.listdir('/sd')):
                file_size = os.stat('/sd/log')[6] + os.stat('/sd/log_old')[6]
            elif ('log' in os.listdir('/sd')):
                file_size = os.stat('/sd/log')[6]

    def _read_queued_frames_from_file(self):
        self._log.debug('_read_queued_frames_from_file')
        queued_frames = []
        try:
            file_path = '/sd/{}'.format(self.QUEUED_FRAMES_FILE)
            if 'sd' in os.listdir('/') and self.QUEUED_FRAMES_FILE in os.listdir('/sd'):
                with open(file_path, 'r') as f:
                    frames_str = f.read()
                    for fr in frames_str.split('\r\n'):
                        queued_frames.append(fr+'\r\n')
                    queued_frames.pop()  # remove last item because it is an empty string with an '\r\n'
            else:
                self._log.debug(
                    'Queued frames file not found "{}"'.format(file_path))

        except Exception as ex:
            self._log.error(
                'ServerUtil._read_queued_frames_from_file: {}'.format(ex))
            sys.print_exception(ex)
        finally:
            return queued_frames

    def _delete_queued_frames_file(self):
        self._log.debug('_delete_queued_frames_file')
        try:
            file_path = '/sd/{}'.format(self.QUEUED_FRAMES_FILE)
            if 'sd' in os.listdir('/') and self.QUEUED_FRAMES_FILE in os.listdir('/sd'):
                os.remove(file_path)

        except Exception as ex:
            self._log.error(
                'ServerUtil._delete_queued_frames_file: {}'.format(ex))
            sys.print_exception(ex)

    def add_frame_to_file(self, frame):
        self._log.debug('_add_frame_to_file')
        try:
            file_path = '/sd/{}'.format(self.QUEUED_FRAMES_FILE)
            if 'sd' in os.listdir('/'):
                with open(file_path, 'a') as f:
                    f.write(frame)

        except Exception as ex:
            self._log.error('ServerUtil._add_frame_to_file: {}'.format(ex))
            sys.print_exception(ex)

    def create_heartbeat_frame(self, num_queued_frames=0):
        uid = ubinascii.hexlify(machine.unique_id()).decode('ascii').upper()

        frame = '+HRT,{},{},{}\r\n'.format(num_queued_frames,
                                           uid, self.PROTOCOL_VERSION)

        return frame

    def create_tel_frame(self, battery_voltage: float, position_data: Position, acc_activity_alert: int, acc_data: tuple, temp_data: tuple, ex_sensor_data: ExternalSensor):
        """Create a @TEL frame:

        @TEL,{utc_datetime},{lat},{lng},{cog},{speed},{battery_voltage},{acc_acitivity_alert},{acc_x},{acc_y},{acc_z},{acc_roll},{acc_pitch},{temp_alert},{temp_1},{temp_2},{temp_3},{temp_4},{ex_type},{ex_uid},{ex_acc_x},{ex_acc_y},{ex_acc_z},{ex_humidity},{ex_temp},{ex_pressure},{ex_battery_voltage},{ex_tx_power}\r\n

        Args:
            utc_datetime (String): ISO date time string
            battery_voltage (Float): Voltage of the device
            position_data (Position): Object containing the GPS position data (see model.py)
            acc_activity_alert (Integer): 0 or 1
            acc_data (Tuple): Tuple with 3 values: (acc_x, acc_y, acc_z)
            temp_data (Tuple): Tuple with 3 values: (temp_1, temp_2, temp_3)
            ex_sensor_data (ExternalSensor): Object containing the external sensor data (see model.py)
        """

        frame = '@TEL,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},,{},{},{},{},{},{},{},{}\r\n'.format(
            position_data.utc_datetime,
            position_data.lat,
            position_data.lng,
            position_data.cog,
            position_data.speed,
            battery_voltage,
            acc_activity_alert,
            acc_data[0],
            acc_data[1],
            acc_data[2],
            acc_data[3],
            acc_data[4],
            temp_data[0],
            temp_data[1],
            temp_data[2],
            temp_data[3],
            temp_data[4],
            ex_sensor_data.sensor_type,
            ex_sensor_data.uid,
            ex_sensor_data.acceleration_x,
            ex_sensor_data.acceleration_y,
            ex_sensor_data.acceleration_z,
            ex_sensor_data.humidity,
            ex_sensor_data.temperature,
            ex_sensor_data.pressure,
            ex_sensor_data.battery_voltage,
            ex_sensor_data.tx_power)

        return frame

    def create_cfg_frame(self):
        c = self._config
        frame = '@CFG,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\r\n'.format(
            c.log_level,
            c.log_file_size,
            c.sleep_seconds,
            c.server_address,
            c.server_port,
            c.server_use_ssl,
            c.server_timeout,
            c.apn,
            c.lte_timeout,
            c.gps_timeout,
            c.ruuvi_enabled,
            c.ruuvi_mac,
            c.ruuvi_timeout,
            c.temp_min,
            c.temp_max,
            c.temp_threshold_enabled,
            c.acc_alert_enabled,
            c.acc_alert_threshold,
            c.acc_alert_duration)
        return frame

    def create_log_frame(self):
        c = self._config

        frame = '@log,{}\r\n\x02{}\x03'.format(
            self._log_file_size(), self._concat_log())

        return frame

    def _send_heartbeat_and_handle_server_request(self, heartbeat_frame):
        frame_out = bytes(heartbeat_frame, 'ascii')
        try:
            self._socket.send(frame_out)

            self._log.debug('SENT:\n\t{}'.format(frame_out))

            frame_in = b''
            buffer = self._socket.recv(4096)
            while buffer and len(buffer) > 0:
                # self._log.debug('buffer:\n\t{}'.format(buffer))
                frame_in += buffer
                if (frame_in[-2:] == b'\r\n'):  # end of frame
                    break
            self._log.debug('RECEIVED:\n\t{}'.format(frame_in))

            frame_words = frame_in.decode('ascii').rstrip('\r\n').split(',')
            # In each frame the first word is {command}, and the second word is {keep_alive}
            cmd = frame_words[0]
            keep_alive = 0
            if(len(frame_words) > 1):
                keep_alive = frame_words[1]

            if cmd == '$TEL':
                self._tel_req(frame_words)
            elif cmd == '$RCF':
                self._rcf_req(frame_words)
            elif cmd == '$WCF':
                self._wcf_req(frame_words)
            elif cmd == '$LOG':
                self._log_req(frame_words)
            else:
                self._log.error(
                    'ServerUtil: Unknown command "{}"'.format(cmd))

            if keep_alive == '1':
                self._send_heartbeat_and_handle_server_request(
                    self.create_heartbeat_frame())
        except Exception as ex:
            self._log.error(
                'ServerUtil._send_heartbeat_and_handle_server_request: {}'.format(ex))
            sys.print_exception(ex)

    def _tel_req(self, frame_words):
        self._log.debug('_tel_req')
        for f in self.queued_frames:
            frame_out = bytes(f, 'ascii')
            self._socket.send(frame_out)
            self._log.debug('SENT:\n\t{}'.format(frame_out))

        # send EOT (end-of-transmission) ascii char (0x04)
        frame_out = bytes('\x04', 'ascii')
        self._socket.send(frame_out)
        self._log.debug('SENT:\n\t{}'.format(frame_out))

        self.queued_frames = []
        self._delete_queued_frames_file()

    def _rcf_req(self, frame_words):
        self._log.debug('_rcf_req')
        frame_out = bytes(self.create_cfg_frame(), 'ascii')
        self._socket.send(frame_out)
        self._log.debug('SENT:\n\t{}'.format(frame_out))

    def _wcf_req(self, frame_words):
        self._log.debug('_wcf_req')
        self._config.write_config_json(frame_words)
        frame_out = bytes(self._config.read_config_file(), 'ascii')
        self._socket.send(frame_out)
        self._log.debug('SENT:\n\t{}'.format(frame_out))

    def _log_req(self, frame_words):
        self._log.debug('_log_req')

        frame_out = bytes(self.create_log_frame(), 'ascii')
        self._socket.send(frame_out)
        self._log.debug('SENT:\n\t{}'.format(frame_out))

    def init(self):
        """Init communication with the server"""

        self.queued_frames = self._read_queued_frames_from_file()

        num_frames = len(self.queued_frames)
        self._log.debug('Queued frames: {}'.format(num_frames))

        heartbeat_frame = self.create_heartbeat_frame(num_frames)
        try:
            self._socket = socket.socket()
            self._socket.settimeout(self._server_timeout)
            if self._use_ssl == 1:
                self._socket = ssl.wrap_socket(s)  # TODO test with SSL
            self._log.debug('Connecting to server [{}:{}] (use_ssl={}, timeout={})'.format(
                self._server_address, self._server_port, self._use_ssl, self._server_timeout))

            self._socket.connect(socket.getaddrinfo(
                self._server_address, self._server_port)[0][-1])
            self._send_heartbeat_and_handle_server_request(heartbeat_frame)

            self._socket.close()
            return True
        except Exception as ex:
            self._log.debug('Exception in ServerUtil: {}'.format(ex))
            sys.print_exception(ex)

        return False
