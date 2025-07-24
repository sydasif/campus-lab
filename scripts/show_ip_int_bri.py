#!/usr/bin/env python3
import sys
from pathlib import Path

import yaml
from netmiko import ConnectHandler
from termcolor import colored


def load_inventory(inventory_path: Path):
    """Loads and parses the inventory file."""
    try:
        with inventory_path.open(encoding="utf-8") as f:
            inventory = yaml.safe_load(f)
        return inventory
    except FileNotFoundError:
        print(colored("Inventory file not found.", "red"))
        sys.exit(1)
    except yaml.YAMLError as e:
        print(colored(f"Error parsing YAML inventory file: {e}", "red"))
        sys.exit(1)


def run_commands_on_devices(inventory: dict, command: str):
    """Connects to devices and executes the given command."""
    for device_name, device_data in inventory.items():
        device_type_mapping = {"arista_ceos": "arista_eos", "cisco_iol": "cisco_ios"}
        device_type = device_type_mapping.get(
            device_data["platform"], device_data["platform"]
        )

        device = {
            "device_type": device_type,
            "host": device_data["hostname"],
            "username": device_data["username"],
            "password": device_data["password"],
        }
        print(colored(f"\nConnecting to {device_name} ({device['host']})...", "yellow"))
        try:
            net_connect = ConnectHandler(**device)
            print(colored(f"Successfully connected to {device_name}.", "green"))
            output = net_connect.send_command(command)
            print(colored(f"\n--- Output from {device_name} ---", "yellow"))
            print(output)  # uncolored as it's raw device output
            net_connect.disconnect()
        except Exception as e:
            print(
                colored(
                    f"Could not connect to or execute command on {device_name}: {e}",
                    "red",
                )
            )


def main():
    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)
    if inventory:
        run_commands_on_devices(inventory, "show ip interface brief")


if __name__ == "__main__":
    main()
