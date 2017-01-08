#!/usr/bin/env python
import csv
import glob
import serial
import sys
import time


# Inspired by https://github.com/jantenhove/P1-Meter-ESP8266 &
# http://stackoverflow.com/a/23695315/236610
def crc16(crc, data):
 for c in data:
   crc ^= ord(c)
   for _ in range(8):
     if crc & 0x0001:
       crc >>= 1
       crc ^= 0xA001
     else:
       crc >>= 1
 return crc

    
def checksum_valid(telegram):
 """ Cumpute checksum, taking into account newlines """
 crc_received = int("0x" + telegram[-6:-2], 16)
 crc_calculated = crc16(0x0000, telegram[:-6])
 return crc_received == crc_calculated



def store_telegram(telegram):
  """ 
  Storing the file 'readable' one-line ascii format, no compression this
  could be done an at later stage to reduce filesize. Normal month will 
  be (every 10 seconds telegram of roughly 800 bytes) ~ 200MB uncompressed.
  Compression ratio will be around 20:1.
  """

  line = telegram.encode('base64').replace('\n', '')
  csvfile = time.strftime("/home/pi/P1_DATA_%Y_%m.csv")
  with open(csvfile, "a") as output:
    data = [int(time.time()), line]
    writer = csv.writer(output, delimiter=";", lineterminator='\n')
    writer.writerow(data)
  


def get_telegram():
  with serial.Serial('/dev/ttyUSB0', 115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN) as ser:
    telegram = ''
    while True:
      s = ser.readline()
      telegram += s
      if s.startswith('!'):
	# When starting the serial connection it is between transition, since
	# the Request line is manually held high.
	if not telegram.startswith('/'):
          print >> sys.stderr, 'ERROR: Incomplete packet received (normal during startup)'
        elif not checksum_valid(telegram):
          print >> sys.stderr, 'ERROR: Invalid checksum'
        else:
          store_telegram(telegram)
        telegram = ''
	


   
if __name__ == '__main__':
  get_telegram()
