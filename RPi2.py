import requests
import json
import RPi.GPIO as GPIO
import time
from requests.models import Response
from time import sleep
import datetime
import Adafruit_CharLCD as LCD  # pip3 install Adafruit-CharLCD
from gpiozero import Servo  # sudo apt install python3-gpiozero

SERVO_PIN = 25
servo = Servo(SERVO_PIN)

GATE_ULTRASONIC_TRIGGER_PIN = 23
GATE_ULTRASONIC_ECHO_PIN = 24
IR_SENSOR_PIN = 17
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
pwm = GPIO.PWM(3, 50)
pwm.start(0)

lcd_rs = 25
lcd_en = 24
lcd_d4 = 23
lcd_d5 = 17
lcd_d6 = 18
lcd_d7 = 22
lcd_backlight = 2

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

# lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5,lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


def fetch_parking_lot_status():
    print("Went into fetch_parking_lot_status() function")
    parking_lot = requests.get(
        "https://iot-smart-parking-lot.herokuapp.com/get-parking-lot/")
    response = parking_lot.json()
    parking_lot_status = []
    for lot in response['slots']:
        parking_lot_status.append(lot['isPresent'])
    print(f"Parking Lot : {parking_lot_status}")
    return parking_lot_status.count(True)


def measure_vehicle_distance(ECHO, TRIG):
    print("Went into measure_vehicle_distance() function")
    print("Distance measurement is in progress . . . .")
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)
    print("Waiting for sensor to settle . . . .")
    time.sleep(0.2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    while not GPIO.input(ECHO):
        pulse_start = time.time()
    while GPIO.input(ECHO):
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print(f"Vehicle distance: {distance} cm")
    return distance


def detect_car_at_entry_gate():
    print("Went into detect_car_at_entry_gate() function")
    # ir_input = GPIO.input(IR_SENSOR_PIN)
    distance = measure_vehicle_distance(GATE_ULTRASONIC_ECHO_PIN,
                                        GATE_ULTRASONIC_TRIGGER_PIN)
    print(f"Ultrasonic Sensor value (Detect car func): {distance}")
    if distance < 5:
        print("Gone into if statement executed when something is detected in IR sensor")
        if fetch_parking_lot_status() == 8:
            print("Parking lot is full")
            # lcd.clear()
            # lcd.message("Sorry, parking lot is full")
        else:
            generate_otp()
            for i in range(3):
                time.sleep(20)
                open_gate()


def generate_otp():
    print("Went into generate_otp() function")
    otp = requests.get(
        "https://iot-smart-parking-lot.herokuapp.com/generate-otp/")
    response = otp.json()
    otp_number = response['otp']
    print(f"OTP : {otp_number}")
    display_LCD(otp_number)


def display_LCD(text):
    print("Went into display_LCD() function")
    # lcd.clear()
    print(f"Text to be displayed on LCD : {text}")
    # lcd.message(text)


def open_gate():
    print("Went into open_gate() function")
    response = requests.get(
        "https://iot-smart-parking-lot.herokuapp.com/fetch-otp-status")
    response = response.json()
    otp_status = response['status']
    print(f"OTP Status : {otp_status}")
    if otp_status == 'success':
        # lcd.clear()
        operate_motor(90)


def operate_motor(angle):
    print("Went into operate_motor() function")
    duty = angle / 18 + 2
    GPIO.output(3, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(3, False)
    pwm.ChangeDutyCycle(0)


if __name__ == "__main__":
    while True:
        detect_car_at_entry_gate()
        time.sleep(5)
