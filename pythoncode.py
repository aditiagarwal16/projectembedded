import serial
import time
from picamera import PiCamera
import mysql.connector
import requests  # Import the requests library

# Setup serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Adjusted for proper port and added timeout

# Setup camera
camera = PiCamera()

# Database configuration
db_config = {
    'user': 'camera_user',
    'password': 'abcd',  # Use your new password
    'host': 'localhost',
    'database': 'camera'
}

# IFTTT Webhook URL
ifttt_webhook_url = "https://maker.ifttt.com/trigger/incorrect_pin/with/key/d1vkk3GB5E4Nke3GfWpv-IKUEaIfxcBD9JlrOm-3BVK"

# Function to capture and store image
def capture_and_store_image():
    image_path = '/home/aditi/python/unauthorized_access.jpg'
    camera.capture(image_path)

    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Read the image file as binary data
    with open(image_path, 'rb') as file:
        binary_data = file.read()
        query = "INSERT INTO images (image) VALUES (%s)"
        cursor.execute(query, (binary_data,))

    # Commit the transaction and close the connection
    connection.commit()
    cursor.close()
    connection.close()

# Function to send email notification via IFTTT
def send_email_notification():
    payload = {'value1': 'Unauthorized access detected!'}  # Customize payload if needed
    response = requests.post(ifttt_webhook_url, json=payload)
    if response.status_code == 200:
        print("Email notification sent successfully.")
    else:
        print("Failed to send email notification.")

try:
    invalid_attempts = 0
    inputPIN = ""
    while True:
        if ser.in_waiting > 0:
            # Read one character at a time from the serial buffer
            char = ser.read().decode('utf-8')
            if char == '\n':
                # When newline is received, process the complete line
                if inputPIN == "TRIGGER_CAMERA":
                    print("Incorrect PIN entered. Capturing image...")
                    capture_and_store_image()
                    print("Image captured and stored successfully.")
                    inputPIN = ""  # Reset after capturing image
                else:
                    print(f"Current PIN entry: {inputPIN}")
                    if inputPIN.isdigit():  # Check if input is a number (PIN attempt)
                        invalid_attempts += 1
                        if invalid_attempts == 2:
                            send_email_notification()  # Send email notification after 2 invalid attempts
                            invalid_attempts = 0  # Reset invalid attempts counter
                    inputPIN = ""  # Reset for next entry
            else:
                inputPIN += char
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    camera.close()
    ser.close()
