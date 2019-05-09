import RPi.GPIO as gpio
import time

gpio.setwarnings(False)
gpio.setmode(gpio.BCM)

driver_dict={}
pwm_dict={}
trim_dict={}
drivers=0

def set_pins(pins):
    global drivers
    driver={}
    lables=['lb','lf','rb','rf','le','re']
    if len(lables) is len(pins):
        for x in range(0,len(pins)):
            driver[lables[x]]=pins[x]
            gpio.setup(pins[x], gpio.OUT)
    else:
        print("incorrect amount of pins specified. takes: ['lb','lf','rb','rf','le','re']")
        exit()
    index=drivers
    driver_dict[index]=driver
    drivers=drivers+1
    return index

def set_pwm(driver,max_duty_cycle,frequency):
    drive=driver_dict[driver]
    max_speed=max_duty_cycle
    pwm_dict[driver]={'left_pwm':gpio.PWM(drive['le'],frequency),'right_pwm':gpio.PWM(drive['re'],frequency),'max_speed':max_duty_cycle}
    pwm_dict[driver]['left_pwm'].start(max_duty_cycle)
    pwm_dict[driver]['right_pwm'].start(max_duty_cycle)

def set_trim(driver,left,right):
    max_speed=pwm_dict[driver]['max_speed']
    if (left <= max_speed and right <= max_speed) and (left >= 0 and right >= 0):
        trim_dict[driver]={'left_trim':left,'right_trim':right} 
    else:
        print('trim must be set in range 0 to max speed set in set_pwm()')
        exit()

def speed(driver,speed):
    left_pwm=pwm_dict[driver]['left_pwm']
    right_pwm=pwm_dict[driver]['right_pwm']
    left_trim=trim_dict[driver]['left_trim']
    right_trim=trim_dict[driver]['right_trim']
    left_pwm.ChangeDutyCycle(speed/100*left_trim)
    right_pwm.ChangeDutyCycle(speed/100*right_trim)

def forward(driver,state):
    pins=['le','re','lf','rf']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def backward(driver,state):
    pins=['le','re','lb','rb']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def left(driver,state):
    pins=['le','re','lb','rf']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def right(driver,state):
    pins=['le','re','lf','rb']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def test(x):
    print(x)



motor1=set_pins([5,6,13,26,17,27])
set_pwm(motor1,100,100)
set_trim(motor1,100,100)
speed(motor1,50)

forward(motor1,True)
time.sleep(1)
forward(motor1,False)


