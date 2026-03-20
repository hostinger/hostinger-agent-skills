# Domain Transfer & Management Guide

Deep dive into domain lifecycle operations using the Hostinger Domains API — purchasing, configuring, transferring, and protecting domains.

## Domain Purchase Workflow

### Step 1: Check Availability

```bash
curl -X POST "https://developers.hostinger.com/api/domains/v1/availability" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "myproject",
    "tlds": ["com", "net", "io", "dev"],
    "with_alternatives": false
  }'
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const availability = await client.domains.availability.check({
  domain: "myproject",
  tlds: ["com", "net", "io", "dev"],
});

for (const result of availability) {
  console.log(`${result.domain}: ${result.available ? "Available" : "Taken"}`);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$result = $client->domains->availability->check([
    'domain' => 'myproject',
    'tlds' => ['com', 'net', 'io', 'dev'],
]);
```

> Rate limit: 10 requests per minute. For alternative suggestions, provide only one TLD and set `with_alternatives: true`.

### Step 2: Ensure WHOIS Profile Exists

```bash
# List existing profiles for the target TLD
curl -X GET "https://developers.hostinger.com/api/domains/v1/whois?tld=com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Create one if needed
curl -X POST "https://developers.hostinger.com/api/domains/v1/whois" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tld": "com",
    "entity_type": "individual",
    "country": "US",
    "whois_details": {
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@company.com",
      "phone": "+1.5551234567",
      "address": "456 Tech Ave",
      "city": "San Francisco",
      "state": "CA",
      "zip": "94105"
    }
  }'
```

### Step 3: Get Pricing from Catalog

```bash
curl -X GET "https://developers.hostinger.com/api/billing/v1/catalog?category=domain" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

Look for `item_id` values like `hostingercom-domain-com-usd-1y`.

### Step 4: Purchase

```bash
curl -X POST "https://developers.hostinger.com/api/domains/v1/portfolio" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "myproject.com",
    "item_id": "hostingercom-domain-com-usd-1y",
    "payment_method_id": 1327362,
    "domain_contacts": {
      "owner_id": 741288,
      "admin_id": 741288,
      "billing_id": 741288,
      "tech_id": 741288
    }
  }'
```

### Step 5: Secure the Domain

```bash
# Enable domain lock
curl -X PUT "https://developers.hostinger.com/api/domains/v1/portfolio/myproject.com/domain-lock" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Enable privacy protection
curl -X PUT "https://developers.hostinger.com/api/domains/v1/portfolio/myproject.com/privacy-protection" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Domain Configuration

### Pointing to Hosting (Hostinger Nameservers)

Use Hostinger's default nameservers to manage DNS through the Hostinger DNS API:

```bash
curl -X PUT "https://developers.hostinger.com/api/domains/v1/portfolio/example.com/nameservers" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ns1": "ns1.dns-parking.com",
    "ns2": "ns2.dns-parking.com"
  }'
```

### Pointing to External DNS (Cloudflare, Route53, etc.)

```bash
# Cloudflare example
curl -X PUT "https://developers.hostinger.com/api/domains/v1/portfolio/example.com/nameservers" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ns1": "aria.ns.cloudflare.com",
    "ns2": "tim.ns.cloudflare.com"
  }'
```

> After changing nameservers, DNS is managed by the new provider. The Hostinger DNS API only works with Hostinger nameservers.

### Domain Forwarding

Redirect one domain to another without hosting:

```bash
# Permanent redirect (301) — best for SEO
curl -X POST "https://developers.hostinger.com/api/domains/v1/forwarding" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "old-brand.com",
    "redirect_type": "301",
    "redirect_url": "https://new-brand.com"
  }'

# Temporary redirect (302) — for marketing campaigns
curl -X POST "https://developers.hostinger.com/api/domains/v1/forwarding" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "promo.com",
    "redirect_type": "302",
    "redirect_url": "https://main-site.com/promo"
  }'
```

## Preparing for Domain Transfer (Out)

To transfer a domain away from Hostinger:

```bash
# Step 1: Disable domain lock
curl -X DELETE "https://developers.hostinger.com/api/domains/v1/portfolio/example.com/domain-lock" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 2: Get domain details (includes auth/EPP code info)
curl -X GET "https://developers.hostinger.com/api/domains/v1/portfolio/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Step 3: Initiate transfer at the new registrar using the EPP code
# (Done outside Hostinger API)

# Step 4: Approve the transfer when notified
# (Done via email or hPanel)
```

## WHOIS Profile Management

### Organization vs Individual

```bash
# Organization profile
curl -X POST "https://developers.hostinger.com/api/domains/v1/whois" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tld": "com",
    "entity_type": "organization",
    "country": "NL",
    "whois_details": {
      "company_name": "Acme Corp",
      "first_name": "John",
      "last_name": "Doe",
      "email": "domains@acme.com",
      "phone": "+31.201234567",
      "address": "Keizersgracht 1",
      "city": "Amsterdam",
      "zip": "1015AA"
    }
  }'
```

### Check Profile Usage Before Deletion

```bash
# See which domains use this profile
curl -X GET "https://developers.hostinger.com/api/domains/v1/whois/741288/usage" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Only delete if no domains use it
curl -X DELETE "https://developers.hostinger.com/api/domains/v1/whois/741288" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Multi-Domain Management Patterns

### Audit All Domains

```bash
# List all domains
curl -X GET "https://developers.hostinger.com/api/domains/v1/portfolio" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK — Check lock and privacy status for all domains:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

domains = client.domains.portfolio.list()
for domain in domains:
    details = client.domains.portfolio.get(domain.name)
    print(f"{domain.name}:")
    print(f"  Lock: {details.domain_lock}")
    print(f"  Privacy: {details.privacy_protection}")
    print(f"  Expires: {details.expiration_date}")
```

### Bulk Security Hardening

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

domains = client.domains.portfolio.list()
for domain in domains:
    # Enable lock on all domains
    client.domains.portfolio.enable_domain_lock(domain.name)
    # Enable privacy on all domains
    client.domains.portfolio.enable_privacy_protection(domain.name)
    print(f"Secured: {domain.name}")
```

## TLD-Specific Considerations

- Some TLDs require `additional_details` during purchase (varies by TLD)
- WHOIS profile requirements differ by TLD — always specify the correct `tld` when creating profiles
- Not all TLDs support domain lock or privacy protection
- Transfer lock periods may apply after registration (typically 60 days for `.com`)
