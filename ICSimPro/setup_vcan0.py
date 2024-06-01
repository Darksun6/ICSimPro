import subprocess

def setup_vcan(interface='vcan0'):
    try:
        # Load CAN modules
        subprocess.run(['sudo', 'modprobe', 'vcan'], check=True)
        subprocess.run(['sudo', 'modprobe', 'can'], check=True)

        # Create and setup vcan interface
        subprocess.run(['sudo', 'ip', 'link', 'add', 'dev', interface, 'type', 'vcan'], check=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', 'up', interface], check=True)

        print(f'Virtual CAN network interface {interface} setup complete.')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    setup_vcan()

