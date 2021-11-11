#include <Servo.h>

Servo servo1;  // create servo object to control a servo
int posn = 0; // variable to store the servo position
int IRSensor = 2; // connect ir sensor to arduino pin 2
int LED = 13; // connect Led to arduino pin 13

void rotate(){
  for (posn = 0; posn < 90; posn += 1) // goes from 0 degrees to 180 degrees
  {
    // in steps of 1 degree
    servo1.write(posn); // tell servo to go to position in variable 'pos'
    delay(10);  // waits 10ms for the servo to reach the position
  }

  for (posn = 90; posn >= 1; posn -= 1)  // goes from 180 degrees to 0 degrees                                                                                 // in steps of 1 degree
  {
    servo1.write(posn); // tell servo to go to position in variable 'pos'
    delay(10);  // waits 10ms for the servo to reach the position
  }
}

void setup() {
  pinMode (IRSensor, INPUT); // sensor pin INPUT
  pinMode (LED, OUTPUT); // Led pin OUTPUT
  servo1.attach(9); // attaches the servo on pin 9 to the servo object
}

void loop() {
  int statusSensor = digitalRead (IRSensor);
  if (statusSensor == 0){
    rotate();
  }
  delay(5);
}
