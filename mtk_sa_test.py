# -*- coding:utf-8 -*-
import tkinter
from tkinter import *
import com
from com import *
import time
import _thread
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import configparser
from sa_logger import sa_logger
import binascii

test_run = 0

root = tkinter.Tk()


btn_name = locals()
status_name = locals()
global test_items
test_items = 0

root.title("MTK SA TestV1.0.1")
listbox = Listbox(root,width=80)
scr3 = Scrollbar(root)
listbox.configure(yscrollcommand = scr3.set)
scr3['command']=listbox.yview

SERIAL = com()
result_data = []

SA_CONFIG_INI_PATH= ".\sa_config.ini"

LOG_FILE = ".\sa_log.log"
LOG = sa_logger(logname=LOG_FILE, loglevel=1, logger="SA").getlog()


# centrer
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2,
                            (screenheight - height) / 2)
    #print(size)
    root.geometry(size)


def parse_data(msg):
    len  = 0
    ret_str =""
    if(msg[1]&0x80 == 0x80):
        # more bytes len
        if(msg[1]&0x7F == 1):
            len = msg[2]
            data = msg[2:len]        
        elif(msg[1]&0x7F == 2):
            len = (msg[2]<<8)&0xFF00 + (msg[3]&0xFF);
            data = msg[3:len]        
        elif(msg[1]&0x7F == 3):
            len = (msg[2]<<16)&0xFFFF00 + (msg[3]<<8)&0xFF00 + msg[4]&0xFF;
            data = msg[4:len]        
    else:
        # one byte len
        len = msg[1]&0xFF
        data = msg[2:len+2]       
   

    if(msg[0]==1):
        data_array = bytearray(data)
        ret_str = data_array.decode('utf-8')
    else:
        if(int(msg[2]) == 0):
            ret_str = "NG"
        elif(int(msg[2])== 1):
            ret_str = "OK"
                              
    return ret_str

# send recv data thread
def send_recv_data_thd(SERIAL, item_idx, data):

    #disabled all button
    global test_items
    for n in range(1,test_items+1):
        btn_name['btn%s'%n].config(state="disabled")

    if (SERIAL.port_is_open()):
        
        status_name['status%s'%item_idx].delete(0,END)
        status_name['status%s'%item_idx].insert(10, "NA")
        
        SERIAL.message.clear()   
        # send log
        log_str="send>>>" + str(binascii.b2a_hex(bytearray(data)))
        LOG.info(log_str)
        listbox.insert(END,log_str)
        listbox.yview_moveto(1.0)

        # send and recv
        SERIAL.send_recv_data(data)
        # recv log
        log_str="recv<<<" + str(binascii.b2a_hex(bytearray(SERIAL.message)))
        LOG.info(log_str)
        listbox.insert(END,log_str)
        listbox.select_set(END,END) 
        listbox.yview_moveto(1.0)
        scr3.set(1,1)

        # parse pkt
        parse_msg = SERIAL.message
        str_info = parse_data(parse_msg)
        #show result
        status_name['status%s'%item_idx].delete(0,END)
        status_name['status%s'%item_idx].insert(10, str_info)
    else:
        print("com open fail!")   
        listbox.insert(END,"com open fail!")

    # enable all buttons
    for n in range(1,test_items+1):
        btn_name['btn%s'%n].config(state="normal")

# button action
def button_1_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = int(sys._getframe().f_code.co_name[7:8])
    

    # send data
    data = []
    # tag
    data.append(0x01)
    # len
    data.append(0x01)
    # data
    data.append(0x00)

    # thread
    _thread.start_new_thread(send_recv_data_thd, (SERIAL, item_idx ,data))  
    pass

def button_2_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = int(sys._getframe().f_code.co_name[7:8])
    btn_name['btn%s'%item_idx].config(state="disabled")

    # send data
    data = []
    # tag
    data.append(0x02)
    # len
    data.append(0x01)
    # data
    data.append(0x00)

    # thread
    _thread.start_new_thread(send_recv_data_thd, (SERIAL, item_idx ,data))  
    pass

def button_3_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = int(sys._getframe().f_code.co_name[7:8])
    btn_name['btn%s'%item_idx].config(state="disabled")

    # send data
    data = []
    # tag
    data.append(0x03)
    # len
    data.append(0x01)
    # data
    data.append(0x00)

    # thread
    _thread.start_new_thread(send_recv_data_thd, (SERIAL, item_idx ,data))  

pass

def button_4_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = int(sys._getframe().f_code.co_name[7:8])
    btn_name['btn%s'%item_idx].config(state="disabled")

    # send data
    data = []
    # tag
    data.append(0x04)
    # len
    data.append(0x01)
    # data
    data.append(0x00)

    # thread
    _thread.start_new_thread(send_recv_data_thd, (SERIAL, item_idx ,data))  
    pass

def button_5_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = int(sys._getframe().f_code.co_name[7:8])
    btn_name['btn%s'%item_idx].config(state="disabled")

    # send data
    data = []
    # tag
    data.append(0x05)
    # len
    data.append(0x01)
    # data
    data.append(0x00)

    # thread
    _thread.start_new_thread(send_recv_data_thd, (SERIAL, item_idx ,data))  
    pass


# create widget list
def init_form_by_config():

    cf=configparser.ConfigParser()
    cf.read(".\sa_config.ini", encoding='UTF-8')
    if not cf:
        print('sa_config.ini open fail!')
        LOG.info('sa_config.ini open fail!')
        #TODO: alert
        return False

    sec = []
    option= []
    item = []
    sec = cf.sections()                           
    #option = cf.options('comconf')             
    #item = cf.items('comconf')                 
    #value=cf.get('comconf','com_num')       
    #cf.type(value)                          
    print(sec)
    grid_column = 0
    grid_row = 0
    item_idx = 1
    global test_items
    test_items = 0
    for section  in sec:
        print(section.find('sa_item'))
        if  section.find('sa_item') == 0:   #pos = 0
            #item
            grid_column = 0
            lb1 = Label(root, text= cf.get(section,'item_name'))
            lb1.grid(column=grid_column, row=grid_row, padx=10, pady=5, sticky=W)
            #status
            grid_column = 1
            status_name['status%s'%item_idx] = Entry(root)
            status_name['status%s'%item_idx].grid(column=grid_column, row=grid_row, pady=5)
            status_name['status%s'%item_idx].insert(10, "NA")
            #button
            grid_column = 2
            func_name = 'button_' + str(item_idx) + '_test'
            fn_obj = getattr(sys.modules[__name__], func_name, '')
            btn_name['btn%s'%item_idx] = Button(root, text='test', width=25, command=fn_obj)
            btn_name['btn%s'%item_idx].grid(column=grid_column, row=grid_row, sticky=E, pady=5)
            #udpate grid
            grid_row = grid_row + 1
            item_idx = item_idx + 1
            test_items = test_items + 1
    



    scr3.grid(row=grid_row,column=5)   
    listbox.grid(columnspan=5, row=grid_row, sticky=W)
#init com
def init_com_by_conf():
    # read config file
    cf=configparser.ConfigParser()

    # check config file 
    cf.read(SA_CONFIG_INI_PATH,encoding= 'UTF-8')
    if not cf:
        print('sa_config.ini open fail!')
        LOG.info('sa_config.ini open fail!')
        #TODO: alert
        return False

    
    # init com
    if (SERIAL.init_com('com' + cf.get('comconf','com_num'), cf.get('comconf', 'baudrate'), cf.get('comconf', 'stopbits'), cf.get('comconf','bytesize')) == 0):
        print("com%d open fail<<<" %int(cf.get('comconf','com_num'))) 
        LOG.info("com%d open fail<<<" %int(cf.get('comconf','com_num'))) 

 
        #TODO:alert
        return False

    SERIAL.port_open()
    SERIAL.message.clear()   
    print("com%d open success<<<" %int(cf.get('comconf','com_num'))) 
    LOG.info("com%d open success<<<" %int(cf.get('comconf','com_num')))      
    return True


# init by config
init_form_by_config()

# init tk form
# init_form()

# layout weight
root.columnconfigure(1, weight=1)

# main UI
center_window(root, 500, 400)


# init com
init_com_by_conf()

root.mainloop()

