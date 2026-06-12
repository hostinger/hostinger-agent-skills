---
name: ecommerce
description: Hostinger Ecommerce API for managing online stores. Use when listing the stores on an account or creating a new store (which also provisions a primary sales channel).
last_updated: "2026-06-12"
doc_source: https://developers.hostinger.com
---

# Hostinger Ecommerce

The Ecommerce API manages online stores associated with your Hostinger account. You can list existing stores and create new ones — creating a store also provisions a primary sales channel for it.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Stores

A store is the top-level ecommerce entity tied to your account. Each store carries company details (name, email, country) and a default language used for the storefront.

### Sales Channels

Every store has at least one **sales channel** — the surface through which products are sold. When you create a store, a **primary sales channel** is created alongside it. You can supply a `sales_channel` object (e.g., `type: custom` with an `external_id`) to link the store to an external system.

## Common Patterns

### List Stores

```bash
curl -X GET "https://developers.hostinger.com/api/ecommerce/v1/stores" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Paginate
curl -X GET "https://developers.hostinger.com/api/ecommerce/v1/stores?page=2" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

stores = client.ecommerce.stores.list()
for store in stores:
    print(store.name)
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const stores = await client.ecommerce.stores.list();
for (const store of stores) {
  console.log(store.name);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$stores = $client->ecommerce->stores->list();
foreach ($stores as $store) {
    echo $store->name . "\n";
}
```

### Create a Store

```bash
curl -X POST "https://developers.hostinger.com/api/ecommerce/v1/stores" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Store",
    "country_code": "us",
    "company_email": "owner@example.com",
    "company_name": "My Company",
    "language": "en",
    "sales_channel": {
      "type": "custom",
      "external_id": "ext-12345"
    }
  }'
```

> A primary sales channel is created automatically with the store. The `sales_channel` object is optional — omit it to use the default.

## API Reference

### Stores

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/ecommerce/v1/stores` | Get stores (paginated via `page`) |
| `POST` | `/api/ecommerce/v1/stores` | Create a store (also creates a primary sales channel) |

### Create Store Body

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Store name |
| `country_code` | string | ISO country code (e.g., `us`) |
| `company_email` | string | Company contact email |
| `company_name` | string | Company name |
| `language` | string | Default storefront language (e.g., `en`) |
| `sales_channel` | object | Optional. `{ "type": "custom", "external_id": "..." }` |

## Best Practices

### Store Setup
- Set `country_code` and `language` to match your target market — they drive storefront defaults
- Use a monitored `company_email` — it receives store-related notifications
- Provide a `sales_channel.external_id` when integrating with an external system so you can reconcile records later

### Listing
- Paginate with `page` when an account has many stores rather than assuming a single page

## Troubleshooting

### 401 Unauthorized
- Verify your API token is valid and not expired
- Check the `Authorization: Bearer <token>` header format

### 422 Unprocessable Content
- Invalid `country_code` (use a valid ISO code like `us`) or malformed `company_email`
- Missing or malformed `sales_channel` object when one is provided

### Store Not Appearing After Creation
- Re-list stores — propagation may take a moment
- Confirm the create request returned a success status and a store ID

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
