import time

import netmiko

# Device parameters
devices = {
    "DIST1": {
        "device_type": "arista_eos",
        "ip": "192.168.122.11",
        "username": "admin",
        "password": "admin",
    },
    "DIST2": {
        "device_type": "arista_eos",
        "ip": "192.168.122.12",
        "username": "admin",
        "password": "admin",
    },
}


def configure_switch(device_name, device_params):
    try:
        print(f"Connecting to {device_name}...")
        net_connect = netmiko.ConnectHandler(**device_params)
        print(f"Successfully connected to {device_name}")

        net_connect.enable()

        # Determine the config file based on the device name
        if device_name == "DIST1":
            config_file = "configs/dist1.ios"
        elif device_name == "DIST2":
            config_file = "configs/dist2.ios"
        else:
            print(f"Error: Unknown device {device_name}")
            return

        # Read configuration commands from file
        with open(config_file) as f:
            config_commands = f.read().splitlines()

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
        configure_switch(device_name, device_params)

    end_time = time.time()
    print(f"Script execution time: {end_time - start_time:.2f} seconds")
