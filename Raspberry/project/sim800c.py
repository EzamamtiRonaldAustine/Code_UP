import serial
import time

def send_cmd(ser, cmd, delay=1):
    """Send AT command to SIM800C and return response"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    print(f">>> {cmd}")
    print(reply)
    return reply

def wait_for_network(ser, timeout=60):
    """Wait for network registration"""
    print("Waiting for network registration...")
    start = time.time()
    
    while time.time() - start < timeout:
        reply = send_cmd(ser, "AT+CREG?", delay=1)
        
        # Check if registered (0,1 = home network, 0,5 = roaming)
        if "+CREG: 0,1" in reply or "+CREG: 0,5" in reply:
            print("✅ Registered on network!")
            return True
        
        # Check signal strength
        signal = send_cmd(ser, "AT+CSQ", delay=1)
        print(f"Signal check: {signal.strip()}")
        
        time.sleep(3)
    
    print("❌ Failed to register on network within timeout")
    return False

def main():
    try:
        ser = serial.Serial(
            port="/dev/serial0",
            baudrate=9600,
            timeout=2
        )
        print("Initializing SIM800C...")
        time.sleep(5)  # Longer initial delay
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return
    
    # Test communication
    send_cmd(ser, "AT")
    time.sleep(1)
    
    # Disable echo
    send_cmd(ser, "ATE0")
    time.sleep(1)
    
    # Check SIM status (with retries)
    for i in range(3):
        reply = send_cmd(ser, "AT+CPIN?", delay=2)
        if "READY" in reply:
            print("✅ SIM card ready")
            break
        time.sleep(2)
    
    # Wait for network registration
    if not wait_for_network(ser, timeout=60):
        print("Cannot proceed without network registration")
        ser.close()
        return
    
    # Check final signal strength
    signal = send_cmd(ser, "AT+CSQ")
    if "+CSQ: 0," in signal or "+CSQ: 99," in signal:
        print("⚠️ WARNING: Signal strength is still very weak or undetectable")
        print("Consider moving antenna to better location")
    
    # Set SMS text mode
    send_cmd(ser, "AT+CMGF=1")
    time.sleep(1)
    
    # Set SMS character set to GSM
    send_cmd(ser, "AT+CSCS=\"GSM\"")
    time.sleep(1)
    
    PHONE = "+256763583059"
    MESSAGE = "Hello from Raspberry Pi and SIM800C!"
    
    print(f"\n--- Attempting to send SMS to {PHONE} ---")
    
    # Tell SIM800C we want to send an SMS
    reply = send_cmd(ser, f'AT+CMGS="{PHONE}"', delay=2)
    
    if ">" in reply:
        print("Prompt received, sending SMS text...")
        
        # Send message text
        ser.write(MESSAGE.encode())
        time.sleep(0.5)
        
        # Send Ctrl+Z to terminate
        ser.write(b'\x1A')
        
        # Wait for transmission with progressive reading
        print("Waiting for network confirmation...")
        final_reply = ""
        
        for i in range(20):  # Wait up to 20 seconds
            time.sleep(1)
            chunk = ser.read_all().decode(errors="ignore")
            final_reply += chunk
            
            # Check if we got a response
            if "+CMGS:" in final_reply or "ERROR" in final_reply:
                break
        
        print("Final response from module:")
        print(final_reply)
        
        if "+CMGS:" in final_reply:
            print("\n✅ SMS sent successfully!")
        elif "ERROR" in final_reply:
            print("\n❌ SMS send failed with ERROR")
            # Check specific error
            error_reply = send_cmd(ser, "AT+CMEE=2", delay=1)  # Enable verbose errors
            print("Error details:", error_reply)
        else:
            print("\n❌ No response from module (timeout)")
            print("Possible reasons:")
            print("- Network congestion")
            print("- SMS service not activated on SIM")
            print("- Module needs reset")
    else:
        print("No > prompt received. SMS cannot be sent.")
    
    ser.close()
    print("Serial connection closed.")

if __name__ == "__main__":
    main()