def crc16_mod(buf,length):
    crc=0xFFFF
    result=[]
    for i in range(len(buf)):    
        crc ^= buf[i]
        for j in range(8):
            LSB = crc & 1
            crc = crc >> 1
            if LSB:
                crc ^= 0xA001
    crc=str(hex(crc))
    result.append(int((crc[4]+crc[5]),16))
    result.append(int((crc[2]+crc[3]),16))
                    
    return result


#a=[0x10,0x20,0x06,0x00]
#a.extend(crc16_mod(a,4))
#print crc16_mod(a,4)
#for i in range(len(a)):
#    print type(a[i])
