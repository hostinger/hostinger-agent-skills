---
name: vps
description: Hostinger VPS API for virtual machine management, Docker projects, firewalls, SSH keys, backups, snapshots, OS templates, post-install scripts, recovery mode, malware scanning, PTR records, and metrics. Use when creating, managing, or troubleshooting VPS instances, deploying Docker containers, configuring firewalls, or managing server infrastructure.
last_updated: "2026-03-20"
doc_source: https://developers.hostinger.com
---

# Hostinger VPS

The VPS API provides comprehensive management of virtual private servers — from purchasing and setup to Docker deployments, firewall configuration, SSH keys, backups, snapshots, OS reinstallation, recovery mode, malware scanning, and performance monitoring.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Virtual Machines

VPS instances with dedicated CPU, RAM, disk, and network resources. Each VM has an OS template, root access, and an IP address. VMs go through states: `initial` → `running` → `stopped`.

### Actions

Asynchronous operations on VMs (start, stop, restart, recreate, etc.) return an action resource with a status you can poll.

### Docker Manager

Deploy and manage Docker Compose projects directly on VPS instances. Supports creating projects from `docker-compose.yaml` content or GitHub URLs.

### Firewalls

Network security rules that control inbound traffic. By default, all incoming traffic is dropped — you must explicitly add accept rules. Only one firewall can be active per VM at a time. Changes require manual sync to take effect.

### SSH Public Keys

SSH keys for authentication. Keys are managed at the account level and attached to specific VMs.

### OS Templates

Pre-configured operating system images for VM installation (Ubuntu, Debian, CentOS, etc.) including panel templates (e.g., with cPanel or Plesk).

### Post-Install Scripts

Automation scripts that run after VM installation. Saved to `/post_install` with executable permissions. Output goes to `/post_install.log`. Maximum size: 48KB.

### Backups & Snapshots

- **Backups**: Automatic periodic backups managed by Hostinger
- **Snapshots**: User-initiated point-in-time captures. Only one snapshot per VM — creating a new one overwrites the existing one

### Recovery Mode

Boot the VM from a recovery disk image for system rescue. The original disk is mounted at `/mnt`.

### Malware Scanner (Monarx)

Optional security tool for malware detection and prevention on VPS instances.

## Common Patterns

### Purchase and Setup a VPS

```bash
# Step 1: Get available OS templates
curl -X GET "https://developers.hostinger.com/api/vps/v1/templates" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 2: Get available data centers
curl -X GET "https://developers.hostinger.com/api/vps/v1/data-centers" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 3: Purchase a VPS
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": "hostingercom-vps-kvm2-usd-1m",
    "payment_method_id": 517244,
    "template_id": 1,
    "data_center_id": 1,
    "hostname": "my-server",
    "password": "SecurePass123!"
  }'

# Step 4: Setup purchased VM (if in initial state)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/setup" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "data_center_id": 1,
    "hostname": "my-server",
    "password": "SecurePass123!"
  }'
```

**CLI (hapi):**

```bash
hapi vps vm list
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

# List all VPS instances
vms = client.vps.virtual_machines.list()
for vm in vms:
    print(f"{vm.hostname} - {vm.state} - {vm.ip_address}")
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const vms = await client.vps.virtualMachines.list();
for (const vm of vms) {
  console.log(`${vm.hostname} - ${vm.state} - ${vm.ipAddress}`);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$vms = $client->vps->virtualMachines->list();
foreach ($vms as $vm) {
    echo "{$vm->hostname} - {$vm->state} - {$vm->ip_address}\n";
}
```

### VM Lifecycle Operations

```bash
# List all VMs
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Get VM details
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Start VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/start" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Stop VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/stop" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Restart VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/restart" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Set hostname
curl -X PUT "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/hostname" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "hostname": "new-hostname.example.com" }'

# Set root password
curl -X PUT "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/root-password" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "password": "NewSecurePass123!" }'

# Recreate VM (DESTRUCTIVE - all data lost)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/recreate" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "password": "SecurePass123!"
  }'
```

### Deploy Docker Compose Projects

```bash
# List Docker projects on a VM
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Deploy from docker-compose.yaml content
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-app",
    "content": "version: \"3\"\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - \"80:80\""
  }'

# Deploy from GitHub URL
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-app",
    "url": "https://github.com/user/repo"
  }'

# Get project containers and stats
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/my-app/containers" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# View project logs (last 300 entries)
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/my-app/logs" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Start / Stop / Restart / Update / Delete project
curl -X POST ".../docker/my-app/start" -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
curl -X POST ".../docker/my-app/stop" -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
curl -X POST ".../docker/my-app/restart" -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
curl -X POST ".../docker/my-app/update" -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
curl -X DELETE ".../docker/my-app/down" -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Configure Firewalls

```bash
# Create a firewall
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "name": "web-server" }'

# Add rules (default drops all — add accept rules for ports you need)
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "tcp",
    "port": "80",
    "source": "0.0.0.0/0",
    "action": "accept"
  }'

# Activate firewall on a VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/activate/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Sync firewall after rule changes
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/sync/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### SSH Key Management

```bash
# Create SSH key
curl -X POST "https://developers.hostinger.com/api/vps/v1/public-keys" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-laptop",
    "key": "ssh-ed25519 AAAA... user@host"
  }'

# Attach key to VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/public-keys/attach/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "ids": [1, 2] }'

# List keys on a VM
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/public-keys" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Backups and Snapshots

```bash
# List backups
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/backups" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Restore a backup (DESTRUCTIVE - overwrites all data)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/backups/99/restore" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Create a snapshot (overwrites existing snapshot)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/snapshot" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Get current snapshot
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/snapshot" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Restore from snapshot
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/snapshot/restore" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Monitor Performance

```bash
# Get VM metrics (CPU, memory, disk, network, uptime)
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/metrics?date_from=2025-05-01T00:00:00Z&date_to=2025-06-01T00:00:00Z" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## API Reference

### Virtual Machines

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/vps/v1/virtual-machines` | List all VMs |
| `POST` | `/api/vps/v1/virtual-machines` | Purchase new VM |
| `GET` | `/api/vps/v1/virtual-machines/{id}` | Get VM details |
| `POST` | `/api/vps/v1/virtual-machines/{id}/setup` | Setup purchased VM |
| `POST` | `/api/vps/v1/virtual-machines/{id}/start` | Start VM |
| `POST` | `/api/vps/v1/virtual-machines/{id}/stop` | Stop VM |
| `POST` | `/api/vps/v1/virtual-machines/{id}/restart` | Restart VM |
| `POST` | `/api/vps/v1/virtual-machines/{id}/recreate` | Recreate VM (destructive) |
| `PUT` | `/api/vps/v1/virtual-machines/{id}/hostname` | Set hostname |
| `DELETE` | `/api/vps/v1/virtual-machines/{id}/hostname` | Reset hostname |
| `PUT` | `/api/vps/v1/virtual-machines/{id}/root-password` | Set root password |
| `PUT` | `/api/vps/v1/virtual-machines/{id}/panel-password` | Set panel password |
| `PUT` | `/api/vps/v1/virtual-machines/{id}/nameservers` | Set nameservers |
| `GET` | `/api/vps/v1/virtual-machines/{id}/metrics` | Get metrics |
| `GET` | `/api/vps/v1/virtual-machines/{id}/public-keys` | Get attached SSH keys |
| `GET` | `/api/vps/v1/virtual-machines/{id}/actions` | Get action history |
| `GET` | `/api/vps/v1/virtual-machines/{id}/actions/{actionId}` | Get action details |

### Docker Manager (experimental)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `.../docker` | List projects |
| `POST` | `.../docker` | Create project |
| `GET` | `.../docker/{name}` | Get project contents |
| `GET` | `.../docker/{name}/containers` | Get containers with stats |
| `GET` | `.../docker/{name}/logs` | Get project logs (last 300) |
| `POST` | `.../docker/{name}/start` | Start project |
| `POST` | `.../docker/{name}/stop` | Stop project |
| `POST` | `.../docker/{name}/restart` | Restart project |
| `POST` | `.../docker/{name}/update` | Update project |
| `DELETE` | `.../docker/{name}/down` | Delete project (irreversible) |

### Firewall

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/vps/v1/firewall` | List firewalls |
| `POST` | `/api/vps/v1/firewall` | Create firewall |
| `GET` | `/api/vps/v1/firewall/{id}` | Get firewall details |
| `DELETE` | `/api/vps/v1/firewall/{id}` | Delete firewall |
| `POST` | `/api/vps/v1/firewall/{id}/rules` | Create rule |
| `PUT` | `/api/vps/v1/firewall/{id}/rules/{ruleId}` | Update rule |
| `DELETE` | `/api/vps/v1/firewall/{id}/rules/{ruleId}` | Delete rule |
| `POST` | `/api/vps/v1/firewall/{id}/activate/{vmId}` | Activate on VM |
| `POST` | `/api/vps/v1/firewall/{id}/deactivate/{vmId}` | Deactivate on VM |
| `POST` | `/api/vps/v1/firewall/{id}/sync/{vmId}` | Sync rules to VM |

### SSH Keys, Templates, Scripts, Backups, Snapshots, Recovery, PTR, Malware

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST/DELETE` | `/api/vps/v1/public-keys` | Manage SSH keys |
| `POST` | `/api/vps/v1/public-keys/attach/{vmId}` | Attach keys to VM |
| `GET` | `/api/vps/v1/templates` | List OS templates |
| `GET` | `/api/vps/v1/templates/{id}` | Get template details |
| `GET/POST/PUT/DELETE` | `/api/vps/v1/post-install-scripts` | Manage scripts |
| `GET` | `/api/vps/v1/data-centers` | List data centers |
| `GET` | `.../backups` | List backups |
| `POST` | `.../backups/{id}/restore` | Restore backup |
| `GET/POST/DELETE` | `.../snapshot` | Manage snapshot |
| `POST` | `.../snapshot/restore` | Restore snapshot |
| `POST/DELETE` | `.../recovery` | Start/stop recovery mode |
| `POST/DELETE` | `.../ptr/{ipId}` | Manage PTR records |
| `GET/POST/DELETE` | `.../monarx` | Manage malware scanner |

## Best Practices

### Security
- Always attach SSH keys and disable password auth when possible
- Configure firewalls — default drops all traffic, add only needed ports
- **Sync firewalls** after any rule change — changes don't auto-apply
- Only one firewall per VM — plan rules in a single firewall
- Install Monarx malware scanner on production servers
- Use strong passwords (12+ chars, mixed case, numbers, not leaked)

### Backups & Recovery
- Take a **snapshot before** destructive operations (recreate, major changes)
- Remember: creating a new snapshot **overwrites** the existing one
- Backup restores **overwrite all data** on the VM
- Use recovery mode for filesystem repair — original disk is at `/mnt`

### Docker
- Docker Manager endpoints are **experimental** — expect changes
- GitHub URLs auto-resolve to `docker-compose.yaml` in master branch
- Deploying a project with an existing name **replaces** it
- Use logs endpoint for debugging container issues

### Performance
- Monitor metrics to right-size your VPS plan
- Set custom nameservers only if you know what you're doing — wrong config breaks DNS resolution

### Post-Install Scripts
- Maximum script size: 48KB
- Script runs as `/post_install`, output goes to `/post_install.log`
- Test scripts on non-production VMs first

## Troubleshooting

### VM Not Starting
- Check action history for error details
- VM may be in recovery mode — stop recovery first
- Check if VM is in `initial` state — run setup first

### Cannot SSH Into VM
- Verify SSH key is attached (not just in account)
- Check firewall allows port 22
- Verify firewall is synced after rule changes
- Try root password login to diagnose

### Firewall Rules Not Taking Effect
- Rules require **manual sync** after changes: `POST .../firewall/{id}/sync/{vmId}`
- Only one firewall can be active per VM
- Default policy is DROP — ensure accept rules exist for needed ports

### Docker Project Not Starting
- Check project logs: `GET .../docker/{name}/logs`
- Verify docker-compose.yaml is valid
- Ensure required ports are not already in use
- Check VM has enough resources (CPU, RAM, disk)

### Password Rejected During Recreate
- Must be 12+ characters with uppercase, lowercase, and numbers
- Password is checked against leaked password databases
- Try a completely unique, complex password

### Action Stuck in Progress
- Poll action status: `GET .../actions/{actionId}`
- Some operations take several minutes (recreate, backup restore)
- If stuck for extended time, contact support

## See Also

The following deep-dive guides are available in this skill directory:

- `deployment-workflow.md` — SSH-first deployment workflow for Dockerized apps (7-step process, rollback strategy, verification levels)
- `docker-patterns.md` — Docker Compose deployment patterns (WordPress, Node+Redis+Postgres, Traefik SSL, lifecycle management)
- `firewall-patterns.md` — Common firewall configurations (web server, database, Docker host, mail server, TypeScript/PHP examples)
- `terraform-examples.md` — Infrastructure as Code with the Hostinger Terraform Provider (VPS provisioning, SSH keys, firewalls, complete infra example)

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
- [Terraform Provider](https://github.com/hostinger/terraform-provider-hostinger)
- [Ansible Collection](https://github.com/hostinger/ansible-collection-hostinger)
- [MCP Server](https://github.com/hostinger/api-mcp-server)
