import os
from subprocess import Popen, PIPE, call
from argparse import ArgumentParser
from time import sleep
from sensor_installer import SensorInstaller

class OldTempReader(object):
	def get_average_temp(self):
    	# Replace 28-000003ae0350 with the address of your DS18B20
    	pipe = Popen(["cat","/sys/bus/w1/devices/w1_bus_master1/28-000003ea0350/w1_slave"], stdout=PIPE)
    	result = pipe.communicate()[0]
    	result_list = result.split("=")
    	temp_mC = int(result_list[-1]) # temp in milliCelcius
    	return temp_mC


class RemoteTransmitter(object):
	def turn_on(self):
  		os.system("sudo ./strogonanoff_sender.py --channel 1 --button 1 --gpio 0 on")

	def turn_off(self):
  		os.system("sudo ./strogonanoff_sender.py --channel 1 --button 1 --gpio 0 off") 


class SousVide(object):
	def __init__(self, args):	
		self.target = args.target * 1000
		print ('Target temp is %d' % (args.target))
		self.P = args.prop
		self.I = args.integral
		self.B = args.bias
		# Initialise some variables for the control loop
		self.interror = 0
		self.pwr_cnt=1 #unused currently, why?
		self.pwr_tot=0 #unused currently, why?

		# Setup 1Wire for DS18B20
		sensor_installer = SensorInstaller()
		sensor_installer.setup_sensors()

		self.heat_source = RemoteTransmitter()

	def run(self):
		# Turn on for initial ramp up
		state="on"
		self.heat_source.turn_on()
		
		sensors = SensorRepository()
		temp_reader = TempReader(sensors)

		temperature = temp_reader.get_average_temp()
		print("Initial temperature ramp up")
		while (self.target - temperature > 6000):
			sleep(15)
		temperature = temp_reader.get_average_temp()
		print(temperature)

		print("Entering control loop")
		while True:
			temperature=temp_reader.get_average_temp()
			print(temperature)
			error = self.target - temperature
			self.interror = self.interror + error
			power = self.B + ((self.P * error) + ((self.I * self.interror)/100))/100
			print power
			# Make sure that if power should be off then it is
			if (state=="off"):
				self.heat_source.turn_off()
			# Long duration pulse width modulation
			for x in range (1, 100):
				if (power > x):
					if (state=="off"):
						state="on"
						print("Turning on the heat!")
						self.heat_source.turn_on()
				else:
					if (state=="on"):
						state="off"
						print("Turning off the heat!")
						self.heat_source.turn_off()
				sleep(1)


class SousVideArgParser(object):
	def __init__(self):
		#Get command line args
		self.parser = ArgumentParser()
		self.parser.add_argument("-t", "--target", type=int, default=55)
		self.parser.add_argument("-p", "--prop", type=int, default=6)
		self.parser.add_argument("-i", "--integral", type=int, default=2)
		self.parser.add_argument("-b", "--bias", type=int, default=22)
	
	def parse_args(self):
		return self.parser.parse_args()


def main():
	arg_parser = SousVideArgParser()
	args = arg_parser.parse_args()
	SousVide(args)


if __name__ == "__main__":
	main()
