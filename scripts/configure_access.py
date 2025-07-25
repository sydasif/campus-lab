import time
from pathlib import Path

import netmiko

# Device parameters
devices = {
    "ACCESS1": {
        "device_type": "cisco_ios",
        "ip": "192.168.122.21",
        "username": "admin",
        "password": "admin",
    },
    "ACCESS2": {
        "device_type": "cisco_ios",
        "ip": "192.168.122.22",
        "username": "admin",
        "password": "admin",
    },
}


def configure_access(device_name, device_params):
    try:
        print(f"Connecting to {device_name}...")
        net_connect = netmiko.ConnectHandler(**device_params)
        print(f"Successfully connected to {device_name}")

        # Determine the config file based on the device name
        if device_name == "ACCESS1":
            config_file = "configs/access1.ios"
        elif device_name == "ACCESS2":
            config_file = "configs/access2.ios"
        else:
            print(f"Error: Unknown device {device_name}")
            return

        config_commands = Path(config_file).read_text(encoding="utf-8").splitlines()

        print(f"Sending configuration commands to {device_name}...")
        output = net_connect.send_config_set(config_commands)
        print(output)

        print(f"Closing connection to {device_name}")
        net_connect.disconnect()

    except Exception as e:
        print(f"Error configuring {device_name}: {e}")


if __name__ == "__main__":
    start_time = time.time()
    for device_name, device_params in devices.items():
        configure_access(device_name, device_params)

    end_time = time.time()
    print(f"Script execution time: {end_time - start_time:.2f} seconds")
