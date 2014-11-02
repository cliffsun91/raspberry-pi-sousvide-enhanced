import os


class SensorInstaller(object):
	def setup_sensors(self):
  		os.system("sudo modprobe w1-gpio && sudo modprobe w1-therm")


