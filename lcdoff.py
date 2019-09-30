import lcddriver as lcd
lcd.clear()
lcd.display_string("     BYE! :)    ", 1)
sleep(1)
lcd.backlight(0)
sys.exit()