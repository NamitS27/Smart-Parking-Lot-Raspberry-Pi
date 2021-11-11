import requests
import json
import RPi.GPIO as GPIO
import time
from requests.models import Response
from time import sleep

# Disable warnings
GPIO.setwarnings(False)


# Set buzzer - pin 23 as output
buzzer = 23
GPIO.setup(buzzer, GPIO.OUT)
GPIO.setmode(GPIO.BCM)

parking_lot_map = {
    (20, 21): 1,
    (16, 18): 2,
    (9, 10): 3,
    (7, 8): 4,
    (5, 6): 5,
    (3, 4): 6,
    (2, 3): 7,
    (0, 1): 8
}


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


def detect_vehicle(ECHO, TRIG):
    print("Went into detect_vehicle() function")
    distance = measure_vehicle_distance(ECHO, TRIG)
    if distance < 0.5:
        print("Distance is less than 0.5")
        call_buzzer(True)
    elif distance < 1.5:
        print("Distance is < 1.5 & >= 0.5")
        call_buzzer(False)
        update_parking_lot_status(parking_lot_map[(ECHO, TRIG)])
    else:
        print("No vehicle detected")


def update_parking_lot_status(parking_space_id):
    try:
        print("Went into update_parking_lot_status() function")
        requests.post(
            f"https://iot-smart-parking-lot.herokuapp.com/update-parking-lot?slot_number={parking_space_id}")
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
