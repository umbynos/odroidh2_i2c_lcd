#!/bin/bash

for BUS in 1 2 3 4 5 6
do
	if [[ $(i2cdetect -y -r $BUS | grep 27) ]]; then
		sed -i -e "s/BUS = \w/BUS = $BUS/g" /home/odroidlcd/lcddriver.py
	fi
done

/usr/bin/python3 /home/odroidlcd/sys_monitor_lcd.py
