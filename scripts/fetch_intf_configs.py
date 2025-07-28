from nornir import InitNornir
from nornir_napalm.plugins.tasks import napalm_get
from nornir_utils.plugins.functions import print_result

# Map Containerlab platform to NAPALM-supported values
platform_map = {"arista_ceos": "eos", "cisco_iol": "ios"}


def gather_required_facts(task):
    raw_platform = task.host.get("platform")

    # Skip unsupported platforms
    if raw_platform not in platform_map:
        print(f"[SKIPPED] {task.host}: Unsupported platform '{raw_platform}'")
        return

    # Set NAPALM-compatible platform name
    task.host.platform = platform_map[raw_platform]

    try:
        task.run(
            task=napalm_get,
            getters=["interfaces"],  # ✅ Corrected 'routes'
        )
    except Exception as e:
        print(f"[ERROR] {task.host}: Failed to retrieve facts - {e}")


nr = InitNornir(config_file="config.yaml")
results = nr.run(task=gather_required_facts)

print_result(results)  # type: ignore
