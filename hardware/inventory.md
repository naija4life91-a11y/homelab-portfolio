# Hardware Inventory & Build Cost

Every price below comes from an order confirmation, receipt, or "Purchased" record. Items without a receipt on file are marked.

![Full rack, door open](../images/06-full-rack-open.jpg)

---

## Purchase Log

### Networking

| Item | Model | Qty | Price | Store | Date |
|---|---|---|---|---|---|
| Router / gateway | UniFi Dream Router 7 (UDR7) | 1 | $279.00 | Ubiquiti Store (store.ui.com) | 2026 |
| Access points | UniFi U7 Lite | 2 | $198.00 ($99 ea) | Ubiquiti Store | 2026 |
| PoE switch | UniFi Switch Lite 8 PoE (USW-Lite-8-PoE) | 1 | $109.00 | Ubiquiti Store | 2026 |

> Ubiquiti order total: **$670.02** ($586.00 subtotal + $14.10 shipping + $32.00 memory surcharge + $37.92 tax)

### Storage

| Item | Model | Qty | Price | Store | Date |
|---|---|---|---|---|---|
| NAS | UGREEN NASync DXP4800 Plus (+ UPS bundle) | 1 | $689.70 (list $725.99, coupon −$36.29) | UGREEN (nas.ugreen.com) | 2026 |
| NAS drives | WD Red Plus 4TB (CMR, WD40EFZZ) | 2 | $288.78 ($144.39 ea) | Amazon | Jun 27, 2026 |

> UGREEN order total: **$731.08** (incl. $41.38 tax). WD order: $288.78 + $17.32 est. tax.

![NAS drive bays](../images/16-nas-drive-bays.jpg)

### Compute

| Item | Model | Qty | Price | Store | Date |
|---|---|---|---|---|---|
| Hypervisor | Lenovo ThinkCentre M80q Tiny (i7-10700T, 32GB, 256GB NVMe), used | 1 | $200.00 | Local private seller | 2026 |
| Mini PC (Windows) | Beelink SER5 | 1 | *price not on file* | Amazon | Nov 28, 2025 |
| SBC | Raspberry Pi 4 | 1 | *no receipt on file* | — | — |

### Rack, Power & Cooling

| Item | Model | Qty | Price | Store | Date |
|---|---|---|---|---|---|
| Server cabinet | SucceBuy 15U wall-mount server cabinet | 1 | $119.39 | AliExpress (SucceBuy store) | May 20, 2026 |
| PDU | 1U PDU, 10 individually switched outlets | 1 | $39.68 | AliExpress (SucceBuy store) | May 20, 2026 |
| UPS | CyberPower CP1500PFCRM2U (1500VA/1000W, pure sine, 2U) | 1 | $341.95 *(cart price — receipt not on file)* | Amazon | Jun 2026 |
| Rack fan | Tupavco TP1721 — 1U, 2 fans, 150 CFM, STC-1000 thermostat | 1 | $79.99 | Amazon | Jun 23, 2026 |
| Rack shelves | Pyle 1U server rack shelf, 8-pack | 1 | $62.99 | eBay | Jun 23, 2026 |

> AliExpress order total (cabinet + PDU): **$168.61**

### Cabling

| Item | Model | Qty | Price | Store | Date |
|---|---|---|---|---|---|
| Patch panel | Sokqovt 24-port Cat6, 1U, keystone | 1 | $32.99 | Amazon | Delivered Jun 8, 2026 |
| Patch cables | Sokqovt Cat6a slim patch cables, 24-pack | 1 | $14.99 | Amazon | Delivered Jun 6, 2026 |
| Patch cables | Sokqovt Cat6a slim patch cables, 24-pack | 1 | $21.80 | Amazon | Delivered Jun 6, 2026 |
| Short patch cables | Mnlnbuao Cat6 slim, 0.5 ft, 10-pack (blue) | 1 | $13.97 | eBay | Jun 23, 2026 |
| Long run | Jadaol Cat6, 100 ft outdoor | 1 | $25.02 | Amazon | Jun 25, 2026 |
| Long run | Jadaol Cat6, 35 ft outdoor | 1 | $11.30 | Amazon | Jun 2026 |
| Long run | XXONE Cat7, 100 ft outdoor | 1 | *price not on file* | Amazon | Jun 23, 2026 |
| Labels | Waterproof cable tags, 300 pcs, 10 colors | 1 | $8.47 | eBay | Jun 23, 2026 |

---

## Cost Summary

| Category | Item prices (pre-tax) |
|---|---|
| Networking | $586.00 |
| Storage | $978.48 |
| Compute (Lenovo) | $200.00 |
| Rack, power & cooling (excl. UPS) | $302.05 |
| Cabling | $128.54 |
| **Confirmed total** | **$2,195.07** |
| + CyberPower UPS (cart price) | $341.95 |
| **Estimated total with UPS** | **~$2,537.02** |

*Not included: Beelink SER5, Raspberry Pi 4, XXONE cable (no price on file), taxes and shipping except where noted.*

---

## Design Decisions

- **WD Red Plus (CMR), not WD Red (SMR)** — SMR drives perform poorly during RAID rebuilds.
- **Pure copper Cat6/Cat6a only** — avoided CCA (copper-clad aluminum) cable for PoE runs; CCA overheats and drops voltage under PoE load.
- **DXP4800 Plus over DXP4800 GT** — stronger Intel CPU and DDR5 matter more for a busy home network than the GT's second 10GbE port.
- **NVMe cache deferred** — SSD prices were inflated at time of build.
- **Used Lenovo Tiny as the hypervisor instead of upgrading the Beelink** — a RAM upgrade for the Beelink cost about $400; a used ThinkCentre with 32GB and an i7 cost $200 and keeps the Beelink free as a Windows PC. Checked before buying: no BIOS supervisor password, SSD health 97%, no corporate enrollment.

---

## Rack Layout (top → bottom)

![3D render of the rack](../images/24-rack-3d-render.jpg)

![Closed rack, front](../images/22-rack-closed-front.jpg)

![NAS, PDU and UPS](../images/04-nas-pdu-ups.jpg)

| Position | Device |
|---|---|
| Top 1U | Tupavco TP1721 thermostat fan (exhausts up, triggers at 77°F) |
| 1U | Sokqovt 24-port patch panel |
| Shelf | Beelink SER5, Raspberry Pi 4, USW-Lite-8-PoE |
| Shelf | UGREEN DXP4800 Plus NAS with the Lenovo ThinkCentre on top; Xfinity gateway (bridge mode) and UDR7 in front; TP-Link Deco X68 (mesh, AP mode) behind them |
| 1U | 10-outlet switched PDU (labeled: UGREEN NAS, Pi-4, Xbox, Mini PC, Cooling Fan, UniFi Switch, UniFi Dream Router) |
| 2U | CyberPower CP1500PFCRM2U UPS |
