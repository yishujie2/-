THRESHOLD = (18, 61, 14, 89, -2, 63) # Grayscale threshold for dark things...

import sensor, image, time, ustruct, pyb
from pyb import UART,LED

LED(1).on()
LED(2).on()
LED(3).on()

uart = UART(3,115200)
uart.init(115200, bits=8, parity=None, stop=1) # init with given parameters

#识别区域
roi1 =     [(0, 17, 15, 25),        #  左  x y w h
            (65,17,15,25),# 右
            (30,0,20,15),#上
            (0,0,80,60)]#停车


def outuart(x,a,flag):
    global uart;
    f_x=0
    f_a=0
    if flag==0:
        if x<0:
            x=-x
            f_x=1
        if a<0:
            a=-a
            f_a=1

    if flag==1: #十字
        x,a,f_x,f_a=(0,0,0,1)
    if flag==2: #上左
        x,a,f_x,f_a=(0,0,1,0)
    if flag==3: #上右
        x,a,f_x,f_a=(0,0,1,1)
    if flag==4: #stop
        x,a,f_x,f_a=(1,1,1,2)

    data = ustruct.pack("<bbhhhhb",      #格式为俩个字符俩个短整型(2字节)
                   0x2C,                      #帧头1
                   0x12,                      #帧头2
                   int(x), # up sample by 4   #数据1
                   int(a), # up sample by 4    #数据2
                   int(f_x), # up sample by 4    #数据1
                   int(f_a), # up sample by 4    #数据2
                   0x5B)
    if flag!=1:
        uart.write(data);  #必须要传入一个字节数组
    else:

        for x in range(50):
            uart.write(data);  #必须要传入一个字节数组
            time.sleep_ms(1)


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
    img = sensor.snapshot().binary([THRESHOLD])
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
                    
            if img.find_blobs([(96, 100, -13, 5, -11, 18)],roi=roi1[0]):  #left
                #print('left')
                left_flag=1
            if img.find_blobs([(96, 100, -13, 5, -11, 18)],roi=roi1[1]):  #right
                #print('right')
                right_flag=1
            if img.find_blobs([(96, 100, -13, 5, -11, 18)],roi=roi1[2]):  #up
                #print('up')
                up_flag=1
            #if not img.find_blobs([(96, 100, -13, 5, -11, 18)],roi=roi1[3]):  #stop
                ##print('up')
                #stop_flag=1
            if left_flag==1 and right_flag==1:
                outuart(0,0,1)
                #time.sleep_ms(5)
                print('shizi')
                continue
            if left_flag==1 and up_flag==1:
                outuart(0,0,2)
                print('up-left')
                continue
            if right_flag==1 and up_flag==1:
                outuart(0,0,3)
                print('up-right')
                continue
            #if stop_flag==1:
                #outuart(0,0,4)
                #print('stop')
                #continue
        else:
            pass

    else:
        pass

        outuart(0,0,4)
        #if  not_stop==1:
            #time.sleep_ms(1000)
            #not_stop=0
        print('stop')
