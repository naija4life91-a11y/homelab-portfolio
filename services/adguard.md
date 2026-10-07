# AdGuard Home

## Status: ✅ Running (October 5, 2026): primary on Proxmox, rollout in progress

Network-wide DNS filter that blocks ads, trackers, phishing and malware domains before they resolve. The primary instance runs on Proxmox. For now only the admin laptop uses it, and the rest of the network moves over one VLAN at a time.

---

## Deployment

| Setting | Value |
|---|---|
| Host | Proxmox VE, LXC container **CT 101** |
| OS template | Debian 13 standard |
| Container type | Unprivileged, **nesting enabled**, start at boot |
| RAM | **2GB** (512MB ran out while loading about 3 million rules) |
| Network | `vmbr0`, no VLAN tag (Storage VLAN 50) |
| IP | `10.0.50.22/24` static, gateway `10.0.50.1`, also reserved in UniFi |
| Web UI | `http://10.0.50.22` (port 80) |
| DNS | Port 53, TCP and UDP |

- **Start at boot** matters more here than for any other guest. Once clients use AdGuard for DNS, a container that stays down after a host reboot takes the network's name resolution down with it.
- **Nesting** is required for Debian 13 containers even without Docker, because systemd 257 inside an unprivileged LXC needs it.

## Build Steps

### 1. Create the container (Proxmox web UI)
1. **Create CT** (top right)
2. **General:** CT ID `101`, hostname `adguard`, Unprivileged ✅, **Nesting ✅**, set a root password from the vault
3. **Template:** `debian-13-standard`
4. **Memory:** started at 512MB and later raised to **2048MB** (see Troubleshooting)
5. **Network:** bridge `vmbr0`, VLAN tag **blank** (the bridge's native VLAN is Storage), IPv4 **Static**, `10.0.50.22/24`, gateway `10.0.50.1`, IPv6 left blank
6. **Finish**, then **CT 101 → Options → Start at boot → Yes**, then **Start**
7. In UniFi, reserve `10.0.50.22` for the container's MAC

### 2. Install AdGuard Home (CT 101 console)
```bash
apt update && apt upgrade -y
apt install -y curl
curl -s -S -L https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts/install.sh | sh -s -- -v
```
The script installs AdGuard Home as a systemd service, so it starts with the container.

### 3. First-run wizard (`http://10.0.50.22:3000`)
1. **Admin web interface:** all interfaces, port **80**
2. **DNS server:** all interfaces, port **53**
3. **Admin account:** non-default username, vault-generated password
4. Log in again at `http://10.0.50.22`

### 4. Configure
1. **Settings → DNS settings → Upstream DNS servers:**
   ```
   https://dns.quad9.net/dns-query
   https://cloudflare-dns.com/dns-query
   ```
   Click **Test upstreams**, then **Apply**
2. **Filters → DNS blocklists → Add blocklist → Choose from the list:** HaGeZi Pro, Phishing URL Blocklist, HaGeZi Threat Intelligence Feeds (the AdGuard DNS filter is on by default)
3. **Settings → General settings:** Use AdGuard browsing security ✅, Query log retention **7 days**, Statistics retention **30 days**
4. Wait for the lists to load. This is where the 512MB container ran out of memory.

### 5. Monitor and test
1. Uptime Kuma: add a **DNS** monitor (resolver `10.0.50.22`, port 53, hostname `google.com`) and an **HTTP** monitor for `http://10.0.50.22`
2. Admin laptop: set its DNS to `10.0.50.22` by hand
3. Check the result: `nslookup doubleclick.net 10.0.50.22` returns `0.0.0.0`, and the laptop's queries appear in AdGuard's **Query Log**

## Upstream DNS

| Provider | Protocol | Why |
|---|---|---|
| Quad9 | DNS-over-HTTPS | Blocks known-malicious domains upstream, no-logging policy |
| Cloudflare | DNS-over-HTTPS | Fast second upstream |

DNS-over-HTTPS encrypts queries leaving the house, so the ISP can't read or tamper with them in transit.

## Blocklists

| List | Covers |
|---|---|
| AdGuard DNS filter | Ads and trackers (default list) |
| HaGeZi Pro | Ads, tracking, telemetry, with a low false-positive rate |
| Phishing URL Blocklist | Phishing domains |
| HaGeZi Threat Intelligence Feeds | Malware, command-and-control, cryptojacking and scam domains |

Together these lists hold about 3 million rules. **Browsing security** (AdGuard's own malware and phishing check) is also on.

## Logging

| Setting | Value | Why |
|---|---|---|
| Query log retention | 7 days | Long enough to troubleshoot a blocked site, short enough to limit how much browsing history sits on the server |
| Statistics retention | 30 days | Aggregated counts only, useful for trends |

## Security

- The web UI runs on the Storage VLAN. Isolated VLANs can't reach it, and the planned firewall rule opens **port 53 only**, never the admin UI.
- Monitored by Uptime Kuma: one check for DNS resolution and one for the web UI, with ntfy alerts to the phone
- No 2FA in AdGuard Home itself. Compensating controls: network isolation now, and Authelia behind a reverse proxy later.

---

## Troubleshooting During Setup

| Issue | Cause | Fix |
|---|---|---|
| Container ran out of memory while blocklists loaded | 512MB can't hold about 3 million rules | Raised RAM to 2GB |

---

## Rollout Plan

1. **Backup instance** on the Raspberry Pi 4 (`10.0.50.30`), so a Proxmox reboot doesn't take DNS down for the house
2. **Firewall:** allow TCP/UDP 53 from every VLAN to `10.0.50.22` and `10.0.50.30` only, placed above the block rules
3. **UniFi DHCP DNS:** point each network at `.22` (DNS 1) and `.30` (DNS 2), one network at a time, testing each before the next
4. **Kids VLAN (`10.0.30.0/24`):** per-client Safe Search and parental control

## Notes

- The UDR7 has no built-in ad blocking, which is why AdGuard Home is needed.
- Commands typed into the Pi's own terminal run on the Pi, not on Proxmox. The prompt (`<user>@raspberrypi` vs `root@pve`) shows which machine you're on.
