import os, glob, sys
from time import sleep
import datetime
import sys

# Load the 1-wire modules (if modules are loaded on boot these two lines can be commented out)
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')


class LoopTempReader(object):
	def __init__(self, log_file="/home/pi/projects/RPi_sousvide/temps.log", max_lines=40):
		self.log_file = log_file
		self.max_lines = max_lines
		self.file_writer = FileWriter(self.log_file)

	def loop_read(self):
		sensor_repo = SensorRepository()
		sensors = sensor_repo.get_all_sensors()
		if len(sensors) == 0:
			raise Exception("No sensors found! Check '/sys/bus/w1/devices/' for sensor devices, you may have to run sudo modprobe w1-gpio/therm")
		reader = TempReader(sensors)
		self.truncate_temp_logs(self.log_file, self.max_lines)
		self.file_writer.append_to_end_of_file("---------- Temp Logging Started {0} ----------\n".format(self.get_time_now()))
		while True:
			try:
				sleep(10)
				temps = reader.read_temps()
				time = self.get_time_now()
				index = 0
				for temp in temps:
					index += 1
					temp_string = u"Sensor {0} - time: {1} | temp: {2}{3}\n".\
										format(index, time, str(temp), u"\u00b0"+'C')
					#print temp_string.encode("UTF-8")
					self.file_writer.append_to_end_of_file(temp_string)
				self.truncate_temp_logs(self.log_file, self.max_lines)
			except (KeyboardInterrupt, SystemExit):
				print 'Stopping writing to temp logs now! Adding end marker to temp file'
				self.file_writer.append_to_end_of_file("---------- Temp Logging Stopped ----------\n")
				raise

	def truncate_temp_logs(self, log_file, max_lines):
		num_lines = sum(1 for line in open(log_file))
		if num_lines > max_lines:
			with open(log_file, 'r') as f_read:
				lines = f_read.readlines()
			with open(log_file, 'w') as f_overwrite:
				f_overwrite.writelines(lines[num_lines-max_lines:])

	def get_time_now(self):
		time_now = datetime.datetime.now()
		time_first = time_now.strftime("%H:%M:%S")
		time_millis = time_now.strftime(".%f")
		time_millis_rounded = round(float(time_millis), 2)
		return "{0}{1}".format(time_first, "{0:.2f}".format(time_millis_rounded)[1:])
		

class FileWriter(object):
	def __init__(self, file_path):
		self.file_path = file_path

	def append_to_end_of_file(self, text):
		with open(self.file_path, "a+") as f:
			f.write(text.encode('utf8'))


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


def main():
	loopReader = LoopTempReader()
	loopReader.loop_read()

if __name__ == "__main__":
	main()
