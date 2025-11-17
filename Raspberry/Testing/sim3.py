import serial
import time

# Configure serial port
ser = serial.Serial(
    port="/dev/serial0",
    baudrate=9600,
    timeout=3,
    rtscts=False,
    dsrdtr=False
)

def send_cmd(cmd, delay=1, wait_for=None):
    """Send AT command and read response"""
    print(f"\n>>> Sending: {cmd}")
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    
    response = ""
    start_time = time.time()
    
    # Read response for up to 'delay' seconds
    while (time.time() - start_time) < delay + 2:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode(errors="ignore")
            response += chunk
            print(chunk, end="", flush=True)
            
            # If we're waiting for a specific response, check for it
            if wait_for and wait_for in response:
                break
        time.sleep(0.1)
    
    print()  # New line
    return response

def check_network():
    """Check network registration status"""
    response = send_cmd("AT+CREG?", delay=1)
    
    # Parse response: +CREG: n,stat
    # stat: 0=not registered, 1=registered home, 5=registered roaming
    if "+CREG: 0,1" in response or "+CREG: 0,5" in response:
        print("✓ Network registered")
        return True
    else:
        print("✗ Not registered on network")
        return False

def check_signal():
    """Check signal strength"""
    response = send_cmd("AT+CSQ", delay=1)
    # +CSQ: rssi,ber
    # rssi: 0-31 (higher is better), 99 = not known
    print(f"Signal quality: {response}")
    return response

def send_sms(phone_number, message):
    """Send SMS message"""
    print(f"\n{'='*50}")
    print(f"Preparing to send SMS to {phone_number}")
    print(f"Message: {message}")
    print(f"{'='*50}\n")
    
    # Step 1: Set SMS to text mode
    response = send_cmd("AT+CMGF=1", delay=1)
    if "OK" not in response:
        print("✗ Failed to set SMS text mode")
        return False
    print("✓ SMS text mode enabled")
    
    # Step 2: Set character set to GSM
    send_cmd('AT+CSCS="GSM"', delay=1)
    
    # Step 3: Initiate SMS send
    response = send_cmd(f'AT+CMGS="{phone_number}"', delay=2, wait_for=">")
    
    if ">" not in response:
        print("✗ Did not receive '>' prompt")
        print("Possible issues:")
        print("  - SIM card not inserted or not detected")
        print("  - PIN required (check with AT+CPIN?)")
        print("  - Network not registered")
        return False
    
    print("✓ Received '>' prompt, sending message...")
    
    # Step 4: Send message text followed by Ctrl+Z
    ser.write(message.encode())
    ser.write(b"\x1A")  # Ctrl+Z to send
    
    # Step 5: Wait for confirmation
    print("Waiting for confirmation (this may take 10-30 seconds)...")
    response = ""
    start_time = time.time()
    
    while (time.time() - start_time) < 30:  # Wait up to 30 seconds
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting).decode(errors="ignore")
            response += chunk
            print(chunk, end="", flush=True)
            
            if "+CMGS:" in response:
                print("\n✓ SMS sent successfully!")
                return True
            elif "ERROR" in response:
                print("\n✗ SMS send failed with ERROR")
                return False
        time.sleep(0.5)
    
    print("\n⚠ Timeout waiting for SMS confirmation")
    return False

# ============================================================
# MAIN PROGRAM
# ============================================================

print("\n" + "="*60)
print("SIM800C SMS Sender - Diagnostic Mode")
print("="*60)

try:
    # Clear any existing data
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(1)
    
    # Test 1: Basic communication
    print("\n[1/7] Testing basic communication...")
    response = send_cmd("AT", delay=1)
    if "OK" not in response:
        print("✗ Module not responding. Check:")
        print("  - Power supply (needs 5V/2A)")
        print("  - Wiring (TX/RX crossed?)")
        print("  - Baudrate (try 115200 if 9600 doesn't work)")
        exit(1)
    print("✓ Module responding")
    
    # Test 2: Disable echo
    print("\n[2/7] Disabling echo...")
    send_cmd("ATE0", delay=1)
    
    # Test 3: Check SIM card
    print("\n[3/7] Checking SIM card status...")
    response = send_cmd("AT+CPIN?", delay=1)
    if "+CPIN: READY" not in response:
        print("✗ SIM card issue. Response:", response)
        print("  - Check if SIM is inserted correctly")
        print("  - Check if SIM requires PIN (if so, unlock with AT+CPIN=xxxx)")
        exit(1)
    print("✓ SIM card ready")
    
    # Test 4: Check network registration
    print("\n[4/7] Checking network registration...")
    for attempt in range(10):
        if check_network():
            break
        print(f"  Waiting for network... (attempt {attempt+1}/10)")
        time.sleep(2)
    else:
        print("✗ Failed to register on network")
        print("  - Check if SIM has active service")
        print("  - Check antenna connection")
        print("  - Try in a location with better signal")
        exit(1)
    
    # Test 5: Check signal strength
    print("\n[5/7] Checking signal strength...")
    check_signal()
    
    # Test 6: Check operator
    print("\n[6/7] Checking network operator...")
    send_cmd("AT+COPS?", delay=2)
    
    # Test 7: Send SMS
    print("\n[7/7] Sending SMS...")
    PHONE = "+256763583059"
    MESSAGE = "Hello from Raspberry Pi and SIM800C!"
    
    success = send_sms(PHONE, MESSAGE)
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS! SMS was sent.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("FAILED to send SMS. Check the error messages above.")
        print("="*60)

except KeyboardInterrupt:
    print("\n\nInterrupted by user")
except Exception as e:
    print(f"\n\nError: {e}")
finally:
    ser.close()
    print("\nSerial port closed.")