import meraki
import os
import json

# === CONFIG ===
API_KEY = '013b5bb91e5a20c9c0618ea8674b58cfa61c857e'  # or use: os.environ["MERAKI_DASHBOARD_API_KEY"]
OUTPUT_DIR = "output"

# === INIT ===
dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)
offline_devices = []
online_devices = []

# === GET ORG INFO ===
orgs = dashboard.organizations.getOrganizations()
organization_name = orgs[0]['name']
organization_id = orgs[0]['id']

# === CREATE OUTPUT FOLDER IF NEEDED ===
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# === FETCH ORG-WIDE UPLINK STATUSES ONCE ===
uplinks_status = dashboard.appliance.getOrganizationApplianceUplinkStatuses(organization_id, total_pages='all')
uplinks_by_network = {u['networkId']: u for u in uplinks_status}

# === GET NETWORKS ===
networks = dashboard.organizations.getOrganizationNetworks(organization_id)

print(f"📡 Meraki Report for Organization: {organization_name}")
print("=" * 50)

for net in networks:
    network_id = net['id']
    network_name = net['name']
    
    try:
        devices = dashboard.networks.getNetworkDevices(network_id)
        clients = dashboard.networks.getNetworkClients(network_id, total_pages=1)  # You can increase pages if needed
    except Exception as e:
        print(f"⚠️ Skipping {network_name} due to error: {e}")
        continue

    # Count status
    online_count = 0
    offline_count = 0

    for dev in devices:
        status = dev.get('status', 'unknown')
        device_info = {
            "name": dev.get("name"),
            "model": dev.get("model"),
            "serial": dev.get("serial"),
            "status": status,
            "network": network_name
        }
        if status == "offline":
            offline_devices.append(device_info)
            offline_count += 1
        elif status == "online":
            online_devices.append(device_info)
            online_count += 1

    # Uplink status for this network
    uplink_info = uplinks_by_network.get(network_id, {}).get('uplinks', [])

    # === CLI OUTPUT ===
    print(f"\n📍 Network: {network_name}")
    print(f"- Devices: {len(devices)} (🟢 {online_count} | 🔴 {offline_count})")
    print(f"- Clients: {len(clients)}")
    print(f"- Uplinks:")
    for uplink in uplink_info:
        print(f"    • {uplink['interface']}: {uplink['status']} ({uplink.get('ip', 'N/A')})")

# === SAVE TO FILES ===
with open(os.path.join(OUTPUT_DIR, "offline_devices.json"), "w") as f:
    json.dump(offline_devices, f, indent=2)

with open(os.path.join(OUTPUT_DIR, "online_devices.json"), "w") as f:
    json.dump(online_devices, f, indent=2)

summary = {
    "offline_devices": offline_devices,
    "online_devices": online_devices
}
with open(os.path.join(OUTPUT_DIR, "all_devices_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print("\n✅ Device data saved to 'output/' folder.")
