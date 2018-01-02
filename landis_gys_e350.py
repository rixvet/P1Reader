#!/usr/bin/env python
import csv
import glob
import re
import serial
import sys
import time
import argparse

from collections import defaultdict

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
  


def get_telegram(port):
  with serial.Serial(port, 115200, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN) as ser:
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


def parse_telegram(csvfile, bucket_size):
  prev_gas_m3 = None
  bucket = defaultdict(float)

  with open(csvfile, "r") as fh:
    reader = csv.reader(fh, delimiter=';', lineterminator='\n')
    for row in reader:
        time_str, telegram_str = row
        time = int(time_str)
        telegram = telegram_str.decode('base64')
        for line in telegram.split():
            if line.startswith('0-1:24.2.1'):
                m = re.match('^[\d\-\:\.]+\(\d+W\)\((\d+\.\d+)\*m3\)$', line)
                gas_m3=float(m.group(1))

        if prev_gas_m3:
            # If delta is more than X days, assume broken sensor and devide
            # amount equally over all buckets
            delta_m3 = gas_m3 - prev_gas_m3
            if (time - prev_time) > (3600 * 24 * 2):
                bk = range(prev_time, time, bucket_size)
                for k in bk:
                    bucket[k - (k % bucket_size)] += (delta_m3 / len(bk))
            else:
                bucket[time - (time % bucket_size)] += delta_m3
        # Store previous values
        prev_gas_m3 = gas_m3
        prev_time = time

    # Display values
    for k,v in sorted(bucket.items()):
        print k,v

	


   
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--bucket_size', type=int, default=3600)
  parser.add_argument('action')
  parser.add_argument('files', nargs='+')
  args = parser.parse_args()

  if args.action == 'parse':
    for fn in args.files:
        parse_telegram(fn, args.bucket_size)
  elif args.action == 'get':
    get_telegram(sys.files[0])
