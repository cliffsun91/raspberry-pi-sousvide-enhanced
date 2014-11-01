import os, glob, sys
from time import sleep
import datetime
import sys

# Load the 1-wire modules (if modules are loaded on boot these two lines can be commented out)
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')


class SensorRepository(object):
	def __init__(self, base_dir='/sys/bus/w1/devices/'):
		self.base_dir = base_dir
		self.device_file = '/w1_slave'

	def get_sensor_from_id(self, sensor_id):
		return TempReader(self.base_dir + sensor_id + self.device_file)

	def get_all_sensors(self):
		devices_base_paths = glob.glob(self.base_dir + '28*')
		return map(lambda x: TempSensor(x + self.device_file), devices_base_paths)


class TempReader(object):
	def __init__(self, sensors):
		self.sensors = sensors

	def read_temps(self):
		return map(lambda s: s.read_temp(), self.sensors)
						

class TempSensor(object):
	def __init__(self, device_path):
		self.device_path = device_path

	def __read_temp_file(self):
		f = open(self.device_path, 'r')
		lines = f.readlines()
		f.close()
		return lines

	def __is_in_ready_state(self, raw_data):
		return raw_data[0].find('YES') >= 0

	def read_temp(self):
		raw_data = self.__read_temp_file()
		if not self.__is_in_ready_state(raw_data):
			return "Not Ready Yet"
		else:
			t_pos = raw_data[1].find('t=')
			if t_pos != -1:
				temp = float(raw_data[1][t_pos+2:]) / 1000
				#print('%s - %.1f%s' % (device, temp, u"\u00b0"+'C'))
				return temp
			else:
				raise Exception('could not read temp \'t=...\' from raw_data: {0}'.format(str(raw_data)))

