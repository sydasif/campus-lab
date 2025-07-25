import time

import netmiko

time.sleep(10)

# Device parameters
device = {
    "device_type": "cisco_ios",
    "ip": "192.168.122.10",
    "username": "admin",
    "password": "admin",
}


def configure_rtr(device_params):
    try:
        print("Connecting to RTR...")
        net_connect = netmiko.ConnectHandler(**device_params)
        print("Successfully connected to RTR")

        # Read configuration commands from file
        with open("configs/rtr.ios") as f:
            config_commands = f.read().splitlines()

        print("Sending configuration commands to RTR...")
        output = net_connect.send_config_set(config_commands)
        print(output)

        print("Closing connection to RTR")
        net_connect.disconnect()

    except Exception as e:
        print(f"Error configuring RTR: {e}")


if __name__ == "__main__":
    start_time = time.time()
    configure_rtr(device)

    end_time = time.time()
    print(f"Script execution time: {end_time - start_time:.2f} seconds")
    end_time = time.time()
    print(f"Script execution time: {end_time - start_time:.2f} seconds")
