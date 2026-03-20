# Firewall Security Patterns for Hostinger VPS

Deep dive into configuring VPS firewalls using the Hostinger API. Covers common configurations, security hardening, and multi-language SDK examples.

## How Firewalls Work

- **Default policy: DROP all** — all incoming traffic is blocked unless explicitly allowed
- **One firewall per VM** — only one firewall can be active on a virtual machine at a time
- **Manual sync required** — after adding/updating/deleting rules, you must sync the firewall to the VM for changes to take effect
- **Account-level resource** — firewalls are created at the account level and activated on specific VMs

## Firewall Lifecycle

```
Create Firewall → Add Rules → Activate on VM → (Modify Rules → Sync to VM)
```

## Common Configurations

### Web Server (HTTP + HTTPS + SSH)

**curl:**

```bash
# Create firewall
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "name": "web-server" }'

# Allow SSH (port 22)
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "22", "source": "0.0.0.0/0", "action": "accept" }'

# Allow HTTP (port 80)
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "80", "source": "0.0.0.0/0", "action": "accept" }'

# Allow HTTPS (port 443)
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "443", "source": "0.0.0.0/0", "action": "accept" }'

# Activate on VM
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/activate/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

// Create firewall
const firewall = await client.vps.firewall.create({ name: "web-server" });

// Add rules
const rules = [
  { protocol: "tcp", port: "22", source: "0.0.0.0/0", action: "accept" },
  { protocol: "tcp", port: "80", source: "0.0.0.0/0", action: "accept" },
  { protocol: "tcp", port: "443", source: "0.0.0.0/0", action: "accept" },
];

for (const rule of rules) {
  await client.vps.firewall.createRule(firewall.id, rule);
}

// Activate on VM
await client.vps.firewall.activate(firewall.id, 12345);
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$firewall = $client->vps->firewall->create(['name' => 'web-server']);

$rules = [
    ['protocol' => 'tcp', 'port' => '22', 'source' => '0.0.0.0/0', 'action' => 'accept'],
    ['protocol' => 'tcp', 'port' => '80', 'source' => '0.0.0.0/0', 'action' => 'accept'],
    ['protocol' => 'tcp', 'port' => '443', 'source' => '0.0.0.0/0', 'action' => 'accept'],
];

foreach ($rules as $rule) {
    $client->vps->firewall->createRule($firewall->id, $rule);
}

$client->vps->firewall->activate($firewall->id, 12345);
```

### Database Server (Restricted Access)

Only allow SSH and database connections from specific IPs:

```bash
# Allow SSH from office IP only
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/2/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "22", "source": "203.0.113.50/32", "action": "accept" }'

# Allow PostgreSQL from app server
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/2/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "5432", "source": "198.51.100.10/32", "action": "accept" }'

# Allow MySQL from app server
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/2/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "3306", "source": "198.51.100.10/32", "action": "accept" }'
```

### Docker Host

Expose SSH + commonly used Docker ports:

```bash
# SSH
curl -X POST ".../firewall/3/rules" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "22", "source": "0.0.0.0/0", "action": "accept" }'

# HTTP/HTTPS for web containers
curl -X POST ".../firewall/3/rules" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "80", "source": "0.0.0.0/0", "action": "accept" }'

curl -X POST ".../firewall/3/rules" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "443", "source": "0.0.0.0/0", "action": "accept" }'

# Custom app port range (e.g., 3000-3999)
curl -X POST ".../firewall/3/rules" -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "3000:3999", "source": "0.0.0.0/0", "action": "accept" }'
```

### Mail Server

```bash
# SSH
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "22", "source": "0.0.0.0/0", "action": "accept" }'
# SMTP
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "25", "source": "0.0.0.0/0", "action": "accept" }'
# SMTPS
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "465", "source": "0.0.0.0/0", "action": "accept" }'
# Submission
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "587", "source": "0.0.0.0/0", "action": "accept" }'
# IMAP
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "143", "source": "0.0.0.0/0", "action": "accept" }'
# IMAPS
curl -X POST ".../firewall/4/rules" -d '{ "protocol": "tcp", "port": "993", "source": "0.0.0.0/0", "action": "accept" }'
```

## Modifying Rules

After modifying rules, **always sync** to apply changes:

```bash
# Update a rule
curl -X PUT "https://developers.hostinger.com/api/vps/v1/firewall/1/rules/5" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "2222", "source": "0.0.0.0/0", "action": "accept" }'

# Delete a rule
curl -X DELETE "https://developers.hostinger.com/api/vps/v1/firewall/1/rules/5" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# IMPORTANT: Sync after changes
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/sync/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Switching Firewalls

To switch from one firewall to another:

```bash
# Deactivate current firewall
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/1/deactivate/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Activate new firewall
curl -X POST "https://developers.hostinger.com/api/vps/v1/firewall/2/activate/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Security Hardening Checklist

1. **Never expose all ports** — only open what you actively use
2. **Restrict SSH access** to known IPs when possible (instead of `0.0.0.0/0`)
3. **Use non-standard SSH port** — change from 22 to reduce automated scan noise
4. **Restrict database ports** to application server IPs only
5. **Always sync after changes** — unsynchronized rules leave the VM exposed
6. **Review rules periodically** — remove rules for services no longer in use
7. **Delete unused firewalls** — deleting a firewall auto-deactivates it on all VMs
