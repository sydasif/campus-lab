import argparse
import time
from pathlib import Path

import netmiko


def configure_access(device_name, ip, device_type, username, password):
    device_params = {
        "device_type": device_type,
        "ip": ip,
        "username": username,
        "password": password,
    }
    try:
        print(f"Connecting to {device_name} ({ip})...")
        net_connect = netmiko.ConnectHandler(**device_params)
        print(f"Successfully connected to {device_name}")

        # Determine the config file based on the device name
        # Assuming config files are named like access1.ios, access2.ios
        config_file = f"configs/{device_name.lower()}.ios"
        if not Path(config_file).exists():
            print(
                f"Error: Configuration file {config_file} not found for {device_name}"
            )
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
    parser = argparse.ArgumentParser(description="Configure an access device.")
    parser.add_argument("--name", required=True, help="Device name (e.g., ACCESS1)")
    parser.add_argument("--ip", required=True, help="Device IP address")
    parser.add_argument(
        "--type", required=True, help="Netmiko device type (e.g., cisco_ios)"
    )
    parser.add_argument("--username", default="admin", help="Device username")
    parser.add_argument("--password", default="admin", help="Device password")

    args = parser.parse_args()

    start_time = time.time()
    configure_access(args.name, args.ip, args.type, args.username, args.password)
    end_time = time.time()
    print(f"Script execution time: {end_time - start_time:.2f} seconds")
