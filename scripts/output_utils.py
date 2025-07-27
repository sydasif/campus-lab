def print_status(message: str, status_type: str = "info"):
    """Prints a status message with appropriate emoji."""
    if status_type == "info":
        print(f"ℹ️ {message}")
    elif status_type == "success":
        print(f"✓ {message}")
    elif status_type == "error":
        print(f"✗ {message}")
    elif status_type == "warning":
        print(f"⚠️ {message}")
    elif status_type == "connecting":
        print(f"→ {message}")
    else:
        print(message)


def print_device_action(device_name: str, action: str, status: str = "info"):
    """Prints a standardized message for device actions."""
    print_status(f"{action} {device_name}", status)


def print_section_header(title: str):
    """Prints a formatted section header."""
    print(f"\n--- {title} ---")


def print_summary(success_count: int, failure_count: int, total_time: float):
    """Prints a summary of operations."""
    print_section_header("Summary")
    print_status(f"Total devices processed: {success_count + failure_count}", "info")
    print_status(f"Successful operations: {success_count}", "success")
    print_status(f"Failed operations: {failure_count}", "error")
    print_status(f"Total execution time: {total_time:.2f} seconds", "info")
