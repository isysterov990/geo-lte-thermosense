import struct
import time
from machine import I2C
from BitUtil import *

# Value found in the device ID register on reset (page 24 Table 3 of datasheet)
DEVICE_ID_VALUE = 0x0117
# Resolution of the device, found on (page 1 of datasheet)
TMP117_RESOLUTION = 0.0078125
CONTINUOUS_CONVERSION_MODE = 0b00  # Continuous Conversion Mode
ONE_SHOT_MODE = 0b11				# One Shot Conversion Mode
SHUTDOWN_MODE = 0b01				# Shutdown Conversion Mode

# Possible I2C address of the TMP117 (page 20 Table 2 of datasheet)
TMP117_I2CADDR_GND = 0x48
TMP117_I2CADDR_VCC = 0x49
TMP117_I2CADDR_SDA = 0x4A
TMP117_I2CADDR_SCL = 0x4B

# Registers of the TMP117 (page 24 Table 3 of datasheet)
TEMP_RESULT_REG = 0x00  # read only
CONFIGURATION_REG = 0x01
T_HIGH_LIMIT_REG = 0x02
T_LOW_LIMIT_REG = 0x03
EEPROM_UL_REG = 0x04
EEPROM1_REG = 0x05
EEPROM2_REG = 0x06
TEMP_OFFSET_REG = 0x07
EEPROM3_REG = 0x08
DEVICE_ID_REG = 0x0F  # read only

MASK_DEVICE_ID_REG_DID = 0x0FFF
MASK_DEVICE_ID_REG_REV = 0xF000

MOD_CC = 0  # Continuous conversion
MOD_SD = 1  # Shutdown
MOD_CC_2 = 2  # Continuous conversion(CC),Same as 00 (readsback=00)
MOD_OS = 3  # One shot conversion

# modes for the alert function (bit 4 in the config register)
# see section 7.4.4 (page 14) of datasheet
ALERT_MODE_THERM = 0
ALERT_MODE_ALERT = 1

# options for alert polarity (bit 3 in the config register)
ALERT_POL_ACTIVE_LOW = 0
ALERT_POL_ACTIVE_HIGH = 1


class TMP117:

    def __init__(self, sda='P10', scl='P11', device_addr=TMP117_I2CADDR_GND):
        self._device_addr = device_addr  # I2C address of Temperature sensor
        self._i2c = I2C(0, mode=I2C.MASTER, pins=(sda, scl))

        # see "Device ID Register Description" (page 31 Table 15 of datasheet)
        r = self._i2c.readfrom_mem(self._device_addr, DEVICE_ID_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        did = r_int & MASK_DEVICE_ID_REG_DID
        rev = r_int & MASK_DEVICE_ID_REG_REV
        # print(repr((did, rev)))
        if (did != DEVICE_ID_VALUE):
            raise ValueError(
                'TMP117 not found at address [{}]'.format(hex(device_addr)))

    # uint8_t getAddress();
    def get_address(self):
        """Returns the address of the device"""
        return self._device_addr

    # double readTempC();
    def read_temp_c(self):
        """Returns the temperature in degrees C"""
        r = self._i2c.readfrom_mem(self._device_addr, TEMP_RESULT_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        # Multiply by the resolution to get the final temp
        temp = r_int * TMP117_RESOLUTION
        return temp

    # void softReset();
    def soft_reset(self):
        """Performs a software reset on the Configuration Register Field bits"""
        r_int = self.get_config_reg()
        r_int = setBit(r_int, 1)
        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    # float getTemperatureOffset();
    def get_temp_offset(self):
        """Reads the temperature offset"""
        r = self._i2c.readfrom_mem(self._device_addr, TEMP_OFFSET_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        offset = r_int * TMP117_RESOLUTION
        return offset

    # void setTemperatureOffset(float offset);
    def set_temp_offset(self, offset):
        """Writes to the temperature offset"""
        offset = offset / TMP117_RESOLUTION
        r = struct.pack('>h', int(offset))
        self._i2c.writeto_mem(self._device_addr, TEMP_OFFSET_REG, r)

    # float getLowLimit();
    def get_low_limit(self):
        """Reads the low limit register that is set by the user. The values are signed integers since they can be negative."""
        r = self._i2c.readfrom_mem(self._device_addr, T_LOW_LIMIT_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        limit = r_int * TMP117_RESOLUTION
        return limit

    # void setLowLimit(float lowLimit);
    def set_low_limit(self, low_limit):
        """Sets the low limit temperature for the low limit register"""
        low_limit = low_limit / TMP117_RESOLUTION
        r = struct.pack('>h', int(low_limit))
        self._i2c.writeto_mem(self._device_addr, T_LOW_LIMIT_REG, r)
        pass

    # float getHighLimit();
    def get_high_limit(self):
        """Reads the high limit register that is set by the user. The values are signed integers since they can be negative."""
        r = self._i2c.readfrom_mem(self._device_addr, T_HIGH_LIMIT_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        limit = r_int * TMP117_RESOLUTION
        return limit

    # void setHighLimit(float highLimit);
    def set_high_limit(self, high_limit):
        """Sets the high limit temperature for the low limit register"""
        high_limit = high_limit / TMP117_RESOLUTION
        r = struct.pack('>h', int(high_limit))
        self._i2c.writeto_mem(self._device_addr, T_HIGH_LIMIT_REG, r)

    # uint16_t getConfigurationRegister();
    def get_config_reg(self):
        """Get Configuration Register"""
        r = self._i2c.readfrom_mem(self._device_addr, CONFIGURATION_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        return r_int

    def get_low_and_high_alert(self):
        """Reads in Alert mode for a high and low alert flags"""
        r_int = 0
        r_int = self.get_config_reg()
        high_alert = readBit(r_int, 15)
        low_alert = readBit(r_int, 14)
        return (low_alert, high_alert)

    # bool getHighAlert();
    def get_high_alert(self):
        """Reads in Alert mode for a high alert flag"""
        r_int = 0
        r_int = self.get_config_reg()
        high_alert = readBit(r_int, 15)
        return high_alert

    # bool getLowAlert();
    def get_low_alert(self):
        """Reads in Alert mode for a low alert flag"""
        r_int = 0
        r_int = self.get_config_reg()
        high_alert = readBit(r_int, 14)
        return high_alert

    def set_alert_function_mode(self, mode):
        """Set alert or therm mode.
            For 'mode' use one of the constnats: ALERT_MODE_THERM or ALERT_MODE_ALERT"""
        r_int = 0
        r_int = self.get_config_reg()
        if mode == ALERT_MODE_THERM:    # == 0
            r_int = clearBit(r_int, 4)
        elif mode == ALERT_MODE_ALERT:  # == 1
            r_int = setBit(r_int, 4)
        else:
            return  # invalid mode, do nothing
        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    def get_alert_function_mode(self):
        """Check to see if in alert or therm mode"""
        r_int = self.get_config_reg()
        mode = readBit(r_int, 4)
        return mode

    def set_alert_pin_polarity(self, pol):
        r_int = 0
        r_int = self.get_config_reg()
        if pol == ALERT_POL_ACTIVE_LOW:
            r_int = clearBit(r_int, 3)
        elif pol == ALERT_POL_ACTIVE_HIGH:
            r_int = setBit(r_int, 3)
        else:
            return  # invalid polarity, do nothing
        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    def get_conversion_mode(self):
        """Checks to see the Conversion Mode the device is currently in. The mode is the bit 10 and 11"""
        conf_reg = self.get_config_reg()
        mod = conf_reg >> 10 & 3
        return mod

    # void setContinuousConversionMode();
    def set_continuous_conversion_mode(self):
        """Sets the Conversion Mode of the Device to be Continuous"""
        r_int = self.get_config_reg()

        # Set bits 11:10 to 00, which is the continuous conversion mode
        r_int = clearBit(r_int, 11)
        r_int = clearBit(r_int, 10)

        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    # void setOneShotMode();
    def set_one_shot_mode(self):
        """Sets the Conversion Mode of the Device to be One Shot"""
        r_int = self.get_config_reg()

        # Set bits 11:10 to 11, which is the oneshot mode
        r_int = setBit(r_int, 11)
        r_int = setBit(r_int, 10)

        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    # void setShutdownMode();
    def set_shutdown_mode(self):
        """Sets the Conversion Mode of the Device to be Shutdown"""
        r_int = self.get_config_reg()

        # Set bits 11:10 to 01, which is the shutdown mode
        r_int = clearBit(r_int, 11)
        r_int = setBit(r_int, 10)

        r = struct.pack('>h', r_int)
        self._i2c.writeto_mem(self._device_addr, CONFIGURATION_REG, r)

    # void setConversionAverageMode(uint8_t convMode);
    def set_conversion_average_mode(self, mode):
        """Sets the conversion averaging mode"""
        # TODO
        pass

    # uint8_t getConversionAverageMode();
    def get_conversion_average_mode(self):
        """Returns the Conversion Averaging Mode"""
        # TODO
        pass

    # void setConversionCycleBit(uint8_t convTime);
    def set_conversion_cycle_bit(self, conv_time):
        """Sets the conversion cycle time bit"""
        # TODO
        pass

    # uint8_t getConversionCycleBit();
    def get_conversion_cycle_bit(self):
        """Returns the conversion cycle time bit value"""
        # TODO
        pass

    # bool dataReady();
    def data_ready(self):
        """Returns 1 when data is ready. """
        r = self._i2c.readfrom_mem(self._device_addr, CONFIGURATION_REG, 2)
        r_int = struct.unpack('>h', r)[0]
        ready = r_int >> 13 & 1
        return ready
