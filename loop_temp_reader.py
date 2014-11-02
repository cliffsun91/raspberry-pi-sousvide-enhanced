import os, glob, sys
from time import sleep
import datetime
import sys
from temp_reader import SensorRepository, TempReader 

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
				avg_temp = reader.get_average_temp()
				time = self.get_time_now()
				index = 0
				for temp in temps:
					index += 1
					temp_string = u"Sensor {0} - time: {1} | temp: {2}{3}\n".\
										format(index, time, str(temp), u"\u00b0"+'C')
					#print temp_string.encode("UTF-8")
					self.file_writer.append_to_end_of_file(temp_string)
					avg_temp_string = u"\t({0}) Average temp: {1}{2}\n".format(time, str(avg_temp), u"\u00b0"+'C')
					self.file_writer.append_to_end_of_file(avg_temp_string)
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


def main():
	loopReader = LoopTempReader()
	loopReader.loop_read()

if __name__ == "__main__":
	main()
