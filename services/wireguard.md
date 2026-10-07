# Remote Access: Tailscale (WireGuard as fallback)

## Status: Planned. Tailscale first, UDR7 WireGuard kept as the alternative

The first plan was a WireGuard server on the UDR7. The plan is now **Tailscale**, which is built on WireGuard, on a Proxmox container or the Pi.

---

## Why Tailscale over a UDR7 WireGuard server

| | UDR7 WireGuard | Tailscale |
|---|---|---|
| Open port on the WAN | Yes (UDP 51820) | **None**: outbound connections only |
| Works behind CGNAT / ISP changes | No | Yes |
| Access control | Whole VLANs | Per-device and per-port ACLs |
| Client login | Static key per device | SSO with 2FA, keys rotate |
| Dependency | None (self-hosted) | Tailscale coordination server |

No open ports means no attack surface for internet scanners. The trade-off is trusting Tailscale's coordination service. That's acceptable because traffic stays end-to-end encrypted with WireGuard, and the UDR7 WireGuard server stays a fallback if that trust changes.

---

## Planned Setup

1. Tailscale account with **2FA** on the identity provider
2. Small Debian LXC on Proxmox (Storage VLAN) running Tailscale as a **subnet router**, advertising only the subnets that need remote access
3. Approve the routes in the admin console. **Disable key expiry** only for the subnet router.
4. **ACLs:** phone and laptop can reach the admin UIs and the camera viewer only, nothing else
5. Install the client on the phone and laptop, then test from cellular with WiFi off
6. **Then:** block the discontinued cameras from the internet (see [firewall.md](../network/firewall.md)) and view them over Tailscale instead

## Notes

- Tailscale auth keys and node keys are never committed to this repo
- The fallback, if ever needed, is UniFi **Settings → VPN → VPN Server → WireGuard**, with a dedicated subnet and one client profile per device
