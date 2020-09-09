import serial
import binascii
from time import sleep
import os 
import sys
import time

print ("set your com:")
#com_set = raw_input()
com_set = input()
select = '1'
#BAUD = '57600'
BAUD = '115200'
baud = int(BAUD)
file_name = 'rtk_status.bin'
file = open(file_name,"wb")



#binfile = open("rtk.bin", 'rb')
#size = os.path.getsize("rtk.bin") 
print ("set your file:")
#bin_file = input()
bin_file = 'firmware.bin'
binfile = open(bin_file, 'rb')
size = os.path.getsize(bin_file) 
all_bytes_len = size
fs_len = size
boot_mode = 0
print ("size:%d" % size)
serial = serial.Serial(com_set, baud, timeout=0.1)  #/dev/ttyUSB0

def calc_crc(payload):
	'''Calculates CRC per 380 manual
	'''
	crc = 0x1D0F
	for bytedata in payload:
		crc = crc^(bytedata << 8) 
		for i in range(0,8):
			if crc&0x8000:
				crc = (crc << 1)^0x1021
			else:
				crc = crc << 1

	crc = crc & 0xffff
	return crc

def start_bootloader():
	'''Starts bootloader
		:returns:
			True if bootloader mode entered, False if failed
	'''
	print ("start")
	C = [0x55, 0x55, ord('J'), ord('I'), 0x00 ]
	crc = calc_crc(C[2:4] + [0x00])    # for some reason must add a payload byte to get correct CRC
	crc_msb = (crc & 0xFF00) >> 8
	crc_lsb = (crc & 0x00FF)
	C.insert(len(C), crc_msb)
	C.insert(len(C), crc_lsb)
	serial.write([0x01,0x02])
	sleep(2)
	serial.write(C)
	print (C)
	time.sleep(2)   # must wait for boot loader to be ready
	R = serial.read(5)
	print(R)
	if R[0] == 85 and R[1] == 85:
		#packet_type =  '{0:1c}'.format(R[2]) + '{0:1c}'.format(R[3])
		packet_type = R[2] + R[3]
		if packet_type == 'JI':
			serial.read(R[4]+2)
			print('bootloader ready')
			time.sleep(2)
			if boot_mode == 0:
				print('resync with device')
				time.sleep(2)
			return True
		else: 
			return False
	else:
		return False



def start_app():
	'''Starts app
	'''
	C = [0x55, 0x55, ord('J'), ord('A'), 0x00 ]
	crc = calc_crc(C[2:4] + [0x00])    # for some reason must add a payload byte to get correct CRC
	crc_msb = (crc & 0xFF00) >> 8
	crc_lsb = (crc & 0x00FF)
	C.insert(len(C), crc_msb)
	C.insert(len(C), crc_lsb)
	serial.write(C)
	sleep(2)
	print (C)
	R = serial.read_all()   #7
	'''
	if (R[0]) == 85 and (R[1]) == 85:
		packet_type =  R[2] + R[3]
		print(packet_type)
	'''
	if R[0] == 85 and R[1] == 85:
		packet_type = '{0:1c}'.format(R[2]) + '{0:1c}'.format(R[3])
		print(packet_type)

def write_block(buf, data_len, addr):
	'''Executed WA command to write a block of new app code into memory
	'''
	print(data_len, addr)
	C = [0x55, 0x55, ord('W'), ord('A'), data_len+5]
	addr_3 = (addr & 0xFF000000) >> 24
	addr_2 = (addr & 0x00FF0000) >> 16
	addr_1 = (addr & 0x0000FF00) >> 8
	addr_0 = (addr & 0x000000FF)
	C.insert(len(C), addr_3)
	C.insert(len(C), addr_2)
	C.insert(len(C), addr_1)
	C.insert(len(C), addr_0)
	C.insert(len(C), data_len)
	for i in range(data_len):
		#C.insert(len(C), ord(buf[i]))
		C.insert(len(C), buf[i])
	crc = calc_crc(C[2:C[4]+5])  
	crc_msb = int((crc & 0xFF00) >> 8)
	crc_lsb = int((crc & 0x00FF))
	C.insert(len(C), crc_msb)
	C.insert(len(C), crc_lsb)
	status = 0
	while (status == 0):
		serial.write(C)
		test = []
		for ele in C:
			test.insert(len(test),hex(ele))
		#print test
		#print len(C)
		#print('percent: {:.2%}'.format(addr/fs_len))
		print ("upload progress: %.3f%%" % (float(addr)/float(fs_len)*100))
		if addr == 0:
		   sleep(8)
		else:
		   #sleep(0.01)
		   sleep(0.05)
		print('wait')
		#input()
		R = serial.read(12)  #longer response
		response=[]
		for ele in bytearray(R):
			response.append(ele)
		print(response)
		#test = ord(R[0])
		status = 1
		#print R[2]
		#print R[3]
		if len(R) > 1 and (R[0]) == 85 and (R[1]) == 85:
			#packet_type =  '{0:1c}'.format(R[2]) + '{0:1c}'.format(R[3])
			#packet_type = R[2] + R[3]
			#print(packet_type)
			packet_type = '{0:1c}'.format(
				R[2]) + '{0:1c}'.format(R[3])
			if packet_type == 'WA':
				status = 1
			else:
				sys.exit()
				print('retry 1')
				status = 0
		else:
			print(len(R))
			print(R)
			#self.reset_buffer()
			sleep(1)
			print('no packet')
			sys.exit()
		


def recv(serial):
	while True:
		if select == "2":
			data = binascii.b2a_hex(serial.read_all())
			file.write(data)
			#data = serial.read_all()
			#data = "test"
		else:
			#data = binascii.b2a_hex(serial.read_all())
			data = serial.read_all()
			file.write(data)
		'''
		if data == '':
			continue
		else:
			break
		'''
		#sleep(0.02)
	return data

write_flag = 1
send_count = 0
max_data_len = 200
write_len = 0
#start_app()
if __name__ == '__main__':

	if serial.isOpen() :
		print("open success")
		start_time = time.time()
	else :
		print("open failed")
	sleep(1)
	start_bootloader()
	sleep(8)
	while True:
		sleep(1)
		print('wait')
	serial.baud = 115200
	while (write_len < fs_len):
		data_to_write = binfile.read(max_data_len)
		#packet_data_len = max_data_len 
		if (fs_len - write_len) > max_data_len:
			packet_data_len = max_data_len 
		else:
			packet_data_len = fs_len - write_len
		write_block(data_to_write,packet_data_len, write_len)
		write_len += packet_data_len
	print ("upload progress: %.3f%%" % 100)
	end_time = time.time()
	print ("upload use time: %.2fs" % (end_time - start_time))
	print ("start app")
	sleep(5)
	start_app()
		#test = raw_input()
	'''
	while write_flag > 0:
		data_to_write = binfile.read(100)
		serial.write(data_to_write)
		all_bytes_len -= 100
		send_count += 100
		if(all_bytes_len) < 100:
			data_to_write = binfile.read(all_bytes_len - 1)
			sleep(0.08)
			serial.write(data_to_write)
			write_flag = 0
			print send_count
			break
		sleep(0.08)
	'''
	print ('end')
		#serial.write(data) 