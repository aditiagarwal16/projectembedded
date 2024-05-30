
#include <Adafruit_Keypad.h>
#include <Servo.h>

// Define the keypad pins
const byte ROWS = 4; // Four rows
const byte COLS = 4; // Four columns
char keys[ROWS][COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[ROWS] = {9, 8, 7, 6}; // Connect to the row pinouts of the keypad
byte colPins[COLS] = {5, 4, 3, 2}; // Connect to the column pinouts of the keypad

// Initialize the keypad
Adafruit_Keypad customKeypad = Adafruit_Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

// Servo setup
Servo myservo;
const int servoPin = 10;
const int lockPosition = 0;
const int unlockPosition = 90;

// Correct PIN
String correctPIN = "1234";
String inputPIN = "";
int attemptCount = 0;

void setup() {
  Serial.begin(9600);
  customKeypad.begin();
  myservo.attach(servoPin);
  myservo.write(lockPosition); // Initially lock the servo
}

void loop() {
  customKeypad.tick();

  while (customKeypad.available()) {
    keypadEvent e = customKeypad.read();
    if (e.bit.EVENT == KEY_JUST_PRESSED) {
      char key = e.bit.KEY;
      Serial.print(key); // Send the key to the serial port

      if (key == '#') {
        Serial.println(); // Newline after PIN entry
        if (inputPIN == correctPIN) {
          myservo.write(unlockPosition); // Unlock the servo
          delay(2000); // Keep it unlocked for 2 seconds
          myservo.write(lockPosition);   // Lock the servo again
        } else {
          attemptCount++;
          if (attemptCount >= 2) {
            Serial.println("TRIGGER_CAMERA"); // Send signal to Raspberry Pi
            attemptCount = 0; // Reset the attempt count
          }
        }
        inputPIN = ""; // Clear the input
      } else {
        inputPIN += key; // Append the key to the inputPIN
      }
    }
  }
}