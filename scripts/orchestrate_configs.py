import subprocess
import sys
import time
from pathlib import Path

from inventory_manager import get_credentials, load_inventory, map_device_type
from output_utils import print_section_header, print_status, print_summary


def execute_config_script(device_name, ip, device_type, username, password):
    """Executes the appropriate configuration script for a given device."""
    script_path = None
    if device_name.startswith("RTR"):
        script_path = "scripts/configure_rtr.py"
    elif device_name.startswith("SW"):  # SW1, SW2 are distribution switches
        script_path = "scripts/configure_dist.py"
    elif device_name.startswith("ACCESS"):
        script_path = "scripts/configure_access.py"
    else:
        print_status(
            f"No specific configuration script found for device type of {device_name}. Skipping.",
            "warning",
        )
        return False  # Indicate failure for summary

    command = [
        sys.executable,
        script_path,
        "--name",
        device_name,
        "--ip",
        ip,
        "--type",
        device_type,
        "--username",
        username,
        "--password",
        password,
    ]

    print_section_header(f"Executing configuration for {device_name}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)  # No color for raw device output
        if result.stderr:
            print_status(f"Error output for {device_name}:\n{result.stderr}", "error")
            return False
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Error executing script for {device_name}: {e}", "error")
        print_status(f"Command: {' '.join(e.cmd)}", "error")
        print_status(f"Stdout: {e.stdout}", "error")
        print_status(f"Stderr: {e.stderr}", "error")
        return False
    except Exception as e:
        print_status(f"An unexpected error occurred for {device_name}: {e}", "error")
        return False


def main():
    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)

    if not inventory:
        print_status("Failed to load inventory. Exiting.", "error")
        return

    devices_to_configure = {}
    for name, info in inventory.items():
        if name.startswith("HOST"):
            continue

        platform = info.get("platform")
        if platform:
            device_type = map_device_type(platform)
            ip = info.get("hostname")
            username, password = get_credentials(info)

            if ip and device_type:
                devices_to_configure[name] = {
                    "ip": ip,
                    "type": device_type,
                    "username": username,
                    "password": password,
                }
            else:
                print_status(
                    f"Could not determine type or IP for device {name}. Skipping.",
                    "warning",
                )
        else:
            print_status(
                f"Device {name} missing 'platform' in inventory. Skipping.", "warning"
            )

    if not devices_to_configure:
        print_status("No network devices found to configure.", "warning")
        return

    print_section_header("Discovered devices for configuration")
    for name, info in devices_to_configure.items():
        print_status(f"- {name}: IP={info['ip']}, Type={info['type']}", "info")

    print_section_header("Starting device configuration")
    start_time = time.time()

    success_count = 0
    failure_count = 0

    for device_name, info in devices_to_configure.items():
        if execute_config_script(
            device_name, info["ip"], info["type"], info["username"], info["password"]
        ):
            success_count += 1
        else:
            failure_count += 1

    end_time = time.time()
    total_time = end_time - start_time

    print_summary(success_count, failure_count, total_time)


if __name__ == "__main__":
    main()
