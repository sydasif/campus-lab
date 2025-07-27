#!/usr/bin/env python3
import sys
import time
from pathlib import Path

from inventory_manager import get_credentials, load_inventory, map_device_type
from netmiko import ConnectHandler
from output_utils import print_section_header, print_status, print_summary


def run_commands_on_devices(inventory: dict, command: str):
    """Connects to devices and executes the given command."""
    success_count = 0
    failure_count = 0
    start_time = time.time()

    for device_name, device_data in inventory.items():
        # Exclude HOST devices
        if device_name.startswith("HOST"):
            continue

        platform_raw = device_data.get("platform")
        if not isinstance(platform_raw, str):
            print_status(
                f"{device_name} missing or invalid 'platform' in inventory. Skipping.",
                "error",
            )
            failure_count += 1
            continue
        device_type = map_device_type(platform_raw)

        hostname = device_data.get("hostname")
        username, password = get_credentials(device_data)

        if not all([hostname, username, password]):
            print_status(
                f"{device_name} missing hostname or credentials in inventory. Skipping.",
                "error",
            )
            failure_count += 1
            continue

        device = {
            "device_type": device_type,
            "host": hostname,
            "username": username,
            "password": password,
        }
        print_status(f"Connecting to {device_name} ({device['host']})...", "connecting")
        try:
            net_connect = ConnectHandler(**device)
            print_status(f"Successfully connected to {device_name}.", "success")
            print_section_header(f"Output from {device_name}")
            output = net_connect.send_command(command)
            print(output)  # uncolored as it's raw device output
            print_status(
                f"Closing connection to {device_name}", "connecting"
            )  # Ensure closing message is yellow
            net_connect.disconnect()
            success_count += 1
        except Exception as e:
            print_status(
                f"Could not connect to or execute command on {device_name}: {e}",
                "error",
            )
            failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time
    print_summary(success_count, failure_count, total_time)


def main():
    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)
    if not inventory:
        print_status("Failed to load inventory. Exiting.", "error")
        sys.exit(1)

    print_section_header("Running 'show ip interface brief' on Devices")
    run_commands_on_devices(inventory, "show ip interface brief")


if __name__ == "__main__":
    main()
