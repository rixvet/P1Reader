# P1Reader
My Utility Infrastructure provider [Liander](http://liander.nl) provided me
with a Smart Meter for gas and electricity, namely a Landis + Gys E350. The
meter is equiped with an TTL Serial port (5V), which output values at the
rather odd `115200 7E1`. (SEVENBITS, EVEN parity, 1 STOPBIT). There is no
hardware-flow support et al on the device.

I have connected this to an FTDI TTL BUB, and said to invert the RxD signal
using the Windows [FT\_PROG](http://www.ftdichip.com/Support/Utilities.htm)
utility. It linux alternative is found in as [ftdi\_eeprom](http://developer.intra2net.com/git/?p=libftdi;a=tree;f=ftdi_eeprom), yet requires some more love to be usable.

The connector being used is a standard RJ12 connector, since Pin 1 & pin 6 are
not being used an RJ11 connector fits nicely and does the job. 

Connector layout as seen from the RJ11 connector:
FTDI TTL | RJ11 connector
---------|----------------
5V       | Pin 1 (Request)
Gnd      | Pin 2 (Gnd)
N/C      | Pin 3 (N/C)
RxD      | Pin 4 (RxD)

The RxD line has to be (pulled down) to 0V by default, else you will get an
rather odd reading. This is best to be tested by measuring with your voltage
meter between the Gnd and the RxD output, this should be 0V. For my FTDI TTL
BUB I had to solder the RxD & TxD together to make this work.


I like to parse this details, to gain up2date insights on my usage, so I build
this Dutch Smart Meter (gas/electric/water) utility reader/processing.

Values received are parsed using the document sourced from "DSMR v4.2.2 Final P1.pdf" found at [Netbeheer Nederland](http://www.netbeheernederland.nl/themas/hotspot/hotspot-documenten/?dossierid=11010056&title=Slimme%20meter&onderdeel=Documenten&pageindex=2)

Since I do not own the equipment, firmware is likely to change without notice.
A library would be better suited in the feature.


Valuefmt| Format/Example        | Meaning
--------|-----------------------|-------------------------------------------------------------------
Sn      | S6 - CCCCCC           | Alphanumeric string
TST     | YYMMDDhhmmssX         | ASCII presentation of Time stamp with Year, Month, 
        |                       | Day, Hour, Minute, Second, and an 
        |                       | indication whether DST is active (X=S) or DST is not active (X=W).
In      | I4 - YYYY             | Integer number
Fn(x,y) | F7(0,3) – YYYY.YYY or | Floating decimal number with a variable
        | YYYYY.YY or YYYYYY.Y  | number of decimals behind the decimal
        | or YYYYYYY            | point (with a maximum of 3)
Fn(x,y) | F7(0,3) – YYYY.YYY    | Floating decimal number with a fixed number of decimals 
        |                       | behind the decimal point (in this case 3)


Example output
==============
```
/XMX5LGBBFG1009020270 => Header information (Manufacturer specific)

1-3:0.2.8(42)	=> Version information for P1 output (S2 tag 9)
0-0:1.0.0(170108161117W) => Date-time stamp of the P1 message (TST)
0-0:96.1.1(4530303331303033303031363939353135) => Equipment identifier (Sn n=0..96, tag 9)
1-0:1.8.1(002074.843*kWh) => Meter Reading electricity delivered to client Tariff 1) in 0,001 kWh 
1-0:1.8.2(000881.383*kWh) => Meter Reading electricity delivered to client Tariff 2) in 0,001 kWh 
1-0:2.8.1(000010.981*kWh) => Meter Reading electricity delivered by client (Tariff 1) in 0,001 kWh 
1-0:2.8.2(000028.031*kWh) => Meter Reading electricity delivered by client (Tariff 2) in 0,001 kWh 
0-0:96.14.0(0001) => Tariff indicator electricity. (S4, tag 9)
1-0:1.7.0(00.484*kW) => Actual electricity power delivered (+P) in 1 Watt resolution 
1-0:2.7.0(00.000*kW) => Actual electricity power received (-P) in 1 Watt resolution 
0-0:96.7.21(00004) => Number of power failures in any phase
0-0:96.7.9(00003) => Number of long power failures in any phase
1-0:99.97.0(3)(0-0:96.7.19)(160315184219W)(0000000310*s)(160207164837W)(0000000981*s)(151118085623W)(0000502496*s) => 
Power Failure Event Log (long power failures) (timestamp)(duration)
1-0:32.32.0(00000) => Number of voltage sags in phase L1 
1-0:32.36.0(00000) => Number of voltage swells in phase L1
0-0:96.13.1() => Text message co-des: numeric 8 digits 
0-0:96.13.0() => Text message max 1024 characters. 
1-0:31.7.0(002*A) => Instantaneous current L1 in A resolution.
1-0:21.7.0(00.484*kW) => Instantaneous active power L1 (+P) in W resolution
1-0:22.7.0(00.000*kW) => Instantaneous active power L1 (-P) in W resolution
0-1:24.1.0(003) => Device-Type (attached M-bus)
0-1:96.1.0(4730303139333430323231313938343135) => Equipment identifier
0-1:24.2.1(170108160000W)(01234.000*m3) => Last hourly Meter reading and capture time (e.g. slave E meter) 
!85F6
```


CRC Calculation
===============
CRC is a CRC16 value calculated over the preceding characters in the data
message (from “/” to “!” using the polynomial: `x**16 +x**15 +x**2 +1`). CRC16
uses no XOR in, no XOR out and is computed with least significant bit first.
The value is represented as 4 hexadecimal characters (MSB first).



Storage
=======
Since most of the values are static, I use compression in the storage to keep
it as small as possible. I like to keep the raw values for future use, since
you will never know when they will be handy.



# License
```
Copyright 2017 Rick van der Zwet <info@rickvanderzwet.nl>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
