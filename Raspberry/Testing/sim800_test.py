import serial
import time

# Open UART
ser = serial.Serial(
    port="/dev/serial0",
    baudrate=9600,
    timeout=1
)

def send_cmd(cmd, delay=1):
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    print(f">>> {cmd}")
    print(reply)
    return reply

print("Initializing SIM800C...")

# Basic communication test
send_cmd("AT")

# Disable echo
send_cmd("ATE0")

# Check SIM card
send_cmd("AT+CPIN?")

# Check network registration
send_cmd("AT+CREG?")

# Set SMS to text mode
send_cmd("AT+CMGF=1")

# Replace with your real number
PHONE_NUMBER = "+256763583059"

# Send SMS command
send_cmd(f'AT+CMGS="{PHONE_NUMBER}"')

# Send the actual message
ser.write(b"Yo ur good, its your Raspberry pi yo.\x1A")

# Wait for SEND OK
time.sleep(3)
reply = ser.read_all().decode(errors="ignore")
print(reply)

print("Done.")
