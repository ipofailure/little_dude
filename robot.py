import RPi.GPIO as gpio
import time

motor={
    'lb':5,
    'lf':6,
    'rb':13,
    'rf':26,
    'le':17,
    're':27,
}

def init_drive():
    global lpwm,rpwm,dcycle
    dcycle=40
    gpio.setmode(gpio.BCM)
    for x in motor.keys():
        gpio.setup(motor[x], gpio.OUT)
        if x is 'le':
            lpwm=gpio.PWM(motor[x],100)
        elif x is 're':
            rpwm=gpio.PWM(motor[x],100)
    lpwm.start(dcycle)
    rpwm.start(dcycle)

def drive_f(t):
    pins=['le','re','lf','rf']
    for x in pins:
        gpio.output(motor[x], True)
    time.sleep(t)
    for x in pins:
        gpio.output(motor[x], False)

def drive_b(t):
    pins=['le','re','lb','rb']
    for x in pins:
        gpio.output(motor[x], True)
    time.sleep(t)
    for x in pins:
        gpio.output(motor[x], False)

def test(t):
    drive_f(t)
    time.sleep(1)
    drive_b(t)

def adjust_trim():
    ltrim=dcycle
    rtrim=dcycle
    t=input('Enter time in secconds to move forward and backward WARNING! robot will move as soon as you hit enter: ')
    while True:
        print('running test with trim settings: left = '+str(ltrim)+' and right = '+str(rtrim))
        test(int(t))
        I=input('adjust with [l or r] space [amount to add or subtract] or hit enter to stay the same. type "done" to exit: ')
        if I == '':
            print('Ok keeping trim the same.')
        elif I == 'done':
            print('Ok if that test passed, the trim for it was: left = '+str(ltrim)+' and right = '+str(rtrim))
            gpio.cleanup()
            exit()
        else:
            try:
                command=I.split(' ')
                flag=command[0]
                change=int(command[1])
                if flag == 'l':
                    ltrim=ltrim+change
                    lpwm.ChangeDutyCycle(ltrim)
                elif flag == 'r':
                    rtrim=rtrim+change
                    rpwm.ChangeDutyCycle(rtrim)
            except:
                print('invalid input')

init_drive()
adjust_trim()

