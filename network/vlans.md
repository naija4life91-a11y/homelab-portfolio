# VLAN Design

## Status: ✅ Implemented (October 2026)

The network is segmented by trust level on the UniFi Dream Router 7 using UniFi's zone-based firewall. The original flat network (`Default`) was kept as the trusted network, and every other device class was moved into its own isolated VLAN.

---

## Networks

| VLAN | Name | Subnet | Zone | Isolated | Purpose |
|---|---|---|---|---|---|
| 1 | Default (Trusted) | `192.168.1.0/24` | Internal | No | Admin devices, family phones and laptops |
| 30 | Kids | `10.0.30.0/24` | Internal | Yes | Kids' phones, tablets, consoles |
| 40 | Gaming | `10.0.40.0/24` | Internal | Yes | Xbox Series X (wired) |
| 50 | Storage / Servers | `10.0.50.0/24` | Internal | Yes | NAS, Proxmox host, Raspberry Pi 4 |
| 60 | IoT | `10.0.60.0/24` | Internal | Yes | Smart home devices, corporate-managed work laptop |
| 70 | Camera | `10.0.70.0/24` | Internal | Yes | IP cameras, video doorbell |
| 80 | Guest | Guest range | Hotspot | n/a | Visitors |

### Design decisions

- **No separate "Trusted" VLAN.** The existing Default network became the trusted network. That avoided re-joining every existing device and kept the UniFi management plane where it already was.
- **Camera and IoT kept separate.** Cameras carry sensitive video and some of them come from a discontinued vendor with no future firmware updates, so they get their own isolated segment.
- **Work laptop on IoT, not Default.** A corporate-managed laptop only needs the internet (VPN, Microsoft 365). Isolating it keeps employer-managed software off the personal network, and it keeps the personal network out of the employer's view.
- **Guest uses the Hotspot zone.** UniFi's Hotspot zone blocks guests from the gateway and every internal network by default, so no extra rules are needed.

### Build steps (UniFi Network app)

Each VLAN was created and tested before any device moved onto it.

1. **Settings → Networks → New Virtual Network**
2. **Name:** e.g. `Camera` · **Zone:** Internal · **VLAN ID:** `70`
3. **Gateway IP / subnet:** `10.0.70.1/24` (DHCP range filled in automatically)
4. **Isolate Network ✅** (on every VLAN except Default)
5. **Save**, then repeat for Kids (30), Gaming (40), Storage (50) and IoT (60)
6. **Guest (80):** same steps, but with **Zone: Hotspot**, which blocks guests from the gateway and every internal network

Camera was built first, so the discontinued-vendor cameras (the riskiest devices) were contained before anything else.

---

## Wired Port Assignments

| Device | Switch / Port | Native VLAN | Tagged VLANs |
|---|---|---|---|
| Lenovo ThinkCentre (Proxmox) | UDR7 Port 1 | Storage (50) | Allow All (VMs can be tagged onto other VLANs) |
| UGREEN NAS | UDR7 | Storage (50) | — |
| Raspberry Pi 4 | USW-Lite-8-PoE Port 8 | Storage (50) | Block All |
| Xbox Series X | USW-Lite-8-PoE | Gaming (40) | Block All |
| Work laptop | USW-Lite-8-PoE | IoT (60) | Block All |
| Beelink SER5 (Windows) | USW-Lite-8-PoE | Default | — |
| TP-Link Deco X68 (mesh, AP mode) | USW-Lite-8-PoE Port 4 | Default | — (move to Gaming planned) |

Least privilege on switch ports: end devices get **Block All** for tagged VLANs. Only the hypervisor gets **Allow All**, because it trunks VLANs to its virtual machines.

### Build steps (moving a wired device)

1. **UniFi Devices →** the switch (or UDR7) **→ Port Manager →** select the port
2. **Native VLAN / Network:** the target VLAN (e.g. `Gaming (40)`)
3. **Tagged VLAN Management:** **Block All** (Allow All only on the Proxmox port)
4. **Apply Changes**
5. Renew the device's address (unplug/replug or reboot), then confirm it got the new subnet in **Client Devices**
6. Test what the device needs, e.g. Xbox NAT type, or VPN and Microsoft 365 on the work laptop

Lesson: a device that also has WiFi can keep its old `192.168.1.x` lease (this happened with the Pi). Turn WiFi off on servers and reboot after a port change.

---

## WiFi Networks

| SSID purpose | Network | Bands | Security | Notes |
|---|---|---|---|---|
| Main (unchanged) | Default | 2.4 / 5 / 6 GHz | WPA2/WPA3 | Original SSID kept so nothing had to re-join |
| IoT | IoT (60) | **2.4 GHz only** | WPA2/WPA3 | MLO, band steering and fast roaming off for cheap IoT radios |
| Kids | Kids (30) | 2.4 / 5 GHz | WPA2/WPA3 | Band steering on |
| Guest | Guest (80) | **5 GHz only** | WPA2/WPA3 | Client Device Isolation on, no captive portal |

SSID names are intentionally left out of this repo.

### Build steps (new SSID)

![IoT WiFi settings](../images/13-iot-wifi-settings.jpg)

1. **Settings → WiFi → Create New**
2. **Name / Password:** a password generated and stored in the vault
3. **Network:** the target VLAN (IoT, Kids or Guest)
4. **Radio Band:** IoT **2.4 GHz** only · Kids 2.4 + 5 GHz · Guest **5 GHz** only
5. **Advanced → Manual:**
   - IoT: MLO off, Band Steering off, Fast Roaming (802.11r) off, so cheap IoT radios connect reliably
   - Guest: **Client Device Isolation ✅**, no Hotspot portal
6. **Security:** WPA2/WPA3
7. **Create**, then join with a phone and check the IP is in the right subnet (still pending for each SSID, see Testing)

**Constraint hit:** the APs reached the per-radio SSID limit on 2.4 GHz, so the Guest network was built as 5 GHz only. Keeping the SSID count low also saves airtime, since every SSID adds beacon overhead. Private Pre-Shared Keys (one SSID, one password per VLAN) is the next option if more segments are needed.

**Why 6 GHz isn't used on the extra SSIDs:** only the UDR7 has a 6 GHz radio and it sits in the basement rack, 6 GHz has the shortest range, and it requires WPA3, which many IoT and guest devices don't support.

---

## Testing

| Test | Expected | Result |
|---|---|---|
| Proxmox installer DHCP on UDR7 Port 1 | `10.0.50.x`, gateway `10.0.50.1` | ✅ `10.0.50.203` before switching to static |
| Xbox NAT type on Gaming VLAN | Open | ✅ |
| Work laptop on IoT | `10.0.60.x`, VPN and M365 work | ✅ |
| Browse to gateway admin page from an isolated VLAN | Blocked | ✅ |
| Each new SSID gets the right subnet and internet | Correct subnet, sites load | Pending |
