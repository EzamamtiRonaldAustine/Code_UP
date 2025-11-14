import serial
import time

# Initialize serial connection
ser = serial.Serial(
    port="/dev/serial0",
    baudrate=9600,
    timeout=5  # Increased timeout
)

def send_cmd(cmd, delay=2, wait_for=None):
    """Send AT command and wait for response"""
    ser.reset_input_buffer()  # Clear any old data
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    print(f">>> {cmd}")
    print(f"<<< {reply}")
    return reply

def wait_for_response(timeout=10):
    """Wait for module to respond"""
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting:
            return ser.read_all().decode(errors="ignore")
        time.sleep(0.1)
    return ""

print("=" * 50)
print("SIM800C Diagnostic Test")
print("=" * 50)

# Give module time to boot
print("\nWaiting for module to boot (10 seconds)...")
time.sleep(10)

# Test 1: Basic communication
print("\n[TEST 1] Basic AT command test")
for i in range(3):
    reply = send_cmd("AT")
    if "OK" in reply:
        print("✓ Module responding!")
        break
    print(f"Attempt {i+1}/3 failed. Retrying...")
    time.sleep(2)
else:
    print("✗ FAILED: Module not responding to AT commands")
    print("\nTroubleshooting:")
    print("1. Check power supply (needs 2A)")
    print("2. Verify TX/RX connections aren't swapped")
    print("3. Try disabling serial console: sudo raspi-config > Interface > Serial")
    exit(1)

# Test 2: Disable echo
print("\n[TEST 2] Disabling echo")
send_cmd("ATE0")

# Test 3: Check SIM card
print("\n[TEST 3] Checking SIM card")
reply = send_cmd("AT+CPIN?", delay=2)
if "+CPIN: READY" in reply:
    print("✓ SIM card ready")
elif "+CPIN: SIM PIN" in reply:
    print("✗ SIM card requires PIN")
    exit(1)
else:
    print("✗ SIM card not detected or error")
    print("Check: SIM card inserted correctly? Has credit?")
    exit(1)

# Test 4: Check signal strength
print("\n[TEST 4] Checking signal strength")
reply = send_cmd("AT+CSQ")
if "+CSQ:" in reply:
    # Extract signal strength (0-31, 99=unknown)
    try:
        rssi = int(reply.split("+CSQ:")[1].split(",")[0].strip())
        if rssi == 99:
            print("✗ No signal detected")
        elif rssi < 10:
            print(f"⚠ Weak signal: {rssi}/31")
        else:
            print(f"✓ Signal strength: {rssi}/31")
    except:
        print("Could not parse signal strength")

# Test 5: Network registration
print("\n[TEST 5] Checking network registration")
for i in range(6):  # Try for 60 seconds
    reply = send_cmd("AT+CREG?", delay=2)
    if "+CREG: 0,1" in reply or "+CREG: 0,5" in reply:
        print("✓ Registered on network!")
        break
    elif "+CREG: 0,2" in reply:
        print(f"⏳ Searching for network... ({i+1}/6)")
        time.sleep(10)
    else:
        print(f"Network status: {reply}")
        time.sleep(10)
else:
    print("✗ Not registered on network")
    print("Check: Is Lyca SIM activated? Has it been used recently?")
    exit(1)

# Test 6: Check operator
print("\n[TEST 6] Checking operator")
reply = send_cmd("AT+COPS?", delay=3)
print(f"Operator: {reply}")

# Test 7: Set SMS text mode
print("\n[TEST 7] Setting SMS text mode")
reply = send_cmd("AT+CMGF=1")
if "OK" in reply:
    print("✓ SMS text mode set")

# Test 8: Send SMS
print("\n[TEST 8] Sending SMS")
PHONE = "+256764152908"
print(f"Recipient: {PHONE}")

ser.reset_input_buffer()
ser.write(f'AT+CMGS="{PHONE}"\r\n'.encode())
time.sleep(1)

# Wait for > prompt
prompt = wait_for_response(timeout=5)
print(f"<<< {prompt}")

if ">" in prompt:
    print("✓ Prompt received! Sending message...")
    message = "Hello from Raspberry Pi and SIM800C!"
    ser.write((message + "\x1A").encode())  # \x1A is Ctrl+Z
    
    # Wait for response (can take 10-30 seconds)
    print("Waiting for confirmation (this may take 30 seconds)...")
    response = wait_for_response(timeout=30)
    print(f"<<< {response}")
    
    if "+CMGS:" in response or "OK" in response:
        print("✓ SMS SENT SUCCESSFULLY!")
    else:
        print("✗ SMS send failed")
        print("Response:", response)
else:
    print("✗ No prompt received")
    print("This usually means:")
    print("- Not registered on network")
    print("- SIM has no credit")
    print("- Invalid phone number format")

print("\n" + "=" * 50)
print("Test complete")
print("=" * 50)

ser.close()