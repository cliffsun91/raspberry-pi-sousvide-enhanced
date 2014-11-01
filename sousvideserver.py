import cherrypy
import os.path
from cherrypy.process.plugins import Daemonizer


class SousVideServer(object):
	def __init__(self, log_file):
		self.logs = SousVideTempLogResource(log_file)

	@cherrypy.expose
	def index(self):
		return """
			<html>
				<head>
					<h2>This is the root of the Sous Vide server</h2>
				</head>
				<body>
					<ul>
						<li><a href=\"/logs\">see the temp logs here</a></li>
					</ul>
				</body>
			</html>"""


class SousVideTempLogResource(object):
	def __init__(self, log_file):
		self.log_file = log_file

	@cherrypy.expose
	def index(self):
		if os.path.isfile(self.log_file):
			with open(self.log_file) as file:
				return self.__temp_log_html_template(file.readlines())
		else:
			return "No temp logs to show at the moment, please run the sous vide application..."

	def __temp_log_html_template(self, content):
		return """ 
				<html>
					<head>
						<h2>Sous Vide Temp Logs</h2>
					</head>
					<body>
						{content}
					<body>			
				</html>""".format(content="<br />".join(content))	

if __name__ == '__main__':
	Daemonizer(cherrypy.engine).subscribe()
	cherrypy.config.update({'server.socket_host': '0.0.0.0',
							'server.socket_port': 8181,
							'environment': 'embedded'})
	cherrypy.quickstart(SousVideServer("/home/pi/projects/RPi_sousvide/temps.log"))
