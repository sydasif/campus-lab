from pathlib import Path

import yaml


def load_inventory(inventory_path: Path):
    """Loads and parses the nornir inventory file."""
    try:
        with inventory_path.open(encoding="utf-8") as f:
            inventory = yaml.safe_load(f)
        return inventory
    except FileNotFoundError:
        print("Inventory file not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML inventory file: {e}")
        return None


def get_device_info(inventory: dict, device_name: str):
    """Returns device information from the inventory."""
    if device_name in inventory:
        return inventory[device_name]
    print(f"Device {device_name} not found in inventory.")
    return None


def map_device_type(platform: str):
    """Maps platform to netmiko device type."""
    device_type_mapping = {"arista_ceos": "arista_eos", "cisco_iol": "cisco_ios"}
    return device_type_mapping.get(platform, platform)


def get_credentials(device_info: dict):
    """Returns username and password from device info."""
    return device_info.get("username", "admin"), device_info.get("password", "admin")


if __name__ == "__main__":
    inventory_file = Path("clab-campus/nornir-simple-inventory.yml")
    inventory = load_inventory(inventory_file)

    if inventory:
        device_name = "SW1"
        device_info = get_device_info(inventory, device_name)

        if device_info:
            print(f"Device Info for {device_name}: {device_info}")
            platform = device_info.get("platform")
            device_type = map_device_type(platform)
            print(f"Device Type: {device_type}")
            username, password = get_credentials(device_info)
            print(f"Username: {username}, Password: {password}")
