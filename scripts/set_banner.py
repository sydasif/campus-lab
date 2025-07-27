#!/usr/bin/env python3
import sys
import time  # Added this line
from pathlib import Path

from inventory_manager import get_credentials, load_inventory, map_device_type
from netmiko import ConnectHandler
from output_utils import (
    print_device_action,
    print_section_header,
    print_status,
    print_summary,
)

BANNER_TEXT = "Unauthorized access is prohibited. This is a lab network."


def get_banner(platform: str) -> list:
    if platform == "cisco_ios":
        return [f"banner motd # {BANNER_TEXT} #"]
    if platform == "arista_eos":
        return ["banner login", BANNER_TEXT, "EOF"]
    return []


def configure_banner(name: str, info: dict):
    platform_raw = info.get("platform")
    if not isinstance(platform_raw, str):
        print_status(f"{name} missing or invalid 'platform' in inventory.", "error")
        return False
    platform = map_device_type(platform_raw)

    hostname = info.get("hostname")
    username, password = get_credentials(info)

    if not all([hostname, username, password]):
        print_status(f"{name} missing hostname or credentials in inventory.", "error")
        return False

    commands = get_banner(platform)
    if not commands:
        print_status(f"Skipping {name}: unsupported platform '{platform}'", "warning")
        return False

    device = {
        "device_type": platform,
        "host": hostname,
        "username": username,
        "password": password,
    }

    try:
        print_status(f"Connecting to {name} ({device['host']})...", "connecting")
        conn = ConnectHandler(**device)
        conn.enable()
        output = conn.send_config_set(commands)
        print_status(f"Banner applied on {name}", "success")
        print(output)  # No color for raw device output
        print_status(f"Closing connection to {name}", "connecting")  # Changed to yellow
        conn.disconnect()
        return True
    except Exception as e:
        print_status(f"Failed on {name}: {e}", "error")
        return False


def main():
    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)

    if not inventory:
        print_status("Failed to load inventory. Exiting.", "error")
        sys.exit(1)

    print_section_header("Applying Banners to Devices")

    success_count = 0
    failure_count = 0
    start_time = time.time()

    for name, info in inventory.items():
        # Exclude HOST devices
        if name.startswith("HOST"):
            continue
        if configure_banner(name, info):
            success_count += 1
        else:
            failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time
    print_summary(success_count, failure_count, total_time)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
