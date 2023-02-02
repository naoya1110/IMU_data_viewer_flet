import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from datetime import datetime

import flet as ft
from flet.matplotlib_chart import MatplotlibChart



def draw_figure(ax_gyro, ax_acc, t_list, 
                gyroX_list, gyroY_list, gyroZ_list, 
                accX_list, accY_list, accZ_list):
    
    ax_gyro.clear()
    ax_acc.clear()
    
    gyroX_list = np.array(gyroX_list)*60/360 #RPM
    gyroY_list = np.array(gyroY_list)*60/360 #RPM
    gyroZ_list = np.array(gyroZ_list)*60/360 #RPM

    line_gyroX, = ax_gyro.plot(t_list, gyroX_list, lw=1, label="gyroX", color="#1f77b4")
    line_gyroY, = ax_gyro.plot(t_list, gyroY_list, lw=1, label="gyroY", color="#ff7f0e")
    line_gyroZ, = ax_gyro.plot(t_list, gyroZ_list, lw=1, label="gyroZ", color="#2ca02c")
    line_accX, = ax_acc.plot(t_list, accX_list, lw=1, label="accX", color="#1f77b4")
    line_accY, = ax_acc.plot(t_list, accY_list, lw=1, label="accY", color="#ff7f0e")
    line_accZ, = ax_acc.plot(t_list, accZ_list, lw=1, label="accZ", color="#2ca02c")
    ax_gyro.grid(True)
    ax_acc.grid(True)
    ax_gyro.legend(loc=4)
    ax_acc.legend(loc=4)
    ax_gyro.set_xlim(0, max(t_list))
    ax_acc.set_xlim(0, max(t_list))
    ax_gyro.set_ylim(-400, 400)
    ax_gyro.set_yticks(np.arange(-400, 401, 100))
    ax_acc.set_ylim(-10, 10)
    ax_acc.set_yticks(np.arange(-10, 10.1, 2.5))
    ax_gyro.set_ylabel("Rotation Speed (RPM)")
    ax_acc.set_ylabel("Acceleration (G)")
    ax_acc.set_xlabel("Time (s)")
    return ax_gyro, ax_acc


def main(page: ft.page):


    fig = plt.figure(figsize=(8, 5))        # グラフのサイズを指定
    plt.rcParams["font.size"] = 10    # フォントサイズ
    ax_gyro = fig.add_subplot(2, 1, 1)
    ax_acc = fig.add_subplot(2, 1, 2)

    elapsed_time = 0
    t_list = [0,1]
    moveflag_list = [0,0]
    gyroX_list = [0,0]
    gyroY_list = [0,0]
    gyroZ_list = [0,0]
    accX_list = [0,0]
    accY_list = [0,0]
    accZ_list = [0,0]
    ax_gyro, ax_acc = draw_figure(ax_gyro, ax_acc, t_list, 
                                    gyroX_list, gyroY_list, gyroZ_list, 
                                    accX_list, accY_list, accZ_list)

    is_receiving_ble = False

    page.title = "IMU data viewer"
    page.window_width = 700
    page.window_height=700
    page.bgcolor = "WHITE"

    app_title = ft.Text("IMU data viewer",size=40)
    current_time = ft.Text(size=30)
    message = ft.Text(size=30)
    plot = MatplotlibChart(fig, expand=True)

    #page.add(ft.Column(controls=[
    #    ft.Row(controls=[app_title]),
    #    current_time,
    #    message,
    #    plot
    #]))
    page.add(app_title)
    page.add(current_time)
    page.add(message)
    page.add(plot)
    
    plot.value = fig
    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    current_time.value = now_str
    message.value = "Preparing"
    message.color = "red"
    page.update () 

    with serial.Serial('COM4', 9600, timeout=1) as ser:
            
        while True:
            try:
                line = ser.readline()   # read a '\n' terminated line
                text_data = line.decode().split("\n")[0]
                print(line)
                
                
                if text_data=="":
                    now_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    current_time.value = now_str
                    message.value = ""
                    page.update()
                    time.sleep(0.01)
                    message.value = "Waiting for motion"
                    message.color = "green"
                    page.update() 
                
                # print(text_data)

                if text_data == "end":
                    is_receiving_ble = False
                    
                    for i_start, moveflag in enumerate(moveflag_list):
                        if moveflag == 1:
                            print(i_start)
                            i_start = max(0, i_start-20)
                            break
                    
                    i_max = t_list.index(max(t_list))
                    t_list = list(np.array(t_list)-t_list[i_start])
                    t_list = t_list[i_start:i_max]
                    gyroX_list = gyroX_list[i_start:i_max]
                    gyroY_list = gyroY_list[i_start:i_max]
                    gyroZ_list = gyroZ_list[i_start:i_max]
                    accX_list = accX_list[i_start:i_max]
                    accY_list = accY_list[i_start:i_max]
                    accZ_list = accZ_list[i_start:i_max]
                    ax_gyro, ax_acc = draw_figure(ax_gyro, ax_acc, t_list, 
                                                    gyroX_list, gyroY_list, gyroZ_list, 
                                                    accX_list, accY_list, accZ_list)
                
                    plot.value = fig
                    page.update()

                    
                
                elif is_receiving_ble:
                    count, moveflag, elapsed_time, accX, accY, accZ, gyroX, gyroY, gyroZ = text_data.split("\t")
                    moveflag = int(moveflag)
                    elapsed_time = float(elapsed_time)
                    accX = float(accX)
                    accY = float(accY)
                    accZ = float(accZ)
                    gyroX = float(gyroX)
                    gyroY = float(gyroY)
                    gyroZ = float(gyroZ.split("\n")[0])
                    
                    elapsed_time = elapsed_time/1E3
                    t_list.append(elapsed_time)
                    moveflag_list.append(moveflag)
                    gyroX_list.append(gyroX)
                    gyroY_list.append(gyroY)
                    gyroZ_list.append(gyroZ)
                    accX_list.append(accX)
                    accY_list.append(accY)
                    accZ_list.append(accZ)
                    
                     
                
                elif text_data == "start":
                    is_receiving_ble = True
                    t_list = []
                    moveflag_list = []
                    gyroX_list = []
                    gyroY_list = []
                    gyroZ_list = []
                    accX_list = []
                    accY_list = []
                    accZ_list = []
                    
                    message.value = "Receiving data via BLE"
                    message.color = "blue"
                    page.update()
                    #plt.close()


                    



            
            except ValueError:
                pass

            except KeyboardInterrupt:
                # print(t_list)
                print("Keyboard Interrupt")
                print(len(t_list))
                ser.close()
                break


ft.app(target=main)
