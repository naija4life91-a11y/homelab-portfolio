# Docker & Portainer

## Status: Docker in use per container · Portainer planned

The original plan was one Docker host on the Beelink running every service. That changed when the Lenovo ThinkCentre became the Proxmox host. Each service now gets **its own LXC container**, and Docker is installed only inside the containers that need it.

| Service | How it runs | Docker? |
|---|---|---|
| Uptime Kuma | LXC CT 100, Docker inside | ✅ `louislam/uptime-kuma:2`: see [uptime-kuma.md](uptime-kuma.md) |
| AdGuard Home | LXC CT 101, native install | ❌ Not needed: see [adguard.md](adguard.md) |
| Portainer | LXC, planned | ✅ |
| Vaultwarden | LXC, planned | ✅ |
| Home Assistant | VM on IoT VLAN, planned | ❌ (Home Assistant OS) |

**Why one container per service:** a compromised or broken service can't reach the others' files, each one can be backed up, restored or rolled back on its own in Proxmox, and RAM is sized per workload.

---

## Docker inside a Debian 13 LXC

The container needs **Nesting ✅** (Proxmox → CT → Options → Features).

```bash
apt update && apt upgrade -y
apt install -y curl
curl -fsSL https://get.docker.com | sh
docker --version
```

Containers run as root inside an **unprivileged** LXC, so root in the container is not root on the Proxmox host.

---

## Portainer (planned)

```bash
docker volume create portainer_data
docker run -d \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:lts
```

- HTTPS UI on 9443. The old HTTP port 9000 and the 8000 edge-agent port are not exposed.
- Mounting `docker.sock` gives Portainer full control of Docker in that container, so the admin login gets a vault password and is reachable from the trusted network only.

## Notes

- Every container uses `--restart=always` and named volumes, so data survives upgrades.
