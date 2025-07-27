import subprocess
import sys
import time

import yaml
from termcolor import colored


def read_clab_config(file_path):
    """Reads the lab.clab.yaml file and returns the parsed content."""
    try:
        with open(file_path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(colored(f"Error: {file_path} not found.", "red"))
        sys.exit(1)
    except yaml.YAMLError as e:
        print(colored(f"Error parsing YAML file {file_path}: {e}", "red"))
        sys.exit(1)


def get_device_info(clab_config):
    """Extracts device information (name, type, IP) from the clab config."""
    devices = {}
    if "topology" in clab_config and "nodes" in clab_config["topology"]:
        for name, properties in clab_config["topology"]["nodes"].items():
            # Exclude HOST devices as they are not network devices to be configured by Netmiko
            if name.startswith("HOST"):
                continue

            device_type = None
            # Determine device type based on 'group' or 'kind'
            if "group" in properties:
                group = properties["group"]
                if group == "core":
                    device_type = "cisco_ios"  # For RTR
                elif group == "distribution":
                    device_type = "arista_eos"  # For SW1, SW2
                elif group == "access":
                    device_type = "cisco_ios"  # For ACCESS1, ACCESS2
            elif "kind" in properties:
                if properties["kind"] == "cisco_iol":
                    device_type = "cisco_ios"
                elif properties["kind"] == "arista_ceos":
                    device_type = "arista_eos"

            if device_type and "mgmt-ipv4" in properties:
                devices[name] = {"ip": properties["mgmt-ipv4"], "type": device_type}
            else:
                print(
                    colored(
                        f"Warning: Could not determine type or IP for device {name}. Skipping.",
                        "yellow",
                    )
                )
    return devices


def execute_config_script(device_name, ip, device_type):
    """Executes the appropriate configuration script for a given device."""
    script_path = None
    if device_name.startswith("RTR"):
        script_path = "scripts/configure_rtr.py"
    elif device_name.startswith("SW"):  # SW1, SW2 are distribution switches
        script_path = "scripts/configure_dist.py"
    elif device_name.startswith("ACCESS"):
        script_path = "scripts/configure_access.py"
    else:
        print(
            colored(
                f"Warning: No specific configuration script found for device type of {device_name}. Skipping.",
                "yellow",
            )
        )
        return

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
        "admin",  # Assuming default username
        "--password",
        "admin",  # Assuming default password
    ]

    print(colored(f"\n--- Executing configuration for {device_name} ---", "blue"))
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(colored(result.stdout, "green"))
        if result.stderr:
            print(colored(f"Error output for {device_name}:\n{result.stderr}", "red"))
    except subprocess.CalledProcessError as e:
        print(colored(f"Error executing script for {device_name}: {e}", "red"))
        print(colored(f"Command: {' '.join(e.cmd)}", "red"))
        print(colored(f"Stdout: {e.stdout}", "red"))
        print(colored(f"Stderr: {e.stderr}", "red"))
    except Exception as e:
        print(colored(f"An unexpected error occurred for {device_name}: {e}", "red"))


def main():
    clab_config = read_clab_config("lab.clab.yaml")
    devices_to_configure = get_device_info(clab_config)

    if not devices_to_configure:
        print(colored("No network devices found to configure.", "yellow"))
        return

    print(colored("Discovered devices for configuration:", "blue"))
    for name, info in devices_to_configure.items():
        print(colored(f"- {name}: IP={info['ip']}, Type={info['type']}", "blue"))

    print(colored("\nStarting device configuration...", "blue"))
    start_time = time.time()

    for device_name, info in devices_to_configure.items():
        execute_config_script(device_name, info["ip"], info["type"])

    end_time = time.time()
    print(
        colored(
            f"\nAll configurations attempted. Total execution time: {end_time - start_time:.2f} seconds",
            "green",
        )
    )


if __name__ == "__main__":
    main()
