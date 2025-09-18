# Processing (Python) code for a Radar Display
# This script reads angle and distance data from an Arduino over the serial port
# and visualizes it as a classic radar screen.
#
# MODIFIED to use a rectangular, half-screen layout.

add_library('serial')

# --- Global Variables ---
serial_port = None      # The serial port object
font = None             # Font for displaying text
in_string = ""          # String to buffer data from serial

# CHANGED: Use rectangular screen dimensions
screen_width = 800
screen_height = 450 # Half the original height with some padding

# Radar screen properties
radar_radius = 350
# CHANGED: Center coordinates are now relative to the new rectangular screen
radar_center_x = screen_width / 2
# Position the radar's baseline near the bottom of the window
radar_center_y = screen_height - 100 

# Data from Arduino
current_angle = 0
current_distance = 0

# Data storage for drawing points
point_history = []

def setup():
    """
    This function runs once when the program starts.
    It sets up the display window, initializes the serial communication,
    and loads the font.
    """
    global serial_port, font

    # --- Window and Graphics Setup ---
    # CHANGED: Use the new rectangular dimensions
    size(screen_width, screen_height)
    smooth()

    # Create a font for text display.
    font = createFont("Monospaced", 20)
    textFont(font)

    # --- Serial Communication Setup ---
    print("Available Serial Ports:")
    print(Serial.list())

    # ---!!! IMPORTANT: YOU MUST USE THE CORRECT PORT NAME !!!---
    port_name = "/dev/cu.usbmodem11101"
    
    try:
        print("Connecting to port: {}".format(port_name))
        serial_port = Serial(this, port_name, 9600)
        serial_port.clear()
        
    except Exception as e:
        print("Error opening serial port: {}".format(e))
        print("Please make sure the port name is correct and the Arduino is plugged in.")
        print("Also ensure the Arduino IDE's Serial Monitor is closed.")
        exit()


def draw():
    """
    This function runs continuously in a loop, redrawing the screen
    in each frame.
    """
    global current_angle, current_distance
    background(0, 20, 0)
    draw_radar_grid()
    draw_text_labels()
    draw_sweep_line(current_angle)
    draw_detected_points()
    update_and_draw_history()


def draw_radar_grid():
    """Draws the concentric semi-circles and lines of the radar."""
    stroke(0, 150, 0)
    noFill()
    strokeWeight(2)

    # Draw 2 concentric semi-circles for the top-half display
    for i in range(1, 3):
        radius = i * (radar_radius / 2.0)
        # Use arc() to draw only the top half of the circle (from PI to TWO_PI)
        arc(radar_center_x, radar_center_y, radius * 2, radius * 2, PI, TWO_PI)

    # Draw the horizontal closing line for the semi-circle display
    line(radar_center_x - radar_radius, radar_center_y, radar_center_x + radar_radius, radar_center_y)

    # Draw 5 radial lines for the 180-degree sweep (left-to-right)
    for i in range(5):
        angle = radians((i * 45) - 180) 
        x2 = radar_center_x + radar_radius * cos(angle)
        y2 = radar_center_y + radar_radius * sin(angle)
        line(radar_center_x, radar_center_y, x2, y2)


def draw_text_labels():
    """Displays text information on the screen."""
    fill(0, 200, 0)
    noStroke()
    # Label the 2 rings along the horizontal axis
    for i in range(1, 3):
        radius_text = i * (radar_radius / 2.0)
        text(str(i * 10) + " cm", radar_center_x + radius_text + 5, radar_center_y - 5)
        
    text("Angle: {} deg".format(current_angle), 20, 40)
    text("Distance: {} cm".format(current_distance), 20, 70)
    text("Radar Display", width / 2 - 80, 40)


def draw_sweep_line(angle):
    """Draws the moving line that sweeps across the radar."""
    stroke(0, 255, 0, 150)
    strokeWeight(3)
    rad_angle = radians(angle - 180) 
    end_x = radar_center_x + radar_radius * cos(rad_angle)
    end_y = radar_center_y + radar_radius * sin(rad_angle)
    line(radar_center_x, radar_center_y, end_x, end_y)


def draw_detected_points():
    """Draws a point on the radar for the current detection."""
    max_dist = 20.0 
    if current_distance > 0 and current_distance < max_dist:
        stroke(255, 0, 0)
        strokeWeight(5)
        rad_angle = radians(current_angle - 180)
        mapped_dist = map(current_distance, 0, max_dist, 0, radar_radius)
        point_x = radar_center_x + mapped_dist * cos(rad_angle)
        point_y = radar_center_y + mapped_dist * sin(rad_angle)
        point(point_x, point_y)
        point_history.append({'x': point_x, 'y': point_y, 'age': 255})

def update_and_draw_history():
    """Draws and fades out old points to create a trail effect."""
    global point_history
    new_history = []
    for p in point_history:
        stroke(0, p['age'], 0)
        strokeWeight(4)
        point(p['x'], p['y'])
        p['age'] -= 2
        if p['age'] > 0:
            new_history.append(p)
    point_history = new_history


def serialEvent(port):
    """
    This function is automatically called by Processing whenever new data is available.
    """
    global in_string, current_angle, current_distance

    while port.available() > 0:
        in_char = port.readChar()
        if in_char == '.':
            values = in_string.split(',')
            if len(values) == 2:
                try:
                    angle = int(values[0])
                    distance = int(values[1])
                    current_angle = angle
                    current_distance = distance
                except ValueError:
                    pass
            in_string = ""
        else:
            if in_char != '\n' and in_char != '\r':
                in_string += in_char