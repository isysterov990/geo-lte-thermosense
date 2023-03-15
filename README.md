# Retina Tracker

## Docs
- [Project Requirements](./doc/requirements.md)
- [Server Communication Protocol](./doc/protocol.md)
- [Power Consumption spreadsheet](https://docs.google.com/spreadsheets/d/1yKt7jXkSbqm5DyMouLU8X8WFjGBCADySog3blvWz7OY/edit?usp=sharing)

## Todo

- [x] Sync time with RTC
- [ ] Handle server communications using the defined protocol
  - [ ] Write to config file
  - [ ] Add firmware version and SD card status to heartbeat
- [x] Initial draft for the communications protocol [WIP]
- [x] LTE attaching/connecting timeout (default to 10 seconds)
- [x] Log to a file
- [x] Procedure for OTA updates
- [ ] Implement OTA updates with protocol
- [x] Flashing custom firware (code security)
- [ ] Figure out sending/receiving SMS
- [ ] Enclosure
    - https://toolless.com/
    - https://evatron.com/enclosures/rectangular-potting-boxes/rectangular-potting-boxes-rl-series/rl6115/

## Gpy Pinout   

![gpy-pinout](./doc/gpy-pinout.png)

## PyTrack Pinout

![pytrack-pinout](./doc/pytrack-pinout-1.png)

## Reset Cause values

```c
typedef enum {
    MPSLEEP_PWRON_RESET = 0,
    MPSLEEP_HARD_RESET,
    MPSLEEP_WDT_RESET,
    MPSLEEP_DEEPSLEEP_RESET,
    MPSLEEP_SOFT_RESET,
    MPSLEEP_BROWN_OUT_RESET,
} mpsleep_reset_cause_t;
```

## Resources

- pycom
  - [Offical pycom docs](https://docs.pycom.io)
  - [pycom libraries](https://github.com/pycom/pycom-libraries)
- MicroPython
  - [Official MicroPython docs](https://docs.micropython.org/en/latest/index.html)
  - [Guide to setup a new micropython project with vscode intellisense](https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense)
- Ruuvi
  - [Ruuvi firmware](https://lab.ruuvi.com/ruuvitag-fw/)
  - [Ruuvi sensor protocols](https://github.com/ruuvi/ruuvi-sensor-protocols)
- GNSS/GPS Module (Quectel L76GNSS)
  - [L76 Series GNSS Protocol Specification](./doc/Quectel_L76_Series_GNSS_Protocol_Specification_V3.3.pdf)
  - [Commands manual](./doc/Quectel_GNSS_SDK_Commands_Manual_V1.4.pdf)
- LTE modem (Sequans Monarch LR5110)
  - [AT Commands Reference Manual](./doc/Monarch-LR5110-ATCmdRefMan-rev6_noConfidential.pdf)
- Firmware
  - [Pycom Micropython](https://github.com/pycom/pycom-micropython-sigfox)
- NIST
   - [NIST security requirements Summary](https://www.nist.gov/news-events/news/2019/08/nist-releases-draft-security-feature-recommendations-iot-devices)
   - [NIST security requirements for iot devices](https://nvlpubs.nist.gov/nistpubs/ir/2020/NIST.IR.8259.pdf)
   - [NIST traceable calibration](https://www.nist.gov/calibrations)

