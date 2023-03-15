# Server Communication Protocol

- [Server Communication Protocol](#server-communication-protocol)
  - [Changelog](#changelog)
  - [Overview](#overview)
  - [Frames Structure](#frames-structure)
  - [Commands](#commands)
    - [Heartbeat](#heartbeat)
    - [Telemetry Request](#telemetry-request)
    - [Telemetry Response](#telemetry-response)
      - [External Sensor Types](#external-sensor-types)
    - [Read Config Request](#read-config-request)
    - [Write Config Request](#write-config-request)
    - [Read and Write Config Response](#read-and-write-config-response)
      - [Configurable variables](#configurable-variables)
    - [Log Request](#log-request)
    - [Log Response](#log-response)

## Changelog

| Version | Release Date | Comment                 |
| ------- | ------------ | ----------------------- |
| alpha   | 08-June-2020 | First protocol proposal |


## Overview

The communication between the _Device_ and the _Server_ is done over TCP sockets. The device sends and receives `Frames`. Each frame begins with a [start frame char](#frames-structure) and a three letter command `CMD`; each frame terminates with `\r\n` (CR followed by LF).


1. The _Device_ periodically opens a TCP socket to the _Server_, then sends a `Hearbeat Frame`:

```txt
+HRT,{queued_frames},{device_uid},{protocol_version}\r\n
```

Example:

```txt
+HRT,1,990000862471854,1\r\n
```


2. The _Server_ replies with a `Request Frame`:

```txt
$CMD,{keep_alive},{request_parameters}\r\n
```

Examples:

```txt
$TEL,1\r\n

$RCF,0\r\n
```


3. The _Device_ replies with one or multiple `Response Frames`:

```txt
@CMD,{response_parameters}
```

Example:

```txt
@TEL,1,270520,144403.000,43.76234,-79.32444,A,123.48,1.21,5,38.43,25.8,99902,40,-32,1008,3157,4,165,42467\r\n

@TEL,2,270520,144503.000,43.76234,-79.32444,A,123.48,1.21,5,38.43,25.8,99902,40,-32,1008,3157,4,165,42467\r\n
```


4. (Optional) The _Device_ sends another `Heartbeat Frame` based on the `{keep alive}` value from _step #2_ and will wait for another `Request Frame`

5. The _Device_ closes the socket connection


## Frames Structure

- Each frame begins with a `Start Character`:

| Frame Type | Start Character |
| ---------- | --------------- |
| Heartbeat  | `+`             |
| Request    | `$`             |
| Response   | `@`             |

- After the `Start Character` comes a three-character `Command Name`
  - e.g. `HRT`, `TEL`

- Next comes a list of comma seperated parameters specific to the command

- Each frame is terminated by a _Carriage Return_ and a _Line Feed_: `\r\n`

  
## Commands

### Heartbeat

```txt
+HRT,{queued_telemetry_frames},{device_uid},{protocol_version}\r\n
```

Example:

```txt
+HRT,1,240AC4C7C35C,1\r\n
```

| Parameter               | Type      | Description                                                                     |
| ----------------------- | --------- | ------------------------------------------------------------------------------- |
| queued_telemetry_frames | `Integer` | Number of queued `@TEL` frames that will be sent after a `$TEL`                 |
| device_uid              | `String`  | A unique identifier of the board/SoC                                            |
| protocol_verion         | `Integer` | An integer number representing the version of this communications protocol used |


### Telemetry Request

```txt
$TEL,{keep_alive}\r\n
```

Example:

```txt
$TEL,0\r\n
```

| Parameter  | Type      | Description                                                                                                                                                                                                  |
| ---------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| keep_alive | `Boolean` | If the value is `1`, the _Device_ will send another `Heartbeat Frame` after the response frame(s). Otherwise, if the value is `0`, the _Device_ will close the socket connection after the response frame(s) |

### Telemetry Response

The telmetry response is sent as a list of frames. Like all frames each `@TEL` frame is terminated with `\r\n`, and the whole response is terminated with the `EOT` ("End of Transmission", hex value `04`) ASCII character.
The `queued_telemetry_frames` value from `+HRT` frame corresponds to the number of `@TEL` frames that would be sent as response to `$TEL`. In case there are no queued frames, the reponse will consist only out of the `EOT` character.

```txt
@TEL,{utc_datetime},{lat},{lng},{cog},{speed},{battery_voltage},{acc_activity_alert},{acc_x},{acc_y},{acc_z},{acc_roll},{acc_pitch},{temp_alert},{temp_1},{temp_2},{temp_3},{temp_4},{ex_type},{ex_uid},{ex_acc_x},{ex_acc_y},{ex_acc_z},{ex_humidity},{ex_temp},{ex_pressure},{ex_battery_voltage},{ex_tx_power}\r\n
@TEL,{utc_datetime},{lat},{lng},{cog},{speed},{battery_voltage},{acc_activity_alert},{acc_x},{acc_y},{acc_z},{acc_roll},{acc_pitch},{temp_alert},{temp_1},{temp_2},{temp_3},{temp_4},{ex_type},{ex_uid},{ex_acc_x},{ex_acc_y},{ex_acc_z},{ex_humidity},{ex_temp},{ex_pressure},{ex_battery_voltage},{ex_tx_power}\r\n
@TEL,{utc_datetime},{lat},{lng},{cog},{speed},{battery_voltage},{acc_activity_alert},{acc_x},{acc_y},{acc_z},{acc_roll},{acc_pitch},{temp_alert},{temp_1},{temp_2},{temp_3},{temp_4},{ex_type},{ex_uid},{ex_acc_x},{ex_acc_y},{ex_acc_z},{ex_humidity},{ex_temp},{ex_pressure},{ex_battery_voltage},{ex_tx_power}\r\n
\x04
```

Example:

```txt
TODO add some examples
```

| Parameter          | Type      | Description                                                                                                                                                                                                                                           |
| ------------------ | --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| utc_datetime       | `String`  | Date and time string in ISO 8601 format recorded when device woke up just before reading sensors. Internal clock on the device which is synced using an NTP server on device startup. Example of the date/time string `2020-06-05T22:13:31.754+00:00` |
| lat                | `Float`   | Latitude                                                                                                                                                                                                                                              |
| lng                | `Float`   | Longitude                                                                                                                                                                                                                                             |
| cog                | `Float`   | Course over ground from GPS [degrees]                                                                                                                                                                                                                 |
| speed              | `Float`   | Speed from GPS[knots]                                                                                                                                                                                                                                 |
| battery_voltage    | `Float`   | Voltage of the battery powering the device                                                                                                                                                                                                            |
| acc_activity_alert | `Boolean` | `1`=alert was raised; `0`=no alert. Indicates that the device woke up from sleep due to accelerometer activity (see config params for more details: `acc_alert_enabled`, `acc_alert_threshold`, and `acc_alert_duration`)                             |
| acc_x              | `Float`   | Acceleration in the X direction read from the PyTrack LIS2HH12 sensor                                                                                                                                                                                 |
| acc_y              | `Float`   | Acceleration in the Y direction read from the PyTrack LIS2HH12 sensor                                                                                                                                                                                 |
| acc_z              | `Float`   | Acceleration in the Z direction read from the PyTrack LIS2HH12 sensor                                                                                                                                                                                 |
| acc_roll           | `Float`   | Accelerometer "roll" rotation in degrees (between -180 to 180)                                                                                                                                                                                        |
| acc_pitch          | `Float`   | Accelerometer "pitch" rotation in degrees (between -180 to 180)                                                                                                                                                                                       |
| temp_alert         | `Boolean` | `1`=alert was raised; `0`=no alert. Indicates that the temperature alert was raised because it went below or above the set limits (see config these config params for more details: `temp_alert_low`, `temp_alert_high`, and `temp_alert_enabled`)    |
| temp_1             | `Float`   | Temperature sensor 1 [celsius]                                                                                                                                                                                                                        |
| temp_2             | `Float`   | Temperature sensor 2 [celsius]                                                                                                                                                                                                                        |
| temp_3             | `Float`   | Temperature sensor 3 [celsius]                                                                                                                                                                                                                        |
| temp_4             | `Float`   | Temperature sensor 4 [celsius]                                                                                                                                                                                                                        |
| ex_type            | `Integer` | Enumeration representing the type of the external sensor (see [table of possible values](#external-sensor-types) below)                                                                                                                               |
| ex_uid             | `String`  | Unique identifier of an external sensor device                                                                                                                                                                                                        |
| ex_acc_x           | `Integer` | Acceleration in the X direction read from an external sensor device                                                                                                                                                                                   |
| ex_acc_y           | `Integer` | Acceleration in the Y direction read from an external sensor device                                                                                                                                                                                   |
| ex_acc_z           | `Integer` | Acceleration in the Z direction read from an external sensor device                                                                                                                                                                                   |
| ex_humidity        | `Float`   | Humidity read from an external sensor device                                                                                                                                                                                                          |
| ex_temp            | `Float`   | Humidity read from an external sensor device                                                                                                                                                                                                          |
| ex_pressure        | `Integer` | Humidity read from an external sensor device                                                                                                                                                                                                          |
| ex_battery_voltage | `Integer` | Voltage of the battery powering the external sensor device [mili volts]                                                                                                                                                                               |
| ex_tx_power        | `Float`   | Transmission power of communication with the external sensor device                                                                                                                                                                                   |


#### External Sensor Types

| Value | Description |
| ----- | ----------- |
| 0     | None        |
| 1     | Ruuvi Tag   |


### Read Config Request

Request the device to send the current values of all the [configurable variables](#configurable-variables)

```txt
$RCF,{keep_alive}\r\n
```

Example:

```txt
$RCF,0\r\n
```

### Write Config Request

Request the device to change the value(s) of the [configurable variables](#configurable-variables). Only the specified values would be written, meaning if a variable value is left blank it will be ignored and not changed.

```txt
$WCF,{keep_alive},{log_level},{log_file_size},{sleep_seconds},{server_address},{server_port},{server_user_ssl},{server_timeout},{apn},{lte_timeout},{ruuvi_enabled},{ruuvi_mac},{ruuvi_timeout},{temp_alert_low},{temp_alert_high},{temp_alert_enabled},{acc_alert_enabled},{acc_alert_threshold},{acc_alert_duration}\r\n
```

Example:

```txt
$WCF,0,3,,,,,,,,,,,,,,,,,\r\n
```

The example above will only change the `log_level`


### Read and Write Config Response

The device reponse for read or write config requests is the same. The frame will have all the values of the configurable variables.
```txt
@CFG,{log_level},{log_file_size},{sleep_seconds},{sleep_gps_on},{server_address},{server_port},{server_use_ssl},{server_timeout},{apn},{lte_timeout},{gps_timeout},{ruuvi_enabled},{ruuvi_mac},{ruuvi_timeout},{temp_alert_low},{temp_alert_high},{temp_alert_enabled},{acc_alert_enabled},{acc_alert_threshold},{acc_alert_duration}\r\n
```

Example:

```txt
@CFG,3,1,30,1,trackensure.com,8883,0,10,iot.aer.net,10,,15,0,FFFFFFFFFFFF,10,-10.0,50.0,0,0,200,300\r\n
```

#### Configurable variables

| Variable            | Type      | Default Value     | Example Value(s)                                | Comment                                                                                                                                                                                                                                             |
| ------------------- | --------- | ----------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| log_level           | `Integer` | `1`               | `0`=OFF, `1`=ERROR, `2`=INFO, or `3`=DEBUG      |                                                                                                                                                                                                                                                     |
| log_file_size       | `Integer` | `1`               |                                                 | [_megabytes_] The max size of a log file before it rotates to a new file. Log files are saved on the SD card and there are 2 files in total (one current and one old).                                                                              |
| sleep_seconds       | `Integer` | `30`              |                                                 | [_seconds_] Time the device spends in deep sleep mode (low power consumption)                                                                                                                                                                       |
| sleep_gps_on        | `Boolean` | `1`               | `0`=NO or `1`=YES                               | Keep the GPS module on durin gdeep sleep of the device. This will significantly reduce the time it takes for the GPS module to get a satelite fix every time the device wakes up                                                                    |
| server_address      | `String`  | `trackensure.com` | `trackensure.com/path/to/api` or `123.45.67.89` |                                                                                                                                                                                                                                                     |
| server_port         | `Integer` | `8883`            | ``                                              |                                                                                                                                                                                                                                                     |
| server_use_ssl      | `Boolean` | `0`               | `0`=NO or `1`=YES                               |                                                                                                                                                                                                                                                     |
| server_timeout      | `Integer` | `10`              |                                                 | [_seconds_] TCP socket connection timeout                                                                                                                                                                                                           |
| apn                 | `String`  | `iot.aer.net`     |                                                 | APN (Access Point Name) for the LTE network                                                                                                                                                                                                         |
| lte_timeout         | `Integer` | `10`              |                                                 | [_seconds_] Timeout for attaching to LTE cell network                                                                                                                                                                                               |
| gps_timeout         | `Integer` | `15`              |                                                 | [_seconds_] Timeout for reading data from the GPS module                                                                                                                                                                                            |
| ruuvi_enabled       | `Boolean` | `0`               |                                                 | Scan for a Ruuvi Tag device using BLE                                                                                                                                                                                                               |
| ruuvi_mac           | `String`  | `FFFFFFFFFFFF`    | `DA68B8C24CC4`                                  | MAC address (_ALL CAPS_ and without delimiter) of the of the Ruuvi Tag to read data from. If set to `FFFFFFFFFFFF` and `ruuvi_enabled`=`1` the device will read data from the first found Ruuvi                                                     |
| ruuvi_timeout       | `String`  | `10`              |                                                 | Timeout for scanning for a nearby Ruuvi Tag                                                                                                                                                                                                         |
| temp_alert_low      | `Float`   | `-10.0`           |                                                 | High temperate limit for interrupt/alert                                                                                                                                                                                                            |
| temp_alert_high     | `Float`   | `50.0`            |                                                 | Low temperate limit for interrupt/alert                                                                                                                                                                                                             |
| temp_alert_enabled  | `Boolean` | `0`               | `0`=DISABLED or `1`=ENABLED                     | Enable the temperature sensor interrupt/alert using the `temp_alert_low` and `temp_alert_high` values for the limit. Meaning the device will wakeup when the temperature goes below the `temp_alert_low` limit or above the `temp_alert_high` limit |
| acc_alert_enabled   | `Booealn` | `0`               | `0`=DISABLED or `1`=ENABLED                     | Enable the accelerometer sensor activity interrupt/alert using the `acc_alert_threshold` and `acc_alert_duration` values. The device will wakeup from deep sleep when the acceleration goes above the threshold for the sepcified duration.         |
| acc_alert_threshold | `Integer` | `200`             |                                                 | [_milli G force units_] Accelerometer sensor activity interrupt/alert threshold. The value must be between: `63-8000` (inclusive).                                                                                                                  |
| acc_alert_duration  | `Integer` | `300`             |                                                 | [_milliseconds_] Accelerometer sensor activity interrupt/alert duration. The value must be between: `160-40800` (inclusive).                                                                                                                        |



### Log Request

```txt
$LOG,{keep_alive}\r\n
```

Example:

```txt
$LOG,0\r\n
```

### Log Response

The log response will have the size of the log file in _bytes_ in the response frame followed by the text of the log file(s), and terminated with the `EOT` ASCII character ("End of Transmission", hex value `04`)

```txt
@LOG,{size_in_bytes}\r\n{log_file_text}\x04
```
