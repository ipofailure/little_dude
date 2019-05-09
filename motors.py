import RPi.GPIO as gpio
import time

class drive:
    def set_pins(pins):
        global motor
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        motor={}
        lables=['lb','lf','rb','rf','le','re']
        if len(lables) is len(pins):
            for x in range(0,len(pins)):
                motor[lables[x]]=pins[x]
                gpio.setup(pins[x], gpio.OUT)
        else:
            print("incorrect amount of pins specified. takes: ['lb','lf','rb','rf','le','re']")
            exit()

    def set_pwm(max_duty_cycle,frequency):
        global left_pwm,right_pwm,max_speed
        max_speed=max_duty_cycle
        left_pwm=gpio.PWM(motor['le'],frequency)
        right_pwm=gpio.PWM(motor['re'],frequency)
        left_pwm.start(max_duty_cycle)
        right_pwm.start(max_duty_cycle)

    def set_trim(left,right):
        global left_trim,right_trim
        if (left <= max_speed and right <= max_speed) and (left >= 0 and right >= 0):
            left_trim=left
            right_trim=right 
        else:
            print('trim must be set in range 0 to max speed set in set_pwm()')
            exit()

    def speed(speed):
        left_pwm.ChangeDutyCycle(speed/100*left_trim)
        right_pwm.ChangeDutyCycle(speed/100*right_trim)

    def forward(state):
        pins=['le','re','lf','rf']
        for x in pins:
            gpio.output(motor[x], state)

    def backward(state):
        pins=['le','re','lb','rb']
        for x in pins:
            gpio.output(motor[x], state)

    def left(state):
        pins=['le','re','lb','rf']
        for x in pins:
            gpio.output(motor[x], state)

    def right(state):
        pins=['le','re','lf','rb']
        for x in pins:
            gpio.output(motor[x], state)


drive.set_pins([5,6,13,26,17,27])
drive.set_pwm(100,100)
drive.set_trim(100,100)
drive.speed(40)

drive.forward(True)
time.sleep(1)
drive.forward(False)


