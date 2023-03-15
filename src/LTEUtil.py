#!/usr/bin/env python
#
# This class is a utility to be used to control all communications
# with the LTE modem on the device.
#

from machine import Timer
import time
import gc
from network import LTE


class LTEUtil:

    def __init__(self, log, apn, timeout=None):
        self._lte = LTE()
        self._apn = apn
        self._log = log
        self.imei = self._get_imei()
        self.chrono = Timer.Chrono()
        self.timeout = timeout
        self.timeout_status = True

    def _get_imei(self):
        imei = ''
        try:
            at_cmd = 'AT+CGSN=1'
            result = self._lte.send_at_cmd(at_cmd)

            self._log.debug('AT SENT:\n\t{}'.format(at_cmd))
            self._log.debug('RECEIVED:\n\t{}'.format(repr(result)))

            # result should look something like this:
            #   "\r\n+CGSN: "354347xxxxxxxxx"\r\n\r\nOK"
            # The value between the double quotes is your IMEI

            s = result.find('"')+1
            e = result.rfind('"')

            imei = result[s:e]
        except Exception as ex:
            self._log.debug('Failed to get IMEI: {}'.format(ex))

        return imei

    def connect(self):
        self._log.debug(
            'Attaching cellular modem to a base station [apn={}]'.format(self._apn))

        # TODO figure out which band to use best, and what happens when you don't specify a band?
        # self._lte.attach(band=?,apn=apn)
        # TODO add timeout for attaching

        if self.timeout is not None:
            self.chrono.reset()
            self.chrono.start()

        if not self._lte.isattached():
            self._lte.attach(apn=self._apn)
        while not self._lte.isattached():
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                self._log.debug('Attaching LTE timed out')
                self.timeout_status = True
                break

            self._log.debug('Attaching...')
            time.sleep(0.25)
        self._log.debug('Attached successfully')

        self._log.debug('Starting a data session and obtaining an IP address')
        if not self._lte.isconnected():
            self._lte.connect()
        while not self._lte.isconnected():
            if self.timeout is not None and self.chrono.read() >= self.timeout:
                self.chrono.stop()
                chrono_timeout = self.chrono.read()
                self.chrono.reset()
                self.timeout_status = False
                debug_timeout = True
            if not self.timeout_status:
                gc.collect()
                self._log.debug('Connecting LTE timed out')
                break
            self._log.debug('...')
            time.sleep(0.25)

        self._log.debug('Connected to the network successfully')

    def disconnect(self):
        self._lte.disconnect()
        self._lte.dettach()
        # not sure if this is needed since we already dettach above
        self._lte.deinit(detach=True, reset=False)
        self._log.debug('Detached from LTE module and turned it off\n')

    def send_sms(self, number: str, message: str) -> bool:
        """Sends an SMS message [DOES NOT WORK!]

        Arguments:
            number {str} -- Destination number
            message {str} -- Text message

        Returns:
            bool -- Returns true if message was sent successfuly
        """
        self._log.debug(
            'send_sms:\n\tnumber=[{}]\n\tmessage=[{}]\n'.format(number, message))
        self._lte.pppsuspend()
        # res = self._lte.send_at_cmd('AT+CMGF=1')
        # self._log.debug(repr(res))

        # at_cmd = 'AT+CMGS="{}"\r'.format(number)
        # self._log.debug('sending:\n\t{}'.format(repr(at_cmd)))
        # res = self._lte.send_at_cmd(at_cmd);
        # self._log.debug('received:\n\t{}'.format(repr(res)))

        # at_cmd = '{}\x1a'.format(message)
        # self._log.debug('sending:\n\t{}'.format(repr(at_cmd)))
        # res = self._lte.send_at_cmd(at_cmd);
        # self._log.debug('received:\n\t{}'.format(repr(res)))

        self._log.debug('configuring for sms', end=' ')
        ans = self._lte.send_at_cmd('AT+CMGF=1').split('\r\n')
        self._log.debug(ans, end=' ')

        ans = self._lte.send_at_cmd('AT+CPMS="SM", "SM", "SM"').split('\r\n')
        self._log.debug(ans)
        self._log.debug()
        self._log.debug('receiving an sms', end=' ')
        ans = self._lte.send_at_cmd('AT+CMGL="all"').split('\r\n')
        self._log.debug(ans)
        self._log.debug()
        self._log.debug('sending an sms', end=' ')
        at_cmd = 'AT+SQNSMSSEND="{}", "{}"'.format(number, message)
        ans = self._lte.send_at_cmd(at_cmd).split('\r\n')

        self._lte.pppresume()
        return False
