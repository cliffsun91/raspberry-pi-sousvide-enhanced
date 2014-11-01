#!/bin/sh

case "$1" in
  start)
    python /home/pi/projects/RPi_sousvide/temp_reader.py & > /dev/null
	python /home/pi/projects/RPi_sousvide/sousvideserver.py & > /dev/null 
    ;;
  stop)
	sudo kill -9 `pgrep -f 'python .*sousvideserver.py'`
    sudo kill -TERM `pgrep -f 'python .*temp_reader.py'`
    ;;
  *)
    echo "Usage: /temp_monitor.sh {start|stop}"
    exit 1
    ;;
esac

exit 0

