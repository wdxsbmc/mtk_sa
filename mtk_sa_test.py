#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

test_run = 0

root = tkinter.Tk()


btn_name = locals()
status_name = locals()

root.title("MTK SA TestV1.0.1")
SERIAL = com()
result_data = []

SA_CONFIG_INI_PATH= ".\sa_config.ini"

# read save data thread
def read_data_thd(SERIAL, test_run):
    #time.sleep(1)
    while test_run:
        if (SERIAL.port_is_open()):
            SERIAL.read_data()
            time.sleep(0.5)


def parse_save_thd(SERIAL, test_run, file_name):

    pkt_offset = 0
    time.sleep(1)
    old_len = 0
    old_offset = 0
    parse_msg = SERIAL.message[old_len:]
    b_find = 0
    b_finish = 0

    while test_run:

        time.sleep(0.5)
        # get pkt
        #parse_msg.extend(SERIAL.message[old_len:])
        #old_len = len(parse_msg)

        parse_msg = SERIAL.message
        # print(pkt_offset,len(parse_msg))
        # parse message
        while (pkt_offset < len(parse_msg)):

            # wait next pkt or stop
            if (pkt_offset + 4 > len(parse_msg)):
                if (old_offset != pkt_offset):
                    print('break1 at:',pkt_offset)
                    old_offset = pkt_offset
                break

            # find pkt head
            # print(pkt_offset,len(parse_msg))
            b_find = 0
            for i in range(pkt_offset, len(parse_msg)):
                if (parse_msg[i - 1] == 0xFE and parse_msg[i] == 0x68):
                    pkt_offset = i  #move offset
                    b_find = 1
                    break
            if (b_find == 0):
                break

            # get pkt data len          
            if(pkt_offset + 4 > len(parse_msg)):
                print(pkt_offset,len(parse_msg))
                continue

            pkt_data_len = parse_msg[pkt_offset + 4]
            if (pkt_data_len == 0):
                pkt_offset = pkt_offset + 6  #skip first rsp
                continue

            # check finsih
            #if (parse_msg[pkt_offset + 8] == 0x80):
                #b_finish = 1

            # get pkt data
            pkt_data_len = pkt_data_len - 5  #skip Seq(4bytes)+CUR_MOD(1byte)
            pkt_data = parse_msg[pkt_offset + 10:
                                 pkt_offset + 10 + pkt_data_len]
            pkt_offset = pkt_offset + 10 + pkt_data_len
            print(pkt_data)

            # save data
            with open(file_name, 'a') as fp:
                for i in range(0, len(pkt_data), 2):
                    if(i+2 > len(pkt_data)):
                        print(i,len(pkt_data))
                        break
                    #dcL dcH =>int16
                    dc_value = 0
                    dc_value = pkt_data[i + 1]
                    dc_value <<= 8
                    dc_value = dc_value | pkt_data[i]
                    fp.write(str(dc_value) + ',')
                    # save numpy
                    result_data.append(dc_value)

            # check finish
            #if (b_finish == 1):
                # stop parse
                #return


# button sttart
def button_start():
    print("test start>>>")
    button1.config(state="disabled")
    # init filename
    file_name = ".\dc_current_data"
    file_name += time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(
        time.time()))
    file_name += ".txt"
    en_lb.config(state="normal")
    en_lb.insert(20, file_name)
    en_lb.config(state="disabled")

    # clean plot data
    result_data.clear()

    # init com
    if (SERIAL.init_com('com' + en_com.get()) == 0):
        button1.config(state="normal")
        print("com%d open fail<<<" % int(en_com.get()))
        return
    SERIAL.port_open()
    SERIAL.message.clear()

    # start test
    data = []
    data.append(int(en_model.get()))
    n_hz = int(en_hz.get())
    data.append(n_hz & 0xFF)
    n_hz >>= 8
    data.append(n_hz & 0xFF)

    n_time = int(en_time.get())
    data.append(n_time & 0xFF)
    n_time >>= 8
    data.append(n_time & 0xFF)
    n_time >>= 8
    data.append(n_time & 0xFF)
    n_time >>= 8
    data.append(n_time & 0xFF)

    data_len = len(data)
    ret = SERIAL.cmd_send(en_pld_borad.get(),
                          en_pld_port.get(), 0x07, data_len, data, 0x87)

    if (ret == 1):
        # thread for recv
        test_run = 1
        _thread.start_new_thread(read_data_thd, (SERIAL, test_run))
        time.sleep(1)
        _thread.start_new_thread(parse_save_thd, (SERIAL, test_run, file_name))


# button stop
def button_stop():
    test_run = 0
    time.sleep(3)
    # send stop cmd
    data1 = []
    ret = SERIAL.cmd_send_recv(en_pld_borad.get(),
                               en_pld_port.get(), 0x08, 0, data1, 0x88)

    # close port
    SERIAL.message.clear()
    SERIAL.port_close()

    #root.destroy()
    print("test stop<<<")
    button1.config(state="normal")

# button draw
def button_draw():
    # 通过rcParams设置全局横纵轴字体大小
    mpl.rcParams['xtick.labelsize'] = 24
    mpl.rcParams['ytick.labelsize'] = 24

    #np.random.seed(42)
    y = np.array(result_data)

    # x轴的采样点
    #x = np.linspace(0, 5, 100)
    x_data = []
    for i in range(0, len(result_data)):
        x_data.append(i)

    x = np.array(x_data)
    # 通过下面曲线加上噪声生成数据，所以拟合模型就用y了……
    #y = 2*np.sin(x) + 0.3*x**2
    #y_data = y + np.random.normal(scale=0.3, size=100)

    # figure()指定图表名称
    #plt.figure('data')

    # '.'标明画散点图，每个散点的形状是个圆
    plt.plot(x, y, '.')

    # 画模型的图，plot函数默认画连线图
    #plt.figure('model')
    #plt.plot(x, y)

    # 两个图画一起
    #plt.figure('data & model')

    # 通过'k'指定线的颜色，lw指定线的宽度
    # 第三个参数除了颜色也可以指定线形，比如'r--'表示红色虚线
    # 更多属性可以参考官网：http://matplotlib.org/api/pyplot_api.html
    plt.plot(x, y, 'k', lw=3)

    # scatter可以更容易地生成散点图
    plt.scatter(x, y)

    # 将当前figure的图保存到文件result.png
    plt.savefig('result.png')

    # 一定要加上这句才能让画好的图显示在屏幕上
    plt.show()

# centrer
def center_window(root, width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2,
                            (screenheight - height) / 2)
    #print(size)
    root.geometry(size)


def string parse_data(msg):
    data = msg[1:msg[1]]
    return ''.join(data)

# send recv data thread
def send_recv_data_thd(SERIAL, item_idx, data):
    if (SERIAL.port_is_open()):
        SERIAL.send_recv_data(data)
        #parse pkt
        parse_msg = SERIAL.message
        if(parse_msg[0] == 0x01):
            str_info = parse_data(parse_msg)
            status_name['status%s'%item_idx].insert(10, str_info)
            pass
        else if(parse_msg[0] == 0x02):
            pass

    # enable the button
    btn_name['btn%s'%item_idx].config(state="normal")

# button action
def button_1_test():
    print(sys._getframe().f_code.co_name)

    # disable button
    item_idx = 1
    btn_name['btn%s'%item_idx].config(state="disabled")

    # send data
    data[]
    # tag
    data.append(0x01)
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
    cf.read(".\sa_config.ini")
    sec = []
    option= []
    item = []
    sec = cf.sections()                           #获取读到的所有sections(域)，返回列表类型
    #option = cf.options('comconf')               #某个域下的所有key，返回列表类型
    #item = cf.items('comconf')                 #某个域下的所有key，value对
    #value=cf.get('comconf','com_num')       #获取某个yu下的key对应的value值
    #cf.type(value)                          #获取的value值的类型
    print(sec)
    grid_column = 0
    grid_row = 0
    item_idx = 1
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
            status_name['status%s'%item_idx].insert(10, "0")
            #button
            grid_column = 2
            func_name = 'button_' + str(item_idx) + '_test'
            fn_obj = getattr(sys.modules[__name__], func_name, '')
            btn_name['btn%s'%item_idx] = Button(root, text='test', width=25, command=fn_obj)
            btn_name['btn%s'%item_idx].grid(column=grid_column, row=grid_row, sticky=E, pady=5)
            #udpate grid
            grid_row = grid_row + 1
            item_idx = item_idx + 1

#init com
def init_com_by_conf():
    # read config file
    cf=configparser.ConfigParser()

    # check config file 
    cf.read(SA_CONFIG_INI_PATH)
    if !cf:
        print('sa_config.ini open fail!')
        #TODO: alert
        return FALSE

    
    # init com
    if (SERIAL.init_com('com' + cf.get('comconf','com_num'), cf.get('comconf', 'baudrate'), cf.get('com_conf', 'stopbits'), cf.get('com_conf','bytesize')) == 0):
        print("com%d open fail<<<" %cf.get('comconf','com_num')) 
        #TODO:alert
        return FALSE

    SERIAL.port_open()
    SERIAL.message.clear()    


# init com
#init_com_by_conf()

# init by config
init_form_by_config()

# init tk form
# init_form()

# layout weight
root.columnconfigure(1, weight=1)

# main UI
center_window(root, 450, 600)
# 进入消息循环
root.mainloop()