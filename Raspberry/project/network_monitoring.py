import serial
import time

def send_cmd(ser, cmd, delay=1):
    """Send AT command and return response"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    return reply

def main():
    try:
        ser = serial.Serial(
            port="/dev/serial0",
            baudrate=9600,
            timeout=1
        )
        print("=== Network Monitor ===")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error: {e}")
        return
    
    # Initialize
    send_cmd(ser, "AT")
    send_cmd(ser, "ATE0")
    
    try:
        while True:
            # Check registration
            creg = send_cmd(ser, "AT+CREG?")
            
            # Parse registration status
            if "+CREG: 0,1" in creg:
                status = "✅ Registered (Home)"
            elif "+CREG: 0,5" in creg:
                status = "✅ Registered (Roaming)"
            elif "+CREG: 0,2" in creg:
                status = "🔍 Searching..."
            elif "+CREG: 0,3" in creg:
                status = "❌ Registration Denied"
            elif "+CREG: 0,0" in creg:
                status = "⚠️ Not Registered"
            else:
                status = f"❓ Unknown: {creg.strip()}"
            
            # Check signal
            csq = send_cmd(ser, "AT+CSQ")
            signal = "Unknown"
            if "+CSQ:" in csq:
                try:
                    sig_val = csq.split("+CSQ: ")[1].split(",")[0]
                    signal = f"{sig_val}/31"
                except:
                    signal = csq.strip()
            
            # Display
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Status: {status} | Signal: {signal}")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    
    ser.close()

if __name__ == "__main__":
    main()