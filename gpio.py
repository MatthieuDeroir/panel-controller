import RPi.GPIO as GPIO

# setting up GPIO couting standard as BCM
GPIO.setmode(GPIO.BCM)

# GPIO's indexes
door_1_index = 2
door_2_index = 3
power_index = 4

# setting up GPIOs as Inputs
GPIO.setup(door_1_index, GPIO.IN)
GPIO.setup(door_2_index, GPIO.IN)
GPIO.setup(power_index, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# storing results
def update_input():
    door_1 = GPIO.input(door_1_index)
    door_2 = GPIO.input(door_2_index)
    power = GPIO.input(power_index)
    return door_1, door_2, power

# printing results
# print("Door 1 :", door_1)
# print("Door 2 :", door_2)
# print("Power :", power)