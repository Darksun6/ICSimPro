import can
import pygame

# Initialize Pygame for input handling and GUI
pygame.init()

# Screen setup for Pygame window
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Vehicle Control Simulator")

# Load the joystick image
image_path = "steering.jpg"
joystick_image = pygame.image.load(image_path)
# Calculate the position to center the joystick image
image_x, image_y = (screen_width - joystick_image.get_width()) // 2, (screen_height - joystick_image.get_height()) // 2

# Load and resize the brake pedal image
brake_pedal_image_path = "Brake_pedal.png"
brake_pedal_image = pygame.image.load(brake_pedal_image_path)
# Resize the brake pedal image
new_width = 200
new_height = 200
brake_pedal_image = pygame.transform.scale(brake_pedal_image, (new_width, new_height))
# Calculate the position for the resized brake pedal image
brake_pedal_x, brake_pedal_y = 600, 450

# Setup CAN bus
bus = can.interface.Bus(bustype='socketcan', channel='vcan0', bitrate=250000)

# Function to send CAN messages
def send_can_message(can_id, data):
    message = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
    try:
        bus.send(message)
        print(f"Sent CAN message: ID={can_id}, Data={data}")
    except can.CanError:
        print("Failed to send message")

# Define control functions
def send_lock():
    send_can_message(0x200, [0x00])
    print("Doors locked")

def send_unlock():
    send_can_message(0x200, [0x01])
    print("Doors unlocked")

def adjust_speed(increment):
    global vehicle_speed
    vehicle_speed = max(0, min(100, vehicle_speed + increment))
    send_can_message(0x100, [vehicle_speed])
    print(f"Speed adjusted to: {vehicle_speed}")

def toggle_turn_signal(direction):
    data_byte = 0x09 if direction == "right" else 0x08
    send_can_message(0x300, [data_byte])
    print("signal function" , direction)

# Control states
doors_locked = True
vehicle_speed = 0
turn_signal = "off"

# Main event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                send_lock()
            elif event.key == pygame.K_u:
                send_unlock()
            elif event.key == pygame.K_UP:
                adjust_speed(10)
            elif event.key == pygame.K_DOWN:
                adjust_speed(-10)
            elif event.key == pygame.K_LEFT:
                toggle_turn_signal("left")
            elif event.key == pygame.K_RIGHT:
                toggle_turn_signal("right")

    # GUI updates
    screen.fill((0, 0, 0))
    screen.blit(joystick_image, (image_x, image_y))
    screen.blit(brake_pedal_image, (brake_pedal_x, brake_pedal_y))

    pygame.display.flip()

pygame.quit()
