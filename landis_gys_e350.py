import sys
import serial



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


def parse_telegram(telegram):
  pass


with serial.Serial('/dev/ttyUSB0', 115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN) as ser:
  telegram = ''
  while True:
    s = ser.readline()
    print s,

    telegram += s
    if s.startswith('!'):
      if checksum_valid(telegram):
        parse_telegram(telegram)
      else:
        print >> sys.stderr, 'ERROR: Invalid checksum'
      telegram = ''
	


   
