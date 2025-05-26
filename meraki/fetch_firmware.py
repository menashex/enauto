import meraki
import csv
from collections import defaultdict, Counter
from tabulate import tabulate

# Replace with your actual Meraki API key
API_KEY = '3d327ae751c97cfb4d41190007904e37321b1e15'

# Initialize the Meraki dashboard client
dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

def get_all_firmware_data():
    firmware_report = []
    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    organizations = dashboard.organizations.getOrganizations()

    for org in organizations:
        org_id = org['id']
        org_name = org['name']
        print(f"\n🔍 Processing Organization: {org_name}")

        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        for network in networks:
            network_id = network['id']
            network_name = network['name']
            print(f"  📡 Processing Network: {network_name}")

            try:
                devices = dashboard.networks.getNetworkDevices(network_id)

                for device in devices:
                    name = device.get('name', '') or 'Unnamed'
                    model = device.get('model', 'Unknown')
                    serial = device.get('serial', 'Unknown')
                    address = device.get('address', 'Unknown')
                    firmware = device.get('firmware', 'Unknown')

                    if not firmware or firmware == 'Not running configured version':
                        firmware = 'Unavailable or mismatched'

                    device_type = model[:2] if model else '??'

                    device_info = {
                        'Device Name': name,
                        'Model': model,
                        'Serial': serial,
                        'Address': address,
                        'Firmware': firmware
                    }

                    grouped_data[org_name][network_name][device_type].append(device_info)

                    firmware_report.append({
                        'Organization': org_name,
                        'Network': network_name,
                        'Device Name': name,
                        'Model': model,
                        'Serial': serial,
                        'Address': address,
                        'Firmware Version': firmware
                    })

            except Exception as e:
                print(f"    ❌ Error retrieving devices in {network_name}: {e}")

    return firmware_report, grouped_data

def print_full_table_and_compliance(grouped_data):
    for org, networks in grouped_data.items():
        print(f"\n============================")
        print(f"🏢 ORGANIZATION: {org}")
        print(f"============================")

        for network, device_types in networks.items():
            print(f"\n📶 Network: {network}")

            for device_type, devices in device_types.items():
                print(f"\n  🧩 Device Type: {device_type} — Device Count: {len(devices)}")
                print(tabulate(
                    [[
                        d['Device Name'],
                        d['Model'],
                        d['Serial'],
                        d['Address'],
                        d['Firmware']
                    ] for d in devices],
                    headers=["Device Name", "Model", "Serial", "Address", "Firmware"],
                    tablefmt="github"
                ))

                # Compliance Check
                firmware_versions = [d['Firmware'] for d in devices]
                version_counts = Counter(firmware_versions)
                majority_version, count = version_counts.most_common(1)[0]

                print(f"\n    ✅ Most common firmware: {majority_version} ({count} devices)")
                non_compliant = [d for d in devices if d['Firmware'] != majority_version]

                if non_compliant:
                    print(f"    ⚠️ Non-compliant devices:")
                    print(tabulate(
                        [[d['Device Name'], d['Model'], d['Serial'], d['Firmware']] for d in non_compliant],
                        headers=["Device Name", "Model", "Serial", "Firmware"],
                        tablefmt="grid"
                    ))
                else:
                    print("    ✅ All devices compliant.")

def export_to_csv(data, filename='meraki_firmware_report.csv'):
    if not data:
        print("No data to export.")
        return

    keys = data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"\n✅ CSV report saved to: {filename}")

if __name__ == "__main__":
    firmware_data, organized_data = get_all_firmware_data()
    print_full_table_and_compliance(organized_data)
    export_to_csv(firmware_data)
