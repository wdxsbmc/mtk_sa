import os
# pip3 install pyserial
import serial
from serial import *
import time


class com():

    message = []

    def __init__(self):
        '''
           init serial, send recive data
        '''
        self.message = []

    def init_com(self, com_port):
        # 创建一个com_com
        self.com_port = com_port
        try:
            self.ser = serial.Serial(
                port=self.com_port,
                baudrate=115200,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS)
        except IOError:
            return 0
        else:
            if not self.ser.isOpen():
                self.ser.open()
        return 1

    def init_com(self, com_port, com_baudrate, com_stopbits, com_bytesize):
        # 创建一个com_com
        self.com_port = com_port
        self.com_baudrate = com_baudrate
        self.com_stopbits = com_stopbits
        self.com_bytesize = com_bytesize
        try:
            self.ser = serial.Serial(
                port=self.com_port,
                baudrate=self.com_baudrate,
                stopbits=self.com_stopbits,
                bytesize=self.com_bytesize)
        except IOError:
            return 0
        else:
            if not self.ser.isOpen():
                self.ser.open()
        return 1

    def port_is_open(self):
        return self.ser.isOpen()

    def port_open(self):
        if not self.ser.isOpen():
            self.ser.open()

    def port_close(self):
        self.ser.close()

    def send_data(self, data):
        number = self.ser.write(data)
        return number

    def read_data(self):
        n = self.ser.inWaiting()
        if (n > 0):
            data = self.ser.read(n)
            self.message.extend(data)

    '''
        68H	Addr	SubAddr	07H	07H	CUR_MOD	Freq	TotalS	CS	16H
    test:  FE FE FE FE 68 01 01 07 07 00 E8 03 05 00 00 00 68 16
    '''

    def make_packet(self, board_num, board_port, ctl_code, data_len, data):

        checksum = 0
        pkt = []

        # head
        pkt.append(0xFE)
        pkt.append(0xFE)
        pkt.append(0xFE)
        pkt.append(0xFE)
        pkt.append(0x68)
        pkt.append(int(board_num))
        pkt.append(int(board_port))
        pkt.append(ctl_code)
        pkt.append(data_len)

        # data
        pkt.extend(data)

        # udpate checksum
        if (len(pkt) > 0):
            for i in range(4, len(pkt)):
                checksum = checksum + int(pkt[i])

        pkt.append(checksum % 256)
        pkt.append(0x16)
        return pkt

    def cmd_send(self, board_num, board_port, ctl_code, data_len, data,
                 exp_code):

        if (self.ser.is_open):
            cmd = self.make_packet(board_num, board_port, ctl_code, data_len,
                                   data)
            #   FE FE FE FE 68 01 01 07 07 00 E8 03 05 00 00 00 68 16
            print(cmd)

            self.send_data(cmd)
        return 1

    def cmd_send_recv(self, board_num, board_port, ctl_code, data_len, data,
                      exp_code):

        if (self.ser.is_open):

            cmd = self.make_packet(board_num, board_port, ctl_code, data_len,
                                   data)

            #   FE FE FE FE 68 01 01 07 07 00 E8 03 05 00 00 00 68 16
            print(cmd)

            self.send_data(cmd)

            time.sleep(1)

            self.read_data()

            recv_data = self.message[0:11]

            barr = bytearray(recv_data)

            if (barr.count == 0):
                return 0
            if (barr[7] == exp_code):
                return 1
            else:
                return 0

    def send_recv_data(self, cmd):

        if (self.ser.is_open):
            
            send_barr = bytearray(cmd)

            self.send_data(cmd)

            time.sleep(1)

            self.read_data()

            recv_data = self.message

            barr = bytearray(recv_data)

            if (barr.count == 0):
                return 0
            if (barr[0] == send_barr[0]):
                # check tag
                return 1
            else:
                return 0


    # 转成16进制的函数
    def convert_hex(self, string):
        res = []
        result = []
        for item in string:
            res.append(item)
        for i in res:
            result.append(hex(i))
        return result