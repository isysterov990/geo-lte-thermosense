#!/usr/bin/env python

import machine
import pycom
import network
import gc

pycom.heartbeat(False)  # disable flashing of LED
pycom.pybytes_on_boot(False)

ap = network.WLAN()
ap.deinit()

server = network.Server()
server.deinit()

gc.enable()

machine.main('main.py')


