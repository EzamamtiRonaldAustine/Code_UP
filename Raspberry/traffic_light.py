from gpiozero import TrafficLights, Button 
import time 
# TrafficLights(red, amber, green) 
lights = TrafficLights(25, 8, 7) 
button = Button(21, pull_up=True)  # button to GND, internal pull-up 
 
GREEN_TIME = 5 
AMBER_TIME = 2 
RED_TIME   = 5 
 
def all_off(): 
    lights.red.off(); lights.amber.off(); lights.green.off() 
 
def run_cycle(): 
    # Green 
    lights.green.on() 
    time.sleep(GREEN_TIME) 
    lights.green.off() 
 
    # Amber 
    lights.amber.on() 
    time.sleep(AMBER_TIME) 
    lights.amber.off() 
 
    # Red 
    lights.red.on() 
    time.sleep(RED_TIME) 
    lights.red.off() 
 
if __name__ == "__main__": 
    try: 
        all_off() 
        # Each press launches the cycle (non-blocking handler calls a blocking function — that’s okay here) 
        button.when_pressed = run_cycle 
        while True: 
            time.sleep(0.1) 
    except KeyboardInterrupt: 
        pass 
    finally: 
        all_off()