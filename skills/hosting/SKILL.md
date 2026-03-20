---
name: hosting
description: Hostinger Hosting API for website management, order listing, datacenter selection, domain verification, and free subdomain generation. Use when creating websites, listing hosting orders, choosing datacenters, verifying domain ownership, or generating free subdomains.
last_updated: "2026-03-20"
doc_source: https://developers.hostinger.com
---

# Hostinger Hosting

The Hosting API manages shared hosting services — creating websites, listing orders, selecting datacenters, verifying domain ownership, and generating free subdomains.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Websites

Websites are the core hosting resource. Each website is associated with a domain and a hosting order. Website types include main and addon websites. Creating a website triggers hosting account provisioning if it's the first on that plan.

### Orders

Hosting orders represent purchased hosting plans. Orders can be filtered by status and ID. Shared access is supported — you can see orders from other accounts that have granted you access.

### Datacenters

When creating the first website on a new hosting plan, you must select a datacenter. The first item in the datacenter list is the best match for your order requirements. Subsequent websites use the same datacenter automatically.

### Domain Verification

Before using a domain for hosting, ownership must be verified. Hostinger free subdomains (*.hostingersite.com) skip verification. For other domains, add the provided TXT record to your DNS and verify. Propagation can take up to 10 minutes.

### Free Subdomains

Hostinger provides free subdomains under `*.hostingersite.com` for immediate use without purchasing a custom domain.

## Common Patterns

### Create a Website (Full Flow)

```bash
# Step 1: List available datacenters for your order
curl -X GET "https://developers.hostinger.com/api/hosting/v1/datacenters?order_id=12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 2: Generate a free subdomain (optional, if no custom domain)
curl -X POST "https://developers.hostinger.com/api/hosting/v1/domains/free-subdomains" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 3: Verify domain ownership (skip for *.hostingersite.com)
curl -X POST "https://developers.hostinger.com/api/hosting/v1/domains/verify-ownership" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "domain": "example.com" }'

# Step 4: Create the website
curl -X POST "https://developers.hostinger.com/api/hosting/v1/websites" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "order_id": 12345,
    "datacenter_code": "us-east-1"
  }'
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

# List datacenters
datacenters = client.hosting.datacenters.list(order_id=12345)
dc_code = datacenters[0].code  # Use recommended datacenter

# Create website
client.hosting.websites.create(
    domain="example.com",
    order_id=12345,
    datacenter_code=dc_code
)
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const datacenters = await client.hosting.datacenters.list({ orderId: 12345 });
const dcCode = datacenters[0].code;

await client.hosting.websites.create({
  domain: "example.com",
  orderId: 12345,
  datacenterCode: dcCode,
});
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$datacenters = $client->hosting->datacenters->list(['order_id' => 12345]);
$dcCode = $datacenters[0]->code;

$client->hosting->websites->create([
    'domain' => 'example.com',
    'order_id' => 12345,
    'datacenter_code' => $dcCode,
]);
```

### List Websites

```bash
# List all websites
curl -X GET "https://developers.hostinger.com/api/hosting/v1/websites" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Filter by order ID
curl -X GET "https://developers.hostinger.com/api/hosting/v1/websites?order_id=12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Filter by domain
curl -X GET "https://developers.hostinger.com/api/hosting/v1/websites?domain=example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Paginate results
curl -X GET "https://developers.hostinger.com/api/hosting/v1/websites?page=2&per_page=25" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### List Hosting Orders

```bash
# List all orders
curl -X GET "https://developers.hostinger.com/api/hosting/v1/orders" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Filter by status
curl -X GET "https://developers.hostinger.com/api/hosting/v1/orders?statuses=active" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## API Reference

### Datacenters

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/datacenters` | List available datacenters (requires `order_id` query param) |

### Domains

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/hosting/v1/domains/free-subdomains` | Generate a free subdomain |
| `POST` | `/api/hosting/v1/domains/verify-ownership` | Verify domain ownership |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/orders` | List hosting orders (paginated, filterable) |

### Websites

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/websites` | List websites (paginated, filterable) |
| `POST` | `/api/hosting/v1/websites` | Create a new website |

### Query Parameters for Websites

| Parameter | Description |
|-----------|-------------|
| `page` | Page number |
| `per_page` | Items per page |
| `username` | Filter by username |
| `order_id` | Filter by order ID |
| `is_enabled` | Filter by enabled status |
| `domain` | Filter by domain name |

## Best Practices

### Website Creation
- Always select the recommended datacenter (first in the list) unless you have geographic requirements
- `datacenter_code` is only required for the **first** website on a new hosting plan
- Domain name cannot start with `www.` — use the bare domain
- Website creation takes up to a few minutes — poll the list endpoint to check status

### Domain Verification
- Skip verification for Hostinger free subdomains (`*.hostingersite.com`)
- DNS TXT record propagation can take up to 10 minutes
- Verify before attempting to create the website

### Free Subdomains
- Use free subdomains for testing or getting started quickly
- You can connect a custom domain later

### Orders
- Use filters to narrow down results instead of fetching everything
- Shared access orders appear alongside your own

## Troubleshooting

### Website Creation Failing
- Verify domain ownership first (unless using free subdomain)
- Ensure `order_id` is valid and belongs to an active hosting plan
- For the first website, `datacenter_code` is required
- Domain cannot start with `www.`

### Domain Verification Failing
- TXT record may not have propagated yet (wait up to 10 minutes)
- Verify TXT record is set correctly: `dig TXT example.com`
- Ensure you're verifying the correct domain (bare domain, not subdomain)

### Datacenter List Empty
- Ensure the `order_id` parameter is provided and valid
- The order may not have available capacity in any datacenter

### Website Not Appearing After Creation
- Website provisioning takes a few minutes
- Poll the websites list endpoint to check when it becomes available

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
