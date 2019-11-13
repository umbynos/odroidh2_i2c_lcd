#!/usr/bin/python3
import lcddriver as lcd
from time import sleep
import sys

lcd = lcd.lcd()
lcd.clear()
lcd.display_string("     BYE! :)    ", 1)
sleep(1)
lcd.backlight(0)
sys.exit()