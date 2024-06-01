import pygame
import can
import argparse
import sys
import random
import math,time


# Constants for door and signal status
DOOR_UNLOCKED = 0
ON = 1  # Assuming '1' means on for turn signals
turn_status = [0, 0]  # Initialize both indicators as off

# Default CAN IDs for speed, doors, and turn signals
speed_can_id = 0x100
door_can_id = 0x200
signal_can_id = 0x300

# Default byte positions for doors and signals
DEFAULT_DOOR_BYTE = 0
DEFAULT_SIGNAL_BYTE = 0

# Bit masks for door status (assumed based on common usage)
CAN_DOOR1_LOCK = 0x01
CAN_DOOR2_LOCK = 0x02
CAN_DOOR3_LOCK = 0x04
CAN_DOOR4_LOCK = 0x08

# Bit masks for turn signals
CAN_LEFT_SIGNAL = 0x08
CAN_RIGHT_SIGNAL = 0x09

# CLI Argument Parsing
parser = argparse.ArgumentParser(description='Vehicle Instrument Cluster Simulator.')
parser.add_argument('--model', type=str, default='', help='Vehicle model for simulation, e.g., BMW_X1')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--can_interface', type=str, default='vcan0', help='CAN interface name')
parser.add_argument('--randomize', action='store_true', help='Enable randomization of CAN IDs and positions')
parser.add_argument('--seed', type=int, default=None, help='Seed for randomization')
args = parser.parse_args()

# Apply Randomization if Enabled
if args.randomize:
    random.seed(args.seed or random.random())
    speed_can_id = random.randint(0x100, 0x7FF)
    door_can_id = random.randint(0x100, 0x7FF)
    signal_can_id = random.randint(0x100, 0x7FF)

# Model-specific settings
model_specifics = {
}

# Default settings
default_model = {
    'speed_range': (0, 100),
    'door_sprite_position': (256, 0, 64, 64)
    ,
    'turn_signal_positions': {
        'left': (50, 50),
        'right': (200, 50),
    },
}

# Select the model configuration based on the --model argument or use defaults
model_config = model_specifics.get(args.model, default_model)

# Initialize Pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Load images with updated paths
try:
    
    speedometer_image = pygame.image.load('/home/darksun/Vehicle1/speedometer.png')
    needle_image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load('/home/darksun/Vehicle1/needle2.png'), (40, 320)), -93)
    car_image = pygame.image.load(r'/home/darksun/Vehicle1/car1.png')
    car_image2 = pygame.image.load(r'/home/darksun/Vehicle1/car2.png')
    indicator_image = pygame.image.load(r'/home/darksun/Vehicle1/Indicator.png')
    fuel_gauge_image = pygame.image.load('/home/darksun/Vehicle1/fuel1.png')
    indicator_image1 = pygame.image.load(r'/home/darksun/Vehicle1/Indicator2.png')
    indicator_image2 = pygame.image.load(r'/home/darksun/Vehicle1/Indicator3.png')
    
   # print("command line" , spritesheet_image)

    car_width=150
    car_height=150
    car_image = pygame.transform.scale(car_image, (car_width, car_height))
    car_image2 = pygame.transform.scale(car_image2, (car_width, car_height))

    fuel_guage_width = 150
    fuel_guage_height = 150
    fuel_gauge_image = pygame.transform.scale(fuel_gauge_image, (fuel_guage_width, fuel_guage_height))

    indicator_width = 500
    indicatorheight = 500
    indicator_image = pygame.transform.scale(indicator_image, (indicator_width, indicatorheight))
    indicator_image1 = pygame.transform.scale(indicator_image1, (indicator_width, indicatorheight))
    indicator_image2 = pygame.transform.scale(indicator_image2, (indicator_width, indicatorheight))
except pygame.error as e:
    print(f"Failed to load image: {e}")
    sys.exit(1)

# Fuel gauge position
fuel_gauge_pos = (600, 200)  # Update these coordinates to position the fuel gauge

indicator_pos = (140, 50)

car_pos = (600, 450)

# Speedometer and needle positions
speedometer_pos = ((screen_width - speedometer_image.get_width()) // 2,
                   (screen_height - speedometer_image.get_height()) // 2)


# Calculate the center position of the speedometer where the needle will pivot
speedometer_center_x = speedometer_pos[0] + speedometer_image.get_width() // 2
speedometer_center_y = speedometer_pos[1] + speedometer_image.get_height() // 2


# Assuming pivot is at the bottom center of the needle image
needle_pivot_x = needle_image.get_width() // 2
needle_pivot_y = needle_image.get_height()

# Setup CAN interface
try:
    bus = can.interface.Bus(channel=args.can_interface, bustype='socketcan')
except can.CanError as e:
    print(f"Error setting up CAN interface: {e}", file=sys.stderr)
    pygame.quit()
    sys.exit(1)

# Initialize car state equivalent to init_car_state() in icsim.c
current_speed = 0
door_status = [1, 1, 1, 1]  # Initialize with doors locked, 1 represents locked
turn_status = [0, 0]  # Turn signals off

# Left indicator (grey and green)
left_grey_rect = pygame.Rect(0, 0, 0, 500)
left_green_rect = pygame.Rect(0, 0, 0, 500)

# Right indicator (grey and green)
right_grey_rect = pygame.Rect(500, 0, 250, 500)
right_green_rect = pygame.Rect(750, 0, 250, 500)


def setup_can_interface(interface_name, retries=3):
    while retries > 0:
        try:
            bus = can.interface.Bus(channel=interface_name, bustype='socketcan')
            return bus
        except can.CanError as e:
            print(f"Error setting up CAN interface: {e}", file=sys.stderr)
            retries -= 1
            print("Retrying...", file=sys.stderr)
            time.sleep(1)  # wait a bit before retrying

    print("Failed to set up CAN interface after several attempts.", file=sys.stderr)
    return None

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def update_speed(speed_value):
    global model_config, current_speed, screen, needle_image

    # Determine if a specific model is being simulated and adjust accordingly
    if args.model == 'BMW_X1':
        # Specific calculations for BMW_X1, as an example
        # This is a placeholder; adjust calculations as per actual model specifications
        # Assuming speed_value is obtained directly in the correct format for BMW_X1
        current_speed = speed_value
    else:
        # For other models or the default case, adjust the speed as per the general case
        # Here you map speed_value (usually received from CAN message) to the display range
        speed_min, speed_max = model_config['speed_range']
        angle = map_value(speed_value, speed_min, speed_max, 0, -180)

 
    # Calculate the pivot offset; note that Pygame's y-axis is inverted
    if current_speed>100:
        current_speed = 100
    if current_speed<0:
        current_speed = 0

    actual_speed = current_speed*-1*1.8
    
    # if int(actual_speed) == -180:
    #     actual_speed = -174


    # Rotate the needle image. Negate the angle for correct clockwise rotation
    rotated_needle = pygame.transform.rotate(needle_image, actual_speed)

    pivot2 = [400,410]
    rect3 = rotated_needle.get_rect()
    rect3.center = pivot2

    # Blit the rotated needle onto the screen at the top left of the needle_rect
    screen.blit(rotated_needle, rect3)


def update_doors():
    global door_status, screen, car_image, car_pos, car_width, car_height

    # Define the source rectangles for closed and open doors on the spritesheet
    # Assuming the closed door is the first half and the open door is the second half of the image
    closed_door_rect = pygame.Rect(150, 150, car_width, car_height)  # First half for closed
    open_door_rect = pygame.Rect(car_width, 0, car_width, car_height)  # Second half for open

    # Destination position on the screen where the car is displayed
    dest_rect = pygame.Rect(car_pos[0], car_pos[1], car_width, car_height)

    # Assume all doors share the same status for simplicity, or modify if different doors can be independently controlled
    src_rect = open_door_rect if all(door == 0 for door in door_status) else closed_door_rect
    screen.blit(car_image, dest_rect, src_rect)

def update_turn_signals():
    global turn_status, screen, indicator_image

    # Ensure both indicators start grey unless specifically toggled
    left_rect = pygame.Rect(5777, 0, 250, 500) if not turn_status[0] else pygame.Rect(2500, 0, 250, 500)
    right_rect = pygame.Rect(5000, 0, 250, 500) if not turn_status[0] else pygame.Rect(7050, 0, 250, 500)

    # if key == 'left':
    #     turn_status[0] = 1
    #     turn_status[1] = 1

    # if key == 'right':
    #     turn_status[1] = 1
    #     turn_status[0] = 0
    if turn_status[0]:
        screen.blit(indicator_image1,(-44,-113))
    if turn_status[1]:
        screen.blit(indicator_image2,(324,-113))


def redraw_screen():
    screen.fill((0, 0, 0))  # Fill the screen with black or any background
    screen.blit(speedometer_image, speedometer_pos)  # Draw the speedometer
    screen.blit(fuel_gauge_image, fuel_gauge_pos)  # Draw the fuel gauge
    update_speed(current_speed)  # Update and draw the speed needle
    update_doors()  # Update and draw the door indicators
    update_turn_signals()  # Update and draw the turn signals
    pygame.display.flip()  # Update the full display Surface to the screen


def process_can_message(message):
    global current_speed, door_status, turn_status

    if message.arbitration_id == speed_can_id:
        current_speed = int.from_bytes(message.data[:2], byteorder='big')
    elif message.arbitration_id == door_can_id:
        door_byte = message.data[DEFAULT_DOOR_BYTE]
        if door_byte == 0:
            door_status [0] = 1
            door_status [1] = 1
            door_status [2] = 1
            door_status [3] = 1
        elif door_byte == 1: 
            door_status [0] = 0
            door_status [1] = 0
            door_status [2] = 0
            door_status [3] = 0

        print(door_byte,type(door_byte))


    elif message.arbitration_id == signal_can_id:
        signal_byte = message.data[DEFAULT_SIGNAL_BYTE]
     

        if signal_byte == 9 and turn_status[1] !=1:
            turn_status[1] = 1
            turn_status[0] = 0
        elif signal_byte == 9:
            turn_status[1] = 0
            

        if signal_byte == 8 and turn_status[0] != 1:
            turn_status[0] = 1
            turn_status[1] = 0
        elif signal_byte == 8:
            turn_status[0] = 0
            
        


def main():
    bus = setup_can_interface(args.can_interface)
    if bus is None:
        pygame.quit()
        sys.exit(1)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            message = bus.recv(0.01)  # Non-blocking call with timeout
            if message:
                process_can_message(message)
        except can.CanError as e:
            if args.debug:
                print(f"CAN error: {e}", file=sys.stderr)

        screen.fill((0, 0, 0))
        screen.blit(speedometer_image, speedometer_pos)  # Make sure this comes first
        screen.blit(fuel_gauge_image, fuel_gauge_pos)
        screen.blit(indicator_image, indicator_pos)
        if turn_status[0]:
            screen.blit(indicator_image1,(-44,-113))
        if turn_status[1]:
            screen.blit(indicator_image2,(324,-113))
        if door_status[0] and door_status[1] and door_status[2] and door_status[3]:

            screen.blit(car_image, car_pos)

        else:
            screen.blit(car_image2, car_pos)
        update_speed(current_speed)
        update_doors()
        update_turn_signals()
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
