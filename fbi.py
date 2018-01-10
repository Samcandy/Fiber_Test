import serial,time
import crc16_mod

crc=crc16_mod.crc16_mod
buffer=[]
data_total=[]
wave_length={}
power_data={}
ad_data={}

#------------------------------------Command setting
read_SN = [0x10,0x03,0x06,0x00]
read_SN.extend(crc(read_SN,len(read_SN)))

set_scan = [0x10,0x04,0x06,0x01]
set_scan.extend(crc(set_scan,len(set_scan)))

scan = [0x10,0x20,0x06,0x00]
scan.extend(crc(scan,len(scan)))

read_wave = [0x10,0x01,0x06,0x02]    #read ch2 wavelength
read_wave.extend(crc(read_wave,len(read_wave)))

read_peak = [0x10,0x02,0x06,0x02]    #read ch2 peak
read_peak.extend(crc(read_peak,len(read_peak)))

read_ad = [0x10,0x05,0x06,0x02]    #read ch2 AD Data
read_ad.extend(crc(read_ad,len(read_ad)))

#------------------------------------Serial port setting
fbi=serial.Serial("/dev/ttyUSB0", 115200, timeout=0.5)
lora=serial.Serial("/dev/ttyUSB1", 115200, timeout=0.5)

#lora.parity=serial.PARITY_NONE
#fbi.parity=serial.PARITY_NONE

print "lora port: "+lora.name
print "FBI port: "+fbi.name

#------------------------------------Read SN
print "Serial Send: ",read_SN  
fbi.write(serial.to_bytes(read_SN))

data = fbi.readline()
data = [ord(x) for x in data]
print "Serial Response: ",data

buffer=data[3:7]
SN = buffer[0]*256*256*256 + buffer[1]*256*256 + buffer[2]*256 +buffer[3]
print "SN: ",SN
#------------------------------------Set scan
print "Serial Send: ",set_scan
fbi.write(serial.to_bytes(set_scan))

data= fbi.readline()
data = [ord(x) for x in data]
print "Serial Response: ",data
#------------------------------------Scan
print "Serial Send: ",scan
fbi.write(serial.to_bytes(scan))
while 1:
    data= fbi.readline()
    data = [ord(x) for x in data]
    print "Serial Response: ",data
    if len(data) >0:
        break
    time.sleep(1)
if data[3]==1:
    print '\033[1;32mScanning Success\033[1;m'
else:
    print '\033[1;31mScanning Fail\033[1;m'
    
#------------------------------------Read Channel Wavelength
print "Serial Send(Wavelength): ",read_wave
fbi.write(serial.to_bytes(read_wave))
while 1:
    data= fbi.readline()
    data = [ord(x) for x in data]
    print data
    data_total.extend(data)
    if len(data)==0:
        break
print '\033[1;34mdata Total: \033[1;m',data_total
for i in range(len(data_total)):
    if i % 4 == 0:
        number = data_total[i]
        wave = float(data_total[i+1]*256*256 + data_total[i+2]*256 + data_total[i+3])/10000
        wave_length.update({number:wave})
        number,wave=0,0
    if i  == 120:
        break    
print '\033[1;33mWave_length: \033[1;m',wave_length
data_total=[]
time.sleep(1)

#------------------------------------Read Channel Peak
print "Serial Send(Peak): ",read_peak
fbi.write(serial.to_bytes(read_peak))
while 1:
    data= fbi.readline()
    data = [ord(x) for x in data]
    print data
    data_total.extend(data)
    if len(data)==0:
        break

print '\033[1;34mdata Total: \033[1;m',data_total
for i in range(len(data_total)):
    if i % 4 == 0:
        number = data_total[i]
        power = float(data_total[i+1]*256*256 + data_total[i+2]*256 + data_total[i+3])/10
        power_data.update({number:power})
        number,power=0,0
    if i  == 120:
        break    
print '\033[1;33mPower: \033[1;m',power_data
data_total=[]
time.sleep(1)

#------------------------------------Read Channel AD Data
print "Serial Send(AD): ",read_ad
fbi.write(serial.to_bytes(read_ad))
while 1:
    data= fbi.readline()
    data = [ord(x) for x in data]
    print data
    data_total.extend(data)
    if len(data) == 0:
        break
print '\033[1;34mdata Total: \033[1;m',data_total
print '\033[1;34mdata Length: \033[1;m',len(data_total)

# unit GHz
start_freq= data_total[5]*256*256 + data_total[6]*256 + data_total[7]
step=data_total[8]
for i in range(9):
    data_total.pop(0)

# pop CRC
data_total.pop()
data_total.pop()
while len(data_total) !=0:
    data = data_total.pop()
    data = data + data_total.pop()*256
    ad_data.update({ (len(data_total)/2)+1 :data})
    
print ad_data
data_total=[]
time.sleep(3)

#------------------------------------Lora Setting
lora.write("p2p set_freq 916000000\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p set_pwr 14\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p set_sf 7\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p set_bw 125\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p set_cr 4/6\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p set_sync 34\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)

lora.write("p2p save\r")
while 1:
    data=lora.readline()
    print data
    if len(data) == 7:
        break
    time.sleep(1)
print
time.sleep(2)
#------------------------------------Lora Send

#buffer = [str(x) for x in buffer]
while 1:
    print "Lora send: ",SN
    lora.write("p2p tx "+str(SN)+"\r")
    time.sleep(0.1)
#lora.write("\r")
    while 1:
        data=lora.readline()
        print data
        if len(data) == 7:
            break
        time.sleep(1)
    time.sleep(2)
