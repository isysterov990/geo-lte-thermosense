
class Position:

    def __init__(self, lat='', lng='', utc_datetime='', speed='', cog=''):
        self.lat = lat
        self.lng = lng
        self.utc_datetime = utc_datetime
        self.speed = speed
        self.cog = cog

class ExternalSensor:

    def __init__(self, humidity='', temperature='', pressure='',
                 acceleration_x='', acceleration_y='', acceleration_z='',
                 battery_voltage='', tx_power='', movement_counter='',
                 measurement_sequence='', uid='', sensor_type=0):
        self.sensor_type = sensor_type
        self.uid = uid
        self.humidity = humidity
        self.temperature = temperature
        self.pressure = pressure
        self.acceleration_x = acceleration_x
        self.acceleration_y = acceleration_y
        self.acceleration_z = acceleration_z
        self.battery_voltage = battery_voltage
        self.tx_power = tx_power
        self.movement_counter = movement_counter
        self.measurement_sequence = measurement_sequence
