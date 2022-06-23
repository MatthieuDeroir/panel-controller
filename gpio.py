import RPi.GPIO as GPIO
from time import sleep

# setting up GPIO counting standard as BCM
GPIO.setmode(GPIO.BCM)

# GPIO's indexes
door_1_index = 2
door_2_index = 3
power_index = 4
led_1_index = 17
led_2_index = 27

# setting up GPIOs as Inputs
GPIO.setup(door_1_index, GPIO.IN)
GPIO.setup(door_2_index, GPIO.IN)
GPIO.setup(power_index, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_1_index, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(led_2_index, GPIO.OUT, initial=GPIO.HIGH)


# storing results
def update_input():
    door_1 = GPIO.input(door_1_index)
    door_2 = GPIO.input(door_2_index)
    power = GPIO.input(power_index)
    return door_1, door_2, power


def change_output(state):
    if state:
        led_1 = GPIO.output(led_1_index, GPIO.LOW)
        sleep(1)
        led_2 = GPIO.output(led_2_index, GPIO.LOW)
        state_1 = GPIO.gpio_function(led_1_index)
        state_2 = GPIO.gpio_function(led_2_index)
        print("ALLUMAGE")
        print("LED 1 :", led_1, state_1)
        print("LED 2 :", led_2, state_2)
    else:
        led_1 = GPIO.output(led_1_index, GPIO.HIGH)
        sleep(1)
        led_2 = GPIO.output(led_2_index, GPIO.HIGH)
        state_1 = GPIO.gpio_function(led_1_index)
        state_2 = GPIO.gpio_function(led_2_index)
        print("ETEIGNAGE")
        print("LED 1 :", led_1, state_1)
        print("LED 2 :", led_2, state_2)
