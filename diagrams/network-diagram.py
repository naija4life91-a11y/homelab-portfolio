#!/usr/bin/env python3
"""Generate diagrams/network-diagram.svg (current + planned network).

Run: python3 diagrams/network-diagram.py
Keep it free of secrets: no public IPs, SSID names, MACs or keys.
"""
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1600, 1200
FONT = "Segoe UI, Helvetica, Arial, sans-serif"
C = {  # VLAN colors
    "Default": "#60a5fa", "Kids": "#fbbf24", "Gaming": "#c084fc", "Storage": "#2dd4bf",
    "IoT": "#fb923c", "Camera": "#f472b6", "Guest": "#94a3b8",
}
ALLOW, BLOCK, PLAN, TXT, SUB, CARD, EDGE = "#4ade80", "#f87171", "#a5b4fc", "#e6edf3", "#9fb0c3", "#161d29", "#2a3a55"
out = []


def t(x, y, s, size=14, fill=TXT, weight=400, anchor="start", italic=False):
    st = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
               f'text-anchor="{anchor}"{st}>{escape(s)}</text>')


def rect(x, y, w, h, stroke=EDGE, fill=CARD, r=10, dash=False, sw=1.5):
    d = ' stroke-dasharray="6 5"' if dash else ""
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(pts, color=EDGE, w=2, dash=False, arrow=None):
    d = ' stroke-dasharray="7 6"' if dash else ""
    m = f' marker-end="url(#{arrow})"' if arrow else ""
    p = " ".join(f"{x},{y}" for x, y in pts)
    out.append(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{w}"{d}{m}/>')


def node(x, y, w, h, title, lines=(), vlan=None, dash=False, tsize=15):
    rect(x, y, w, h, stroke=PLAN if dash else EDGE, dash=dash)
    if vlan:
        out.append(f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{C[vlan]}"/>')
    t(x + 16, y + 24, title, tsize, TXT, 600)
    for i, s in enumerate(lines):
        t(x + 16, y + 44 + i * 18, s, 12.5, SUB)


def chip(x, y, label, color):
    w = 7.2 * len(label) + 18
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="1"/>')
    t(x + w / 2, y + 15.5, label, 11.5, color, 600, "middle")
    return w


# ---------- header ----------
t(40, 52, "Home Network · Segmented by Trust", 30, "#ffffff", 700)
t(40, 80, "UniFi zone-based firewall · 7 networks · servers isolated on VLAN 50 · dashed = planned", 15, "#7aa2d6")

# ---------- left: physical path ----------
node(40, 110, 250, 56, "Internet", ["ISP: cable, DHCPv4"])
node(310, 110, 250, 56, "ISP gateway", ["Bridge mode (no double NAT)"])
line([(290, 138), (310, 138)], SUB)
line([(435, 166), (435, 196)], SUB, arrow="a_sub")
node(40, 196, 520, 112, "UniFi Dream Router 7  ·  gateway + zone firewall", [
    "WAN on port 4 (2.5GbE) · DHCP for every VLAN · 192.168.1.1",
    "IPS: Notify and Block, 13/13 categories",
    "UPnP: Default + Gaming only, Secure Mode on",
])
# branches
line([(110, 308), (110, 350)], SUB, 2)
line([(300, 308), (300, 350)], SUB, 2)
line([(480, 308), (480, 708)], SUB, 2)
t(118, 336, "Port 1 · trunk", 11.5, SUB, italic=True)
t(308, 336, "LAN", 11.5, SUB, italic=True)
t(488, 336, "uplink", 11.5, SUB, italic=True)

# Proxmox host with guests
rect(40, 350, 230, 340, stroke=C["Storage"])
out.append(f'<rect x="40" y="350" width="6" height="340" rx="3" fill="{C["Storage"]}"/>')
t(56, 374, "Proxmox VE 9.2", 15, TXT, 600)
t(56, 392, "Lenovo M80q · 10.0.50.20", 12.5, SUB)
t(56, 409, "native 50 · tagged all · root 2FA", 12.5, SUB)
guests = [
    ("CT 100 · Uptime Kuma", "10.0.50.21 · ntfy alerts", False),
    ("CT 101 · AdGuard Home", "10.0.50.22 · DNS filter", False),
    ("Home Assistant VM", "IoT VLAN 60 (tag 60)", True),
    ("Vaultwarden · Portainer", "Storage VLAN", True),
    ("Wazuh SIEM VM", "8 GB · UniFi syslog", True),
]
for i, (a, b, planned) in enumerate(guests):
    y = 424 + i * 52
    rect(56, y, 200, 44, stroke=PLAN if planned else EDGE, fill="#101722", r=7, dash=planned)
    t(66, y + 18, a, 12.5, TXT, 600)
    t(66, y + 35, b, 11.5, SUB)

node(290, 350, 170, 110, "UGREEN NAS", ["DXP4800 Plus", "VLAN 50 · reserved IP", "RAID 5 pending (RMA)"], "Storage")
node(290, 476, 170, 92, "Planned on NAS", ["Proxmox backups", "after RAID 5"], dash=True)

# switch + clients
node(40, 708, 520, 70, "USW-Lite-8-PoE  ·  end-device ports: Block All tagged VLANs", ["Least privilege: only the Proxmox port carries tagged VLANs"])
clients = [
    ("U7 Lite · Basement", "PoE · WiFi 7", None), ("U7 Lite · Main floor", "PoE · WiFi 7", None),
    ("Raspberry Pi 4", "10.0.50.30 · WiFi off", "Storage"), ("Xbox Series X", "Open NAT", "Gaming"),
    ("Work laptop", "Employer-managed", "IoT"), ("Beelink SER5", "Windows PC", "Default"),
    ("Deco X68 (AP mode)", "PS5 via satellite", "Default"),
]
line([(300, 778), (300, 796)], SUB, 2)
rect(40, 796, 520, 222, stroke=EDGE, fill="#0f1520", r=12)
t(52, 813, "Switch ports", 11.5, SUB, italic=True)
cw, ch = 158, 56
for i, (a, b, v) in enumerate(clients):
    col, row = i % 3, i // 3
    x, y = 52 + col * (cw + 8), 822 + row * (ch + 10)
    node(x, y, cw, ch, a, [b], v, tsize=13.5)

# ---------- right: VLANs ----------
X0 = 620
t(X0, 128, "Networks & firewall policy", 19, "#ffffff", 700)
rect(X0, 142, 940, 104, stroke=C["Default"])
out.append(f'<rect x="{X0}" y="142" width="6" height="104" rx="3" fill="{C["Default"]}"/>')
t(X0 + 18, 168, "VLAN 1 · Default (trusted / admin)", 16, TXT, 700)
t(X0 + 18, 190, "192.168.1.0/24 · admin laptop, family phones and laptops, Beelink, Deco mesh", 13, SUB)
t(X0 + 18, 210, "Only network allowed to start connections into other VLANs · reaches the UDR7 admin UI", 13, SUB)
chip(X0 + 18, 218, "Main WiFi: 2.4 / 5 / 6 GHz", C["Default"])

cards = [
    ("Storage", 50, "10.0.50.0/24", ["Proxmox .20 · Kuma .21 · AdGuard .22", "Pi 4 .30 · NAS · static reservations"], True),
    ("IoT", 60, "10.0.60.0/24", ["Smart devices, work laptop", "IoT WiFi: 2.4 GHz only, MLO off"], True),
    ("Camera", 70, "10.0.70.0/24", ["IP cameras, video doorbell", "Vendor discontinued: risk accepted"], True),
    ("Kids", 30, "10.0.30.0/24", ["Kids' phones, tablets, consoles", "Kids WiFi · parental control planned"], False),
    ("Gaming", 40, "10.0.40.0/24", ["Xbox Series X (wired)", "UPnP + Secure Mode → Open NAT"], False),
    ("Guest", 80, "Hotspot zone", ["5 GHz only · client isolation", "No captive portal"], False),
]
cw2, ch2, gx = 300, 132, 20
for i, (name, vid, net, lines_, allowed) in enumerate(cards):
    col, row = i % 3, i // 3
    x, y = X0 + col * (cw2 + gx), 318 + row * (ch2 + 36)
    rect(x, y, cw2, ch2, stroke=C[name])
    out.append(f'<rect x="{x}" y="{y}" width="6" height="{ch2}" rx="3" fill="{C[name]}"/>')
    t(x + 18, y + 26, f"VLAN {vid} · {name}", 16, TXT, 700)
    t(x + 18, y + 46, net, 13, C[name], 600)
    for j, s in enumerate(lines_):
        t(x + 18, y + 68 + j * 18, s, 12.5, SUB)
    chip(x + 18, y + ch2 - 30, "Isolated", "#94a3b8")
    if name != "Guest":
        chip(x + 96, y + ch2 - 30, "No gateway admin", BLOCK)
    else:
        chip(x + 96, y + ch2 - 30, "No internal access", BLOCK)
    if allowed:
        cx = x + cw2 / 2
        line([(cx, 246), (cx, y - 4)], ALLOW, 2.5, arrow="a_allow")
t(X0 + 2, 286, "", 1)
for i, lbl in enumerate(["Allow Default → Storage", "Allow Default → IoT", "Allow Default → Camera"]):
    t(X0 + i * (cw2 + gx) + cw2 / 2 + 8, 284, lbl, 12, ALLOW, 600)

# block rule banner
rect(X0, 636, 940, 46, stroke=BLOCK, fill="#2a1518")
t(X0 + 18, 664, "Block  Kids · Gaming · IoT · Camera  →  Gateway  TCP 22 / 80 / 443", 15, BLOCK, 700)
t(X0 + 590, 664, "DNS 53 · DHCP 67/68 · NTP 123 stay open", 13, "#fca5a5")

# planned
rect(X0, 700, 940, 240, stroke=PLAN, dash=True, fill="#121828")
t(X0 + 18, 728, "Planned next (in order)", 17, PLAN, 700)
plans = [
    ("1", "AdGuard rollout", "Backup on Pi (.30) · allow TCP/UDP 53 from every VLAN to .22 + .30 only · switch DHCP DNS one VLAN at a time"),
    ("2", "Tailscale", "Subnet router, no open ports · then block the discontinued cameras from the internet"),
    ("3", "Wi-Fi moves", "Smart devices → IoT SSID · kids' devices → Kids SSID"),
    ("4", "NAS RAID 5", "When the RMA drive arrives · Proxmox backups to the NAS"),
    ("5", "More services", "Home Assistant (IoT), Vaultwarden, Portainer, CrowdSec, Wazuh SIEM"),
    ("6", "Tidy UPnP", "Deco mesh → Gaming, then drop Default from UPnP"),
    ("7", "HTTPS everywhere", "Reverse proxy + Let's Encrypt DNS challenge · Authelia 2FA"),
]
for i, (n, a, b) in enumerate(plans):
    y = 754 + i * 27
    out.append(f'<circle cx="{X0 + 30}" cy="{y + 2}" r="10" fill="none" stroke="{PLAN}" stroke-width="1.5"/>')
    t(X0 + 30, y + 6.5, n, 11.5, PLAN, 700, "middle")
    t(X0 + 50, y + 7, a, 13.5, TXT, 700)
    t(X0 + 200, y + 7, b, 12.5, SUB)

# legend
ly = 1056
t(40, ly - 8, "Legend", 15, "#ffffff", 700)
line([(40, ly + 14), (90, ly + 14)], SUB, 2); t(100, ly + 19, "Wired / trunk", 13, SUB)
line([(240, ly + 14), (290, ly + 14)], ALLOW, 2.5, arrow="a_allow"); t(304, ly + 19, "Allow policy (Default only)", 13, SUB)
line([(520, ly + 14), (570, ly + 14)], PLAN, 2, dash=True); t(580, ly + 19, "Planned", 13, SUB)
x = 680
for name in ["Default", "Kids", "Gaming", "Storage", "IoT", "Camera", "Guest"]:
    out.append(f'<rect x="{x}" y="{ly + 6}" width="14" height="14" rx="3" fill="{C[name]}"/>')
    t(x + 20, ly + 18, name, 13, SUB)
    x += 34 + 7.5 * len(name)
t(40, ly + 60, "Return traffic is allowed automatically, so an isolated device can answer a connection but never start one. "
  "Every admin login uses 2FA.", 13, SUB, italic=True)
t(40, ly + 82, "No public IPs, SSID names, MAC addresses or keys appear in this diagram.", 12, "#6b7d95", italic=True)

defs = f'''<defs>
<marker id="a_allow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{ALLOW}"/></marker>
<marker id="a_sub" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{SUB}"/></marker>
<radialGradient id="bg" cx="50%" cy="35%" r="75%"><stop offset="0" stop-color="#18202d"/><stop offset="1" stop-color="#0b0f17"/></radialGradient>
</defs>'''
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">'
       f'{defs}<rect width="{W}" height="{H}" rx="16" fill="url(#bg)"/>' + "".join(out) + "</svg>")
Path(__file__).with_name("network-diagram.svg").write_text(svg)
print("wrote network-diagram.svg")
