import argparse
import time
from pathlib import Path

import netmiko
from inventory_manager import (
    get_credentials,
    get_device_info,
    load_inventory,
    map_device_type,
)
from output_utils import print_section_header, print_status, print_summary


def configure_rtr(device_name, ip, device_type, username, password):
    device_params = {
        "device_type": device_type,
        "ip": ip,
        "username": username,
        "password": password,
    }
    try:
        print_status(f"Connecting to {device_name} ({ip})...", "connecting")
        net_connect = netmiko.ConnectHandler(**device_params)
        print_status(f"Successfully connected to {device_name}", "success")

        # Assuming config file is named rtr.ios
        config_file = "configs/rtr.ios"
        if not Path(config_file).exists():
            print_status(
                f"Configuration file {config_file} not found for {device_name}", "error"
            )
            return

        with open(config_file) as f:
            config_commands = f.read().splitlines()

        print_status(f"Sending configuration commands to {device_name}...", "info")
        output = net_connect.send_config_set(config_commands)
        print(output)  # No color for raw device output

        print_status(
            f"Closing connection to {device_name}", "connecting"
        )  # Changed to yellow
        net_connect.disconnect()
        print_status(
            f"Configuration of {device_name} completed successfully.", "success"
        )

    except Exception as e:
        print_status(f"Error configuring {device_name}: {e}", "error")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure the router.")
    parser.add_argument("--name", required=True, help="Device name (e.g., RTR)")
    parser.add_argument("--ip", help="Device IP address (optional, will use inventory)")
    parser.add_argument(
        "--type",
        help="Netmiko device type (e.g., cisco_ios) (optional, will use inventory)",
    )
    parser.add_argument(
        "--username", help="Device username (optional, will use inventory)"
    )
    parser.add_argument(
        "--password", help="Device password (optional, will use inventory)"
    )

    args = parser.parse_args()

    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)

    if not inventory:
        print_status("Failed to load inventory. Exiting.", "error")
        exit(1)

    device_info = get_device_info(inventory, args.name)
    if not device_info:
        exit(1)

    ip = args.ip or device_info.get("hostname")
    device_type = args.type or map_device_type(device_info.get("platform"))
    username, password = get_credentials(device_info)
    username = args.username or username
    password = args.password or password

    if not all([ip, device_type, username, password]):
        print_status(
            "Missing required device information (IP, type, username, or password).",
            "error",
        )
        exit(1)

    start_time = time.time()
    configure_rtr(args.name, ip, device_type, username, password)
    end_time = time.time()
    print_status(f"Script execution time: {end_time - start_time:.2f} seconds", "info")
