#!/usr/bin/python3
import lcddriver as lcd
from time import sleep
import sys
import psutil as ps
import os
import stat
import math
import signal
from datetime import datetime

lcd = lcd.lcd()

# 5 by 8 custom char creation
#https://www.quinapalus.com/hd44780udg.html

#More info here with full char set
#http://www.electronic-engineering.ch/microchip/datasheets/lcd/charset.gif

# Define some static characters
fontdata = [
		 # Char 0 - Celsius
		[ 0x8,0x14,0x8,0x3,0x4,0x4,0x4,0x3],
		# Char 1 1/5 block 
		[ 0x10,0x10,0x10,0x10,0x10,0x10,0x10,0x10],
		# Char 2 2/5 block 
		[ 0x18,0x18,0x18,0x18,0x18,0x18,0x18,0x18],
		# Char 3 3/5 block 
		[ 0x1c,0x1c,0x1c,0x1c,0x1c,0x1c,0x1c,0x1c],
		# Char 4 4/5 block 
		[ 0x1e,0x1e,0x1e,0x1e,0x1e,0x1e,0x1e,0x1e],
		# Char 5 - Arrow up
		[ 0x0,0x4,0xe,0x1f,0x4,0x4,0x4,0x0],
		# Char 6 - Arrow down
		[ 0x0,0x4,0x4,0x4,0x1f,0xe,0x4,0x0],
		# Char 7 ZZ
		[ 0x1e,0x4,0x8,0x1e,0xf,0x2,0x4,0xf],
]

lcd.load_custom_chars(fontdata)

sleep(1)

prev_rx_speed = prev_tx_speed = 0
net_if = 'enp3s0'

#change here to sda sdb sdc etc
disk1_to_check="mmcblk0p2"
#change here to partition full name for pct usage, check with "df -h"
path_disk1="/"
disk2_to_check="sdb1"
path_disk2="/media/umbynos/SAMSUNG"

#offsets 1 char to the right if the first disk starts with "nvme"
nvmeoffset = 0 if disk1_to_check[0:4]!="nvme" else 1

#check if disk exists function
def disk_exists(path):
	try:
		return stat.S_ISBLK(os.stat(path).st_mode)
	except:
		return False

# return simbol to use regarding the disks status to print on the LCD
def get_symbol_disk(path):
	if disk_exists(path)!=True:
		hddstr=chr(6)
	else:
		# read hdd state from hdparm
		hddstate=str(os.popen('hdparm -C '+path+' | grep state | cut -f 2 -d :').readline())[2:][:-1]
		hddstr = chr(7) if hddstate=="standby" else chr(5)
	return hddstr

def print_bars(row, percentage):
	for x in range(0,5):
		if (math.floor(percentage+1)>x*(100/6)) and (math.floor(percentage)>(x+1)*(100/6)) or percentage>98:
			lcd.display_string_pos(chr(255),row,9+x)
		else:
			if ((math.floor(percentage)>x*(100/6)+1) and (math.floor(percentage)<(x+1)*(100/6)) and percentage>2):
				lcd.display_string_pos(chr(min(4,math.floor((percentage-(x*100/6))/((100/6/4))+1))),row,9+x)
			else:  
				lcd.display_string_pos(" ",row,9+x)

def sigterm_handler(signal, frame):
	lcd.clear()
	lcd.display_string("     BYE! :)    ", 1)
	sleep(1)
	lcd.backlight(0)
	sys.exit()

signal.signal(signal.SIGTERM, sigterm_handler)

WAIT_TIME = 4
lcd.clear()
lcd.display_string(str.center(str(os.popen('hostname').readline())[:-1],16,' '),1)
lcd.display_string("    STARTING    ",2)
sleep(WAIT_TIME)
lcd.clear()

try:
	while (1):
		
		#CPU & RAM usage
		lcd.display_string("CPU   % "+chr(126)+"      "+chr(127),1)
		lcd.display_string("RAM   % "+chr(126)+"      "+chr(127),2)
		for x in range(WAIT_TIME):
			cpupct=ps.cpu_percent()
			rampct=ps.virtual_memory()[2]
			lcd.display_string_pos(str(math.floor(cpupct)).rjust(3),1,3)
			lcd.display_string_pos(str(math.floor(rampct)).rjust(3),2,3)
			print_bars(1,cpupct)
			print_bars(2,rampct)
			sleep(1)
		lcd.clear()

		#disk stats & net
		lcd.display_string(disk1_to_check[0:3+nvmeoffset]+"     %   " + chr(6),1)
		lcd.display_string_pos(chr(6),1,12)
		lcd.display_string(disk2_to_check[0:3]+"     %   " + chr(5),2)
		lcd.display_string_pos(str(round(prev_rx_speed)).rjust(3),1,13)
		lcd.display_string_pos(str(round(prev_tx_speed)).rjust(3),2,13)
		for x in range(WAIT_TIME):
			hddstr1=get_symbol_disk("/dev/"+disk1_to_check)
			hddstr2=get_symbol_disk("/dev/"+disk2_to_check)

			lcd.display_string_pos(hddstr1, 1,4+nvmeoffset)
			lcd.display_string_pos(hddstr2, 2,4)

			obj_Disk1 = ps.disk_usage(path_disk1)
			lcd.display_string_pos(str(round(obj_Disk1.percent)), 1,6+nvmeoffset)

			obj_Disk2 = ps.disk_usage(path_disk2)
			lcd.display_string_pos(str(round(obj_Disk2.percent)), 2,6)

			tx1 = ps.net_io_counters(pernic=True)[net_if].bytes_sent
			rx1 = ps.net_io_counters(pernic=True)[net_if].bytes_recv
			delay = 0.96
			sleep(delay)
			tx2 = ps.net_io_counters(pernic=True)[net_if].bytes_sent
			rx2 = ps.net_io_counters(pernic=True)[net_if].bytes_recv
			tx_speed = (tx2 - tx1)/1048576.0/delay
			rx_speed = (rx2 - rx1)/1048576.0/delay
  
			lcd.display_string_pos(str(round(rx_speed)).rjust(3),1,13)
			lcd.display_string_pos(str(round(tx_speed)).rjust(3),2,13)
		sleep(1) #because the delay is in the middle
		lcd.clear()
		prev_tx_speed = tx_speed
		prev_rx_speed = rx_speed

		#IP & time
		lcd.display_string("IP %s" %ps.net_if_addrs()[net_if][0].address,1)
		lcd.display_string("T                 " + chr(8),2)
		for x in range(WAIT_TIME):
			cpu_temp = ps.sensors_temperatures()['coretemp'][0].current
			lcd.display_string_pos(datetime.now().strftime("%H:%M:%S") + "  " + str(round(cpu_temp)).rjust(3) + chr(8),2,2)
			sleep(1)
		lcd.clear()
		lcd.backlight(0)

# If a keyboard interrupt occurs (ctrl + c)
except(KeyboardInterrupt):
	print("\nsystem monitor interrupted by keyboard")
	lcd.clear()
	lcd.display_string("     BYE! :)    ", 1)
	sys.exit()