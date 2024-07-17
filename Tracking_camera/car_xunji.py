Threshold = (18, 61, 14, 89, -2, 63)
RGB_Threshold = (96, 100, -13, 5, -11, 18)

import sensor, image, time, ustruct, pyb
from pyb import UART,LED

LED(1).on()
LED(2).on()
LED(3).on()

uart = UART(3,115200)
uart.init(115200, bits=8, parity=None, stop=1)

# 识别区域
roi1 =     [(0, 17, 15, 25),        #  左  x y w h
            (65, 17, 15, 25),# 右
            (30, 0, 20, 15),#上
            (0, 0, 80, 60)]#停车

# 数据包
Run = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x41, 0x26])
Left = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x42, 0x26])
Right = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x43, 0x26])
Stop = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x44, 0x26])
Crossing = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x45, 0x26]) 

N_1 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x31, 0x26])
N_2 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x32, 0x26])
N_3 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x33, 0x26])
N_4 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x34, 0x26])

N_5 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x35, 0x26])
N_6 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x36, 0x26])
N_7 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x37, 0x26])
N_8 = bytearray([0x24, 0x4F, 0x4D, 0x56, 0x38, 0x26])

# 初始化摄像头
sensor.reset()
#sensor.set_vflip(True)
#sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)
#sensor.set_windowing([0,20,80,40])
sensor.skip_frames(time = 2000)
clock = time.clock()

while(True):
    clock.tick()
    img = sensor.snapshot().binary([Threshold])
    line = img.get_regression([(100,100)], robust = True)

    left_flag,right_flag,up_flag=(0,0,0)
    for rec in roi1:
            img.draw_rectangle(rec, color=(255,0,0))#绘制出roi区域

    if (line):
        rho_err = abs(line.rho())-img.width()/2
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        #直角坐标调整
        img.draw_line(line.line(), color = 127)
        #画出直线
        #print(rho_err,line.magnitude(),rho_err)
        if line.magnitude()>8:
            outdata=[rho_err,theta_err,0]
            print(outdata)
            outuart(rho_err,theta_err,0)
                    
            if img.find_blobs([RGB_Threshold],roi=roi1[0]):  #left
                #print('left')
                left_flag=1
            if img.find_blobs([RGB_Threshold],roi=roi1[1]):  #right
                #print('right')
                right_flag=1
            if img.find_blobs([RGB_Threshold],roi=roi1[2]):  #up
                #print('up')
                up_flag=1
            #if not img.find_blobs([RGB_Threshold],roi=roi1[3]):  #stop
                ##print('up')
                #stop_flag=1
            if left_flag==1 and right_flag==1:
                uart.write(Crossing)
                #time.sleep_ms(5)
                print("Crossing")
                continue
            if left_flag==1 and up_flag==1:
                uart.write(Left)
                print("Crossing")
                continue
            if right_flag==1 and up_flag==1:
                uart.write(Right)
                print("Right")
                continue
            #if stop_flag==1:
                #uart.write(Run)
                #print("Run")
                #continue
        else:
            pass

    else:
        pass
                
        #if  not_stop==1:
            #time.sleep_ms(1000)
            #not_stop=0
        #print('stop')
