---
name: billing
description: Hostinger Billing API for catalog browsing, order creation, payment method management, and subscription control. Use when checking pricing, placing orders, managing payment methods, viewing subscriptions, or toggling auto-renewal.
last_updated: "2026-03-20"
doc_source: https://developers.hostinger.com
---

# Hostinger Billing

The Billing API allows you to browse the Hostinger service catalog, place orders, manage payment methods, and control subscriptions programmatically.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Catalog

The catalog contains available products and pricing. Prices are displayed in **cents** (integer), e.g., `1799` means `$17.99`. Use the catalog to discover available services and their `item_id` values before placing orders.

### Orders

Orders are created by referencing catalog `item_id` values and a payment method. Orders created via API are set for automatic renewal by default. Some `credit_card` payments may require additional verification.

### Payment Methods

Payment methods must be added via [hPanel](https://hpanel.hostinger.com/billing/payment-methods). The API lets you list, set a default, or delete existing payment methods.

### Subscriptions

Subscriptions represent active service plans. You can list subscriptions and toggle auto-renewal on or off.

## Common Patterns

### Browse Catalog and Place an Order

**CLI (curl):**

```bash
# Get available catalog items
curl -X GET "https://developers.hostinger.com/api/billing/v1/catalog" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json"

# Filter catalog by category
curl -X GET "https://developers.hostinger.com/api/billing/v1/catalog?category=vps" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

# List catalog items
catalog = client.billing.catalog.get_catalog_item_list()
for item in catalog:
    print(f"{item.name}: {item.price / 100:.2f} USD")
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const catalog = await client.billing.catalog.list();
for (const item of catalog) {
  console.log(`${item.name}: ${(item.price / 100).toFixed(2)} USD`);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$catalog = $client->billing->catalog->list();
foreach ($catalog as $item) {
    echo $item->name . ': ' . number_format($item->price / 100, 2) . " USD\n";
}
```

### Manage Payment Methods

```bash
# List payment methods
curl -X GET "https://developers.hostinger.com/api/billing/v1/payment-methods" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Set default payment method
curl -X POST "https://developers.hostinger.com/api/billing/v1/payment-methods/517244" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Delete a payment method
curl -X DELETE "https://developers.hostinger.com/api/billing/v1/payment-methods/517244" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Manage Subscriptions

```bash
# List all subscriptions
curl -X GET "https://developers.hostinger.com/api/billing/v1/subscriptions" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Disable auto-renewal for a subscription
curl -X DELETE "https://developers.hostinger.com/api/billing/v1/subscriptions/12345/auto-renewal/disable" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Enable auto-renewal for a subscription
curl -X PATCH "https://developers.hostinger.com/api/billing/v1/subscriptions/12345/auto-renewal/enable" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## API Reference

### Catalog

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/billing/v1/catalog` | Get catalog items (filterable by `category` and `name`) |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/billing/v1/orders` | Create service order (**DEPRECATED** - use domain/VPS specific endpoints) |

### Payment Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/billing/v1/payment-methods` | List payment methods |
| `POST` | `/api/billing/v1/payment-methods/{id}` | Set default payment method |
| `DELETE` | `/api/billing/v1/payment-methods/{id}` | Delete payment method |

### Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/billing/v1/subscriptions` | List all subscriptions |
| `DELETE` | `/api/billing/v1/subscriptions/{id}/auto-renewal/disable` | Disable auto-renewal |
| `PATCH` | `/api/billing/v1/subscriptions/{id}/auto-renewal/enable` | Enable auto-renewal |

## Best Practices

### Pricing
- Always fetch catalog prices before displaying to users — prices are in **cents**
- Divide by 100 and format appropriately for display

### Orders
- The generic `/api/billing/v1/orders` endpoint is **deprecated**
- Use `POST /api/domains/v1/portfolio` for domain purchases
- Use `POST /api/vps/v1/virtual-machines` for VPS purchases
- Prefer non-credit-card payment methods to avoid verification delays

### Payment Methods
- New payment methods must be added through hPanel, not the API
- If no payment method is specified in an order, the default method is used automatically
- Remove unused payment methods to keep your account clean

### Subscriptions
- Monitor subscriptions to avoid unexpected service interruptions
- Disable auto-renewal well before expiration if you intend to cancel

## Troubleshooting

### 401 Unauthorized
- Verify your API token is valid and not expired
- Token permissions match the owning user's permissions
- Check `Authorization: Bearer <token>` header format

### 422 Unprocessable Content
- Invalid `item_id` in order request — verify against catalog
- Invalid `payment_method_id` — list payment methods first

### 429 Too Many Requests
- You've exceeded rate limits — back off and retry
- Repeated violations may temporarily block your IP

### Order Not Processing
- `credit_card` payments may require additional verification
- Check order status in [hPanel](https://hpanel.hostinger.com/)
- Try a different payment method

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
