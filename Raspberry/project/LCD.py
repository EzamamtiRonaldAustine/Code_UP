from RPLCD. i2c import CharLCD
import time

# Using I2C address 0x27
lcd = CharLCD('PCF8574', 0x27)

lcd.clear ()
lcd.write string ("Smart Fish Pond")
time. sleep (2)

lcd.clear ()
lcd.write string ("LCD Working OK!")
time.sleep (2)