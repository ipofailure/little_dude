import RPi.GPIO as gpio #import for triggering gpio pins on the raspberry pi. imported as "gpio"

gpio.setwarnings(False) #setting console warnings from gpio module to false because they are annoying.
gpio.setmode(gpio.BCM) #setting mode to "BCM" tells gpio that we will be referring to the nonphysical pin numbering system for pins.

driver_dict={}
'''    ^^^^
this dictionary holds each drivers pin numbers with the coresponding lables for them.
example of this having one drivers pin numbers: {0: {'ENB': 27, 'IN3': 13, 'IN4': 26, 'IN1': 5, 'ENA': 17, 'IN2': 6}}
with 0 being the index of the only initialized driver in this dictionary.
ENA,ENB,IN1,IN2,IN3,IN4 are the input lables on the actual physcal driver.
the numbers next to each of them are the pins on the pi that are connected to those inputs.
driver_dict does not have any items until a driver is initialized in fuction set_pins()
the index of each pin set is important because it is the primary key of each driver so any time you call a function to carryout
a task for a driver, you must pass the function the index number of the driver you wish to control.

see set_pins for more details.
'''
pwm_dict={}
'''
each item in this dictionary actually share the same index number as the items in driver_dict because each item in this dictionary
is responsible for storing the pulse width modulation objects constructed for its coresponding driver, in set_pwm().
example of one item stored in this dictionary:
{0: {'max_speed': 100, 'enb_pwm': <RPi.GPIO.PWM object at 0x7632dc98>, 'ena_pwm': <RPi.GPIO.PWM object at 0x768eabf0>}}
with 0 being the shared index of the first item in driver_dict
max_speed actually being the max duty cycle each motor is allowed to handle. in this case the user has set the max speed to 100%.
enb_pwm being the pulse width modulation object for speed control of motor b.
we need this object later for use with gpio.ChangeDutyCycle() which we use to change the speed of the drivers motors.
ena_pwm is the same concept as mentioned for enb_pwm, only this stores the pwm object for motor A.

see set_pwm for more details.
'''
trim_dict={}
'''
same rule as the last dictionary, the index numbers of items in this dictionary corespond with the items of the same index number in
driver_dict and pwm_dict because the items in this dictionary store the trim values for motor A and B for the coresponding driver.
why have a trim variable you ask? because life isnt perfect and you have to account for slight variations between 2 seemingly
identical motors.
example of this having one item:
{0: {'ena_trim': 100, 'enb_trim': 100}}
with 0 being the shared index of the first item in driver_dict
ena_trim stores the current user specified trim setting defined in set_trim
enb_trim is the same concept as ena_trim but for motor B

see set_trim for more details.
'''
drivers=0 #this is just a counter to help us index each driver we store in driver_dict

def set_pins(pins): #this function takes an array of pins connected to each driver, lables them, then stores them for later use.
    global drivers #we specify global variable drivers so we can increment it by one each time we define a new driver.
    driver={} #this is the driver item we append to driver_dict once we fill it with labled pins.
    lables=['ENA','IN1','IN2','IN3','IN4','ENB'] #array of lables we are going to slap on each pin.
    if len(lables) is len(pins): #if the array of user specified pins has the same amount as our array of lables...
        for x in range(0,len(pins)):#then for each pin and each lable with the same index.
            driver[lables[x]]=pins[x]#append the pin and lable pair to driver.
            gpio.setup(pins[x], gpio.OUT)#define pin as a gpio output pin.
    else:#the user didnt pass the right amount of pins and this will break things later on...
        print("incorrect amount of pins specified. takes: ['ENA','IN1','IN2','IN3','IN4','ENB']")#so we tell them the issue.
        exit()#then kill the program so they can fix their code and try again.
    index=drivers#setting an index number equal to amount of drivers we have
    driver_dict[index]=driver#we append our newly constructed driver into the driver_dict with its unique index number.
    drivers=drivers+1#we increase our counter by one, because we just added a new driver.
    return index#we return the unique identifier for this new driver for referenceing it with the rest of the functions.

def set_pwm(driver,max_duty_cycle,frequency): #setting up the pwm max_speed and frequency for a specific drivers motor pair.
    drive=driver_dict[driver] #pulling specific driver from driver_dict by index number
    max_speed=max_duty_cycle #setting user defined max speed variable 
    pwm_dict[driver]={'ena_pwm':gpio.PWM(drive['ENA'],frequency),'enb_pwm':gpio.PWM(drive['ENB'],frequency),'max_speed':max_duty_cycle} #initializing motor A and B's PWM objects, and storing them along with max speed.
    pwm_dict[driver]['ena_pwm'].start(max_duty_cycle) #starting the actual pulse width modulation for motor A
    pwm_dict[driver]['enb_pwm'].start(max_duty_cycle) #starting the actual pulse width modulation for motor B

def set_trim(driver,ENA,ENB):# setting trim for motors by off-setting the duty cycle of motor A or B by user specified values.
    max_speed=pwm_dict[driver]['max_speed'] #pulling the max_speed variable for specific driver
    if (ENA <= max_speed and ENB <= max_speed) and (ENA >= 0 and ENB >= 0): #as long as new value is within 0 and max_speed...
        trim_dict[driver]={'ena_trim':ENA,'enb_trim':ENB} #append drivers trim values for motor A and B to trim_dict for later reference.
        ena_pwm=pwm_dict[driver]['ena_pwm'].ChangeDutyCycle(ENA)#apply trim setting to motor A
        enb_pwm=pwm_dict[driver]['enb_pwm'].ChangeDutyCycle(ENB)#apply trim setting to motor B
    else: #if not in range then this will break the code later on so...
        print('trim must be set in range 0 to max speed set in set_pwm()') #we tell them the issue.
        exit() #then kill the code so they can fix their issue then try again.

def speed(driver,speed): #easily change the speed during or after operation of 2 motors of the same driver. speed being a percentage.
    ena_pwm=pwm_dict[driver]['ena_pwm'] #pulling the PWM object for motor A so we can change its duty cycle.
    enb_pwm=pwm_dict[driver]['enb_pwm'] #pulling the PWM object for motor B so we can change its duty cycle.
    ena_trim=trim_dict[driver]['ena_trim'] #pulling the current trim settings for motor A to account for it durring speed change.
    enb_trim=trim_dict[driver]['enb_trim'] #pulling the current trim settings for motor B to account for it durring speed change.
    ena_pwm.ChangeDutyCycle(speed/100*ena_trim) #change speed of A with speed being a percentage of its trim setting rather than of max speed.
    enb_pwm.ChangeDutyCycle(speed/100*enb_trim) #change speed of B with speed being a percentage of its trim setting rather than of max speed.
'''
(speed/100*enb_trim) this formula is to ensure that given any speed change, the motor still inherits the same
margin of trim specified. this is so the motors will constantly share a 1:1 speed ratio.
'''

# below are all possible combinations for directional control of 2 motors.
def both1(driver,state):
    pins=['ENA','ENB','IN2','IN4']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def both2(driver,state):
    pins=['ENA','ENB','IN1','IN3']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def opposite1(driver,state):
    pins=['ENA','ENB','IN1','IN4']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def opposite2(driver,state):
    pins=['ENA','ENB','IN2','IN3']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def motor_a1(driver,state):
    pins=['ENA','IN1']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def motor_a2(driver,state):
    pins=['ENA','IN2']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def motor_b1(driver,state):
    pins=['ENB','IN3']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

def motor_b2(driver,state):
    pins=['ENB','IN4']
    for x in pins:
        gpio.output(driver_dict[driver][x], state)

    





