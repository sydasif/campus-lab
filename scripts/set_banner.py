#!/usr/bin/env python3
import sys
from pathlib import Path

import yaml
from netmiko import ConnectHandler
from termcolor import colored

BANNER_TEXT = "Unauthorized access is prohibited. This is a lab network."


def load_inventory(path: Path):
    try:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(colored(f"Inventory error: {e}", "red"))
        sys.exit(1)


def get_banner(platform: str) -> list:
    if platform == "cisco_ios":
        return [f"banner motd # {BANNER_TEXT} #"]
    if platform == "arista_eos":
        return ["banner login", BANNER_TEXT, "EOF"]
    return []


def configure_banner(name: str, info: dict):
    kind_map = {"arista_ceos": "arista_eos", "cisco_iol": "cisco_ios"}
    platform_value = info.get("platform")
    if not isinstance(platform_value, str):
        print(colored(f"{name} missing or invalid 'platform' in inventory.", "red"))
        return
    platform = kind_map.get(platform_value, platform_value)

    for key in ["hostname", "username", "password"]:
        if key not in info:
            print(colored(f"{name} missing '{key}' in inventory.", "red"))
            return

    commands = get_banner(platform)
    if not commands:
        print(colored(f"Skipping {name}: unsupported platform '{platform}'", "magenta"))
        return

    device = {
        "device_type": platform,
        "host": info["hostname"],
        "username": info["username"],
        "password": info["password"],
    }

    try:
        print(colored(f"\n→ Connecting to {name} ({device['host']})...", "yellow"))
        conn = ConnectHandler(**device)
        conn.enable()
        output = conn.send_config_set(commands)
        print(colored(f"✓ Banner applied on {name}\n", "green"))
        print(output)
        conn.disconnect()
    except Exception as e:
        print(colored(f"✗ Failed on {name}: {e}", "red"))


def main():
    inventory = load_inventory(Path("clab-campus/nornir-simple-inventory.yml"))
    for name, info in inventory.items():
        configure_banner(name, info)


if __name__ == "__main__":
    main()
