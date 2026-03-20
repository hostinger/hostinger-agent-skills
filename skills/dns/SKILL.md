---
name: dns
description: Hostinger DNS API for zone record management, snapshots, and validation. Use when creating, updating, or deleting DNS records, restoring DNS snapshots, validating zone changes, or resetting DNS to defaults.
last_updated: "2026-03-20"
doc_source: https://developers.hostinger.com
---

# Hostinger DNS

The DNS API enables full management of DNS zone records for domains hosted on Hostinger. You can create, update, delete, validate, and reset DNS records, as well as manage DNS snapshots for backup and restore operations.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### DNS Records

Standard DNS record types are supported:

| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | `192.168.1.1` |
| AAAA | IPv6 address | `2001:db8::1` |
| CNAME | Canonical name alias | `www.example.com.` |
| ALIAS | ANAME/ALIAS record | `example.com.` |
| MX | Mail exchange | `mail.example.com.` |
| TXT | Text record | `v=spf1 include:...` |
| NS | Name server | `ns1.example.com.` |
| SOA | Start of authority | Zone authority info |
| SRV | Service locator | `_sip._tcp.example.com.` |
| CAA | Certificate authority auth | `0 issue "letsencrypt.org"` |

### Zone Updates

When updating DNS records, the `overwrite` flag controls behavior:
- `overwrite: true` (default) — Replaces existing records matching name and type with the new records
- `overwrite: false` — Updates TTL on existing records, appends new records; if no match found, creates them

### Snapshots

DNS snapshots capture the state of a domain's DNS zone at a point in time. Use them to restore previous configurations if something goes wrong.

### TTL (Time-To-Live)

TTL controls how long DNS resolvers cache a record. Default is `14400` seconds (4 hours). Lower values propagate changes faster but increase DNS query load.

## Common Patterns

### Get DNS Records for a Domain

```bash
curl -X GET "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")
records = client.dns.zone.get_dns_records("example.com")
for record in records:
    print(f"{record.type} {record.name} -> {record.content}")
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const records = await client.dns.zone.getRecords("example.com");
for (const record of records) {
  console.log(`${record.type} ${record.name} -> ${record.content}`);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$records = $client->dns->zone->getRecords('example.com');
foreach ($records as $record) {
    echo "{$record->type} {$record->name} -> {$record->content}\n";
}
```

### Create/Update DNS Records

```bash
# Add an A record for www subdomain
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": true,
    "zone": [
      {
        "name": "www",
        "type": "A",
        "ttl": 14400,
        "records": [
          { "content": "192.168.1.1" }
        ]
      }
    ]
  }'

# Add MX records for email
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": true,
    "zone": [
      {
        "name": "@",
        "type": "MX",
        "ttl": 14400,
        "records": [
          { "content": "10 mail1.example.com." },
          { "content": "20 mail2.example.com." }
        ]
      }
    ]
  }'

# Add a TXT record for SPF
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "@",
        "type": "TXT",
        "ttl": 14400,
        "records": [
          { "content": "v=spf1 include:_spf.google.com ~all" }
        ]
      }
    ]
  }'
```

### Validate Before Updating

```bash
# Validate records first (returns 200 if valid, 422 if invalid)
curl -X POST "https://developers.hostinger.com/api/dns/v1/zones/example.com/validate" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": true,
    "zone": [
      {
        "name": "www",
        "type": "CNAME",
        "ttl": 14400,
        "records": [
          { "content": "example.com." }
        ]
      }
    ]
  }'
```

### Delete Specific DNS Records

```bash
curl -X DELETE "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      { "name": "www", "type": "A" },
      { "name": "old", "type": "CNAME" }
    ]
  }'
```

### Reset DNS to Defaults

```bash
curl -X POST "https://developers.hostinger.com/api/dns/v1/zones/example.com/reset" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sync": true,
    "reset_email_records": false,
    "whitelisted_record_types": ["MX", "TXT"]
  }'
```

### Work with DNS Snapshots

```bash
# List available snapshots
curl -X GET "https://developers.hostinger.com/api/dns/v1/snapshots/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Get a specific snapshot with contents
curl -X GET "https://developers.hostinger.com/api/dns/v1/snapshots/example.com/42" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Restore from a snapshot
curl -X POST "https://developers.hostinger.com/api/dns/v1/snapshots/example.com/42/restore" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## API Reference

### Zone Records

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dns/v1/zones/{domain}` | Get DNS records |
| `PUT` | `/api/dns/v1/zones/{domain}` | Update DNS records |
| `DELETE` | `/api/dns/v1/zones/{domain}` | Delete DNS records |
| `POST` | `/api/dns/v1/zones/{domain}/reset` | Reset DNS to defaults |
| `POST` | `/api/dns/v1/zones/{domain}/validate` | Validate DNS records |

### Snapshots

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/dns/v1/snapshots/{domain}` | List DNS snapshots |
| `GET` | `/api/dns/v1/snapshots/{domain}/{snapshotId}` | Get snapshot with contents |
| `POST` | `/api/dns/v1/snapshots/{domain}/{snapshotId}/restore` | Restore from snapshot |

## Best Practices

### Record Management
- **Always validate** records with the `/validate` endpoint before applying changes
- Use `overwrite: false` when adding records without removing existing ones
- Use `overwrite: true` when you want to completely replace records of a given name/type
- Use `@` as the name for root domain records

### Safety
- **Take a snapshot** (or note existing records) before making bulk changes
- Use the `whitelisted_record_types` parameter during reset to preserve email records (MX, TXT)
- Set `reset_email_records: false` when resetting if you use third-party email services

### TTL
- Use lower TTL (300-600s) when planning changes for faster propagation
- Increase TTL (14400s+) for stable records to reduce DNS query load
- Remember: old cached records persist until the previous TTL expires

### Email Records
- Be careful with MX records — incorrect changes break email delivery
- SPF, DKIM, and DMARC records are TXT records — don't overwrite them accidentally

## Troubleshooting

### Records Not Propagating
- DNS propagation can take up to 48 hours (usually much less)
- Check the TTL of the old record — resolvers cache for that duration
- Use `dig` or `nslookup` to verify: `dig @8.8.8.8 example.com A`

### 422 Validation Error
- Invalid record content format (e.g., CNAME must end with `.`)
- Conflicting records (e.g., CNAME at root with other records)
- Invalid record type for the operation

### Email Stopped Working After DNS Change
- Check MX records: `dig example.com MX`
- Verify SPF TXT record is intact
- Use the snapshot restore to revert if needed

### Delete Not Working as Expected
- Filters match by `name` AND `type` — both must match
- If multiple records share name/type and you want to delete only some, use the update endpoint instead

## See Also

The following deep-dive guide is available in this skill directory:

- `email-dns-setup.md` — Complete email DNS setup (MX, SPF, DKIM, DMARC for Google Workspace, Microsoft 365, and Hostinger Email)

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
