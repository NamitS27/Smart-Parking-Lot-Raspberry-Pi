import requests
import json
import RPi.GPIO as GPIO
import time
from requests.models import Response
from time import sleep

# Disable warnings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Set buzzer - pin 25 as output
buzzer = 25
GPIO.setup(buzzer, GPIO.OUT)


parking_lot_map = {
    (23, 24): 1,
    (20, 21): 2,
    (13, 19): 3,
    (17, 27): 4,
}


def measure_vehicle_distance(TRIG, ECHO):
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
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print(f"Vehicle distance: {distance} cm")
    return distance


def fetch_parking_lot_status():
    print("Went into fetch_parking_lot_status() function")
    parking_lot = requests.get(
        "https://iot-smart-parking-lot.herokuapp.com/get-parking-lot/")
    response = parking_lot.json()
    parking_lot_status = []
    for lot in response['slots']:
        parking_lot_status.append(lot['isPresent'])
    print(f"Parking Lot : {parking_lot_status}")
    return parking_lot_status


def detect_vehicle(TRIG, ECHO):
    print("Went into detect_vehicle() function")
    distance = measure_vehicle_distance(TRIG, ECHO)
    if distance < 3:
        print("Distance is less than 3")
        call_buzzer(True)
    elif distance < 5:
        print("Distance is < 5 & >= 3")
        call_buzzer(False)
        update_parking_lot_status(parking_lot_map[(TRIG, ECHO)])
    else:
        print("No vehicle detected")


def update_parking_lot_status(parking_space_id):
    try:
        print("Went into update_parking_lot_status() function")
        resp = requests.post(
            f"https://iot-smart-parking-lot.herokuapp.com/update-parking-lot?slot_number={parking_space_id}")
        print(f"Response from server: {resp.json()}")
    except Exception as e:
        print(e)


def call_buzzer(flag):
    print("Went into call_buzzer() function")
    if flag:
        GPIO.output(buzzer, GPIO.HIGH)
    else:
        GPIO.output(buzzer, GPIO.LOW)


if __name__ == "__main__":
    while True:
        try:
            for key, value in parking_lot_map.items():
                detect_vehicle(key[0], key[1])
                sleep(1)
        except KeyboardInterrupt:
            print("Exiting . . .")
            GPIO.cleanup()
            break
