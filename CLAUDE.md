# CLAUDE.md: Homelab context

Read this first. It is the current state of the homelab and the rules for working in this repo. Update the **Current state** and **Next up** sections whenever something changes.

## About this repo

- Private portfolio and build journal for a segmented home network and Proxmox homelab in a basement 15U rack.
- Owner holds Security+, CEH, CySA+. Write docs that show security reasoning (why, not just what): least privilege, risk decisions, compensating controls, what broke and how it was fixed.
- The owner works step by step from screenshots, often on a phone. When guiding, give short numbered steps with exact field values.

## Rules

1. **Never commit secrets.** No passwords, recovery codes or keys, API tokens, Tailscale/WireGuard keys, ntfy topic names, public IP addresses, WiFi SSID names, or personal names and addresses. If one shows up in a screenshot, crop or blur it before adding it.
2. Images go in `images/` with the next number prefix (`16-...jpg`), resized to about 1400px on the long edge.
3. Every change gets a dated entry in `logs/build-log.md`. Add to its **Issues & Resolutions** table when something broke.
4. Each service gets its own page in `services/` (deployment table, security, troubleshooting). Link it from `README.md` and from the table in `services/proxmox.md`.
5. Keep `README.md`'s **Current Status** table and this file's **Current state** in sync.
6. Design defaults: least privilege (end-device switch ports use **Block All** tagged VLANs), isolated VLANs, explicit allow rules placed above block rules, 2FA on every admin login.

## Current state (as of Oct 6, 2026)

### Network: UniFi Dream Router 7 + USW-Lite-8-PoE + 2x U7 Lite
| VLAN | Name | Subnet | Notes |
|---|---|---|---|
| 1 | Default (trusted) | 192.168.1.0/24 | Admin network; UDR7 at .1 |
| 30 | Kids | 10.0.30.0/24 | Isolated |
| 40 | Gaming | 10.0.40.0/24 | Isolated; Xbox (UPnP on, Open NAT) |
| 50 | Storage / Servers | 10.0.50.0/24 | Isolated; servers live here |
| 60 | IoT | 10.0.60.0/24 | Isolated; smart devices + employer-managed work laptop |
| 70 | Camera | 10.0.70.0/24 | Isolated; IP cameras, doorbell |
| 80 | Guest | Hotspot zone | 5 GHz only, client isolation, no portal |

### Firewall policies
- Allow Default → Camera, Default → Storage, Default → IoT
- Block Kids/Gaming/IoT/Camera → Gateway on TCP 22/80/443 (DNS/DHCP/NTP left open)
- UPnP for Default + Gaming only, Secure Mode on. IPS in Notify and Block, all categories.

### Storage VLAN hosts (all IPs reserved in UniFi)
| Host | IP | What |
|---|---|---|
| UDR7 gateway | 10.0.50.1 | Router interface |
| Proxmox VE 9.2 | 10.0.50.20 | Lenovo ThinkCentre M80q, i7-10700T, 32GB, 256GB NVMe. UDR7 Port 1, native VLAN 50, tagged Allow All. `vmbr0` is VLAN aware. No-subscription repo, updated, root TOTP 2FA (recovery keys in password vault) |
| Uptime Kuma | 10.0.50.21 | LXC CT 100, Debian 13 + Docker, `louislam/uptime-kuma:2`, port 3001, SQLite, ntfy phone alerts, 2FA. Monitors: gateway, Proxmox, Pi, NAS, internet, web, AdGuard DNS + web UI |
| AdGuard Home | 10.0.50.22 | LXC CT 101, Debian 13, **2 GB RAM** (512 MB ran out loading ~3M rules), nesting on, start at boot. Web UI http://10.0.50.22 (port 80), DNS 53. Upstreams Quad9 + Cloudflare DoH. Lists: AdGuard DNS filter, HaGeZi Pro, Phishing URL, HaGeZi Threat Intelligence Feeds. Browsing security on. Log 7d, stats 30d. **Only the admin laptop uses it so far.** |
| Raspberry Pi 4 | 10.0.50.30 | Rack admin workstation; WiFi off; future backup AdGuard DNS |
| UGREEN DXP4800 Plus NAS | 10.0.50.x (reserved) | 3 of 4 WD Red Plus 4TB installed; one drive on RMA; RAID 5 pending |

### Proxmox guests
- Guest on Storage: leave the VLAN tag blank. Guest on IoT: VLAN tag 60.
- Next free IP: 10.0.50.23 and up.
- Debian 13 LXCs need **nesting** enabled (systemd 257), even without Docker.
- Size RAM for the workload: DNS blocklists in the millions of rules need 1–2 GB.

### Other hardware
- Beelink SER5: Windows PC on Default (not a server)
- CyberPower CP1500 UPS, 10-outlet switched PDU, Tupavco thermostat fan (77°F)
- TP-Link Deco X68 mesh in AP mode on Default (move to Gaming later)

## Known limitations
- Storage is isolated, so Uptime Kuma can't reach devices on other VLANs. That needs a narrow allow rule for 10.0.50.21 only.
- The discontinued camera vendor's cameras still use their cloud for remote viewing. Cut them off from the internet once a self-hosted VPN is in place.

## Next up (in order)
1. **AdGuard rollout**: backup AdGuard on the Pi (10.0.50.30), firewall allow TCP/UDP 53 from all VLANs to .22 and .30, point UniFi DNS at them one network at a time, then per-client Safe Search + parental control for Kids (10.0.30.0/24)
2. **Tailscale**: remote access with no open ports; then block the discontinued cameras from the internet
3. Move smart devices to the IoT SSID and kids' devices to the Kids SSID
4. NAS RAID 5 when the replacement drive arrives, then Proxmox backups to the NAS
5. Home Assistant (IoT VLAN), Vaultwarden, Portainer, CrowdSec, **Wazuh SIEM** (8GB VM, ingests UniFi syslog)
6. Move the Deco mesh to Gaming, then drop Default from UPnP
7. Reverse proxy (Nginx Proxy Manager or Caddy) + Let's Encrypt DNS challenge for HTTPS on AdGuard/Uptime Kuma/Proxmox; Authelia for 2FA on apps without it
