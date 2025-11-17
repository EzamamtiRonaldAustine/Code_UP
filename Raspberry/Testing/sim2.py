import serial
import time

ser = serial.Serial(
    port="/dev/serial0",
    baudrate=9600,
    timeout=2
)

def send_cmd(cmd, delay=1):
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    print(f">>> {cmd}")
    print(reply)
    return reply

print("Initializing SIM800C ...")

# Test communication
send_cmd("AT")

# Disable echo
send_cmd("ATE0")

# SIM status
send_cmd("AT+CPIN?")   # Should return: +CPIN: READY

# Network registration
send_cmd("AT+CREG?")   # Good values: 0,1 or 0,5

# Set SMS text mode
send_cmd("AT+CMGF=1")

PHONE = "+256763583059"

# Tell SIM800C we want to send an SMS
reply = send_cmd(f'AT+CMGS="{PHONE}"', delay=2)

# If module returns ">" it is ready for the SMS text
if ">" in reply:
    print("Prompt received, sending SMS text...")
    ser.write(b"Hello from Raspberry Pi and SIM800C!\x1A")  # CTRL+Z
else:
    print("No > prompt received. SMS cannot be sent.")

time.sleep(3)
print(ser.read_all().decode(errors="ignore"))
print("Done.")
