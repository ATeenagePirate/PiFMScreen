#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import PiFm
import subprocess
import os

time.sleep(30)

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

try:

	os.system("sudo python /home/pi/fm/convert.py")

	FrequencyFile = "/home/pi/fm/frequency"

	f = open (FrequencyFile,"r")

	#Read whole file into data
	temp = f.read()

	if temp == "":
		
		Frequency = 98.50
	
	else:

		Frequency = float(temp)

	# Close the file
	f.close()

	# Define GPIO to LCD mapping
	LCD_RS = 7
	LCD_E  = 8
	LCD_D4 = 25 
	LCD_D5 = 24
	LCD_D6 = 23
	LCD_D7 = 11
	UP_FREQ = 27
	DN_FREQ = 22
	NXT_SNG = 10
	SHT_DWN = 9

	# Define some device constants
	LCD_WIDTH = 16    # Maximum characters per line
	LCD_CHR = True
	LCD_CMD = False

	LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
	LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

	# Timing constants
	E_PULSE = 0.00005
	E_DELAY = 0.00005

	def shutdown(channel):
		
		# Send some centred test
		lcd_byte(LCD_LINE_1, LCD_CMD)
		lcd_string("Are you sure?",2)
		lcd_byte(LCD_LINE_2, LCD_CMD)
		lcd_string("Again = Yes",2)

		time.sleep(1.5)

		while True:

			if not GPIO.input(UP_FREQ) or not GPIO.input(DN_FREQ) or not GPIO.input(NXT_SNG):

				break


			if not GPIO.input(SHT_DWN):
		
				# Send some centred test
				lcd_byte(LCD_LINE_1, LCD_CMD)
				lcd_string("System is",2)
				lcd_byte(LCD_LINE_2, LCD_CMD)
				lcd_string("shutting down...",2)

				print "\nShutting Down Now..."
				os.system("sudo halt now")
	
	def next_song(channel):
		
		# Send some centred test
		lcd_byte(LCD_LINE_1, LCD_CMD)
		lcd_string("Skipping current",2)
		lcd_byte(LCD_LINE_2, LCD_CMD)
		lcd_string("song . . .",2)

		time.sleep(1)

		os.system("sudo pkill -2 a.out")	

	def move_frequency_up(channel):

		global Frequency

		# Send some centred test
		lcd_byte(LCD_LINE_1, LCD_CMD)
		lcd_string("Frequency up",2)
		lcd_byte(LCD_LINE_2, LCD_CMD)
		lcd_string("by 0.05 MHz",2)

		#If the UP_FREQ button is pressed, raise the frequency

		if Frequency < 108:

				Frequency = Frequency + 0.05
			
		else:
			
				Frequency = 87

		print "Frequency has been upped by .05 MHz"

		file = open(FrequencyFile, "w")
		file.write(str(Frequency))
		file.close()
		
		os.system("sudo pkill -2 a.out")

	def move_frequency_down(channel):

		global Frequency
		
		# Send some centred test
		lcd_byte(LCD_LINE_1, LCD_CMD)
		lcd_string("Frequency down",2)
		lcd_byte(LCD_LINE_2, LCD_CMD)
		lcd_string("by 0.05 MHz",2)
		
		if Frequency > 87:

				Frequency = Frequency - 0.05

		else:

				Frequency = 108

		print "Frequency has been dropped by .05 MHz"

		file = open(FrequencyFile, "w")
		file.write(str(Frequency))
		file.close()

		os.system("sudo pkill -2 a.out")

	def main():
	  # Main program block

	  GPIO.cleanup()

	  time.sleep(1)

	  GPIO.setwarnings(False)

	  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
	  GPIO.setup(LCD_E, GPIO.OUT)  # E
	  GPIO.setup(LCD_RS, GPIO.OUT) # RS
	  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
	  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
	  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
	  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

	  time.sleep(0.25)

	  GPIO.setup(UP_FREQ, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Up frequency button

	  time.sleep(0.25)

	  GPIO.setup(DN_FREQ, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Down frequency button

	  time.sleep(0.25)

	  GPIO.add_event_detect(UP_FREQ, GPIO.FALLING, callback=move_frequency_up, bouncetime=400)

	  time.sleep(0.25)

	  GPIO.add_event_detect(DN_FREQ, GPIO.FALLING, callback=move_frequency_down, bouncetime=400)

	  time.sleep(0.25)

	  GPIO.setup(NXT_SNG, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Next Song button

	  time.sleep(0.25)

	  GPIO.add_event_detect(NXT_SNG, GPIO.FALLING, callback=next_song, bouncetime=400)

	  time.sleep(0.25)

	  GPIO.setup(SHT_DWN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Shutdown button

	  time.sleep(0.25)

	  GPIO.add_event_detect(SHT_DWN, GPIO.FALLING, callback=shutdown, bouncetime=400)

	  # Initialise display
	  lcd_init()

	def lcd_init():
	  # Initialise display
	  lcd_byte(0x33,LCD_CMD)
	  lcd_byte(0x32,LCD_CMD)
	  lcd_byte(0x28,LCD_CMD)
	  lcd_byte(0x0C,LCD_CMD)  
	  lcd_byte(0x06,LCD_CMD)
	  lcd_byte(0x01,LCD_CMD)

	def lcd_string(message,style):
	  # Send string to display
	  # style=1 Left justified
	  # style=2 Centred
	  # style=3 Right justified

	  if style==1:
	    message = message.ljust(LCD_WIDTH," ")  
	  elif style==2:
	    message = message.center(LCD_WIDTH," ")
	  elif style==3:
	    message = message.rjust(LCD_WIDTH," ")

	  for i in range(LCD_WIDTH):
	    lcd_byte(ord(message[i]),LCD_CHR)

	def lcd_byte(bits, mode):
	  # Send byte to data pins
	  # bits = data
	  # mode = True  for character
	  #        False for command

	  GPIO.output(LCD_RS, mode) # RS

	  # High bits
	  GPIO.output(LCD_D4, False)
	  GPIO.output(LCD_D5, False)
	  GPIO.output(LCD_D6, False)
	  GPIO.output(LCD_D7, False)
	  if bits&0x10==0x10:
	    GPIO.output(LCD_D4, True)
	  if bits&0x20==0x20:
	    GPIO.output(LCD_D5, True)
	  if bits&0x40==0x40:
	    GPIO.output(LCD_D6, True)
	  if bits&0x80==0x80:
	    GPIO.output(LCD_D7, True)

	  # Toggle 'Enable' pin
	  time.sleep(E_DELAY)    
	  GPIO.output(LCD_E, True)  
	  time.sleep(E_PULSE)
	  GPIO.output(LCD_E, False)  
	  time.sleep(E_DELAY)      

	  # Low bits
	  GPIO.output(LCD_D4, False)
	  GPIO.output(LCD_D5, False)
	  GPIO.output(LCD_D6, False)
	  GPIO.output(LCD_D7, False)
	  if bits&0x01==0x01:
	    GPIO.output(LCD_D4, True)
	  if bits&0x02==0x02:
	    GPIO.output(LCD_D5, True)
	  if bits&0x04==0x04:
	    GPIO.output(LCD_D6, True)
	  if bits&0x08==0x08:
	    GPIO.output(LCD_D7, True)

	  # Toggle 'Enable' pin
	  time.sleep(E_DELAY)    
	  GPIO.output(LCD_E, True)  
	  time.sleep(E_PULSE)
	  GPIO.output(LCD_E, False)  
	  time.sleep(E_DELAY)

	try:
		os.system("sudo initctl stop xbmc")

	except Exception, e:
		print "Error killing XBMC: \n " + e

	main()
	
	def broadcast():

		time.sleep(0.5)

		#Virtually unlimited amount loop over files (convert them then broadcast, if already converted, just broadcast it)
		for x in range (1, 100000):
			for root, dirs, files in os.walk("/home/pi/Music/MP3/"):
				for f in files:

					MP3Path = os.path.join(root, f)
					WAVPath = "/home/pi/Music/WAV/" + f[0:(len(f) - 4)] + ".wav"			

					if MP3Path.endswith('.mp3'):

						print "\nBroadcasting %s on frequency: %0.2f MHz" % (f[0:(len(f) - 4)], Frequency), "blue"

						# Send some centred test
						lcd_byte(LCD_LINE_1, LCD_CMD)
						lcd_string("Bass In Yo Face!",2)
						lcd_byte(LCD_LINE_2, LCD_CMD)
						string = "%0.2f MHz FM" % Frequency

						lcd_string(str(string),2)

						broadcast_command = '/home/pi/fm/./a.out "%s" %0.2f 44100' % (WAVPath, Frequency)

						try:
							
							r = os.system(broadcast_command)

						except Exception, e:

							print "Error occurred: \n" + str(e)
	
	broadcast()

except Exception, e:
	# Send some centred test
	lcd_byte(LCD_LINE_1, LCD_CMD)
	lcd_string(str(e[0:16]),2)
	lcd_byte(LCD_LINE_2, LCD_CMD)
	lcd_string(str(e[16:32]),2)
	print 'Something went wrong :\n' + str(e)
	GPIO.cleanup()
	os.system("sudo pkill -15 /home/pi/fm/screen.py")