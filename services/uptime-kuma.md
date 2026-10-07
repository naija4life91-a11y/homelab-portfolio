# Uptime Kuma

## Status: ✅ Running (October 4, 2026)

Self-hosted uptime monitoring for the rack, with phone alerts. First service deployed on Proxmox.

![Uptime Kuma dashboard](../images/14-uptime-kuma-dashboard.jpg)

---

## Deployment

| Setting | Value |
|---|---|
| Host | Proxmox VE, LXC container **CT 100** (`uptime-kuma`) |
| OS template | Debian 13 standard |
| Container type | Unprivileged, **nesting enabled** (required for Docker) |
| Resources | 1 core, 1GB RAM, 512MB swap, 8GB disk |
| Network | `vmbr0`, no VLAN tag (Storage VLAN 50) |
| IP | `10.0.50.21/24` static, gateway `10.0.50.1`, also reserved in UniFi |
| Runtime | Docker, official convenience script |
| Image | `louislam/uptime-kuma:2` |
| Web UI | `http://10.0.50.21:3001` |
| Database | SQLite (single-file, plenty for a home lab) |

## Build Steps

### 1. Create the container (Proxmox web UI)
1. **Create CT**
2. **General:** CT ID `100`, hostname `uptime-kuma`, Unprivileged ✅, **Nesting ✅**, set a root password from the vault
3. **Template:** `debian-13-standard`
4. **Disks:** 8GB · **CPU:** 1 core · **Memory:** 1024MB, swap 512MB
5. **Network:** bridge `vmbr0`, VLAN tag blank, IPv4 **Static** `10.0.50.21/24`, gateway `10.0.50.1`, IPv6 blank
6. **Finish**, then **Start**. Reserve `10.0.50.21` in UniFi.

### 2. Install Docker and Uptime Kuma (CT 100 console)

```bash
apt update && apt upgrade -y
apt install -y curl
curl -fsSL https://get.docker.com | sh
docker pull louislam/uptime-kuma:2
docker run -d --restart=always -p 3001:3001 -v kuma:/app/data --name kuma louislam/uptime-kuma:2
```

- `--restart=always` brings it back after container or host reboots
- Data lives in the named volume `kuma`, so the container can be recreated or upgraded without losing history

### 3. First login and hardening (`http://10.0.50.21:3001`)
1. Select **SQLite** as the database
2. Create the admin account: non-default username, vault-generated password
3. **Settings → Security → Two Factor Authentication → Enable 2FA**, scan the QR code into the authenticator app, then confirm with a code

### 4. Phone alerts
1. Install the **ntfy** app on the phone and subscribe to a long random topic (the topic name stays in the vault, never in this repo)
2. **Settings → Notifications → Setup Notification:** type **ntfy**, server `https://ntfy.sh`, the same topic
3. Tick **Default enabled** and **Apply on all existing monitors**, then **Test** and **Save**

### 5. Monitors and test
1. **Add New Monitor** for each row in the [Monitors](#monitors) table
2. Unplug the Pi and check for a DOWN alert, then plug it back in and check for an UP alert

## Security

- Admin account uses a non-default username and a vault-generated password
- Two-factor authentication enabled
- Reachable only from the trusted network and the Storage VLAN; isolated VLANs (Kids, IoT, Guest, etc.) cannot reach it

---

## Monitors

| Monitor | Type | Target | Interval / retries |
|---|---|---|---|
| UDR7 Gateway | Ping | `10.0.50.1` | 60s / 2 |
| Proxmox | HTTP(s) | `https://10.0.50.20:8006` (self-signed cert ignored) | 60s / 2 |
| Pi 4 | Ping | `10.0.50.30` | 60s / 2 |
| UGREEN NAS | Ping | NAS on Storage VLAN | 60s / 2 |
| Internet (Xfinity) | Ping | `1.1.1.1` | 60s / 2 |
| Web (Google) | HTTP(s) | `https://www.google.com` | 120s / 2 |
| AdGuard DNS | DNS | resolver `10.0.50.22`, port 53 | added Oct 5 |
| AdGuard web UI | HTTP(s) | `http://10.0.50.22` | added Oct 5 |

Two retries mean a single dropped packet doesn't page me; a device has to fail three checks in a row.

## Alerting

- Push notifications through the **ntfy** app on a long, random, non-guessable topic (topic name kept out of this repo)
- Applied to every monitor by default

### Test

Unplugged the Pi 4's network cable: a **DOWN** alert arrived on the phone within a few minutes, and an **UP** alert arrived after reconnecting. The Pi's bar shows the outage (orange/red) and recovery.

---

## Troubleshooting During Setup

| Issue | Cause | Fix |
|---|---|---|
| Browser: "Unable to connect" on port 3001 | Network fine, but no container running (`docker ps -a` empty) | Ran the `docker run` command |
| `'docker run' requires at least 1 argument` | Long command cut off mid-line | Pulled the image separately, then ran a shorter command |
| LXC network form error-prone | Gateway entered in the IP field, IPv4 address in the IPv6 gateway | Container IP in IPv4/CIDR, router in Gateway, IPv6 left blank |

## Limitation / Next Step

Storage is an isolated VLAN, so Uptime Kuma can't reach the switch, APs, or devices on other VLANs. A narrow firewall policy allowing only `10.0.50.21` to ping those networks would let them be monitored without opening anything else.
