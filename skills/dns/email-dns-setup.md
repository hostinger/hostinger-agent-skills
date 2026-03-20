# Email DNS Setup Guide

Complete guide for configuring SPF, DKIM, DMARC, and MX records using the Hostinger DNS API. Proper email DNS configuration is critical for deliverability and preventing spoofing.

## Overview

Email DNS requires four types of records:

| Record | Purpose | Type |
|--------|---------|------|
| **MX** | Routes email to mail servers | MX |
| **SPF** | Declares which servers can send email for your domain | TXT |
| **DKIM** | Cryptographic signature verifying email authenticity | TXT |
| **DMARC** | Policy for handling emails that fail SPF/DKIM | TXT |

## MX Records

MX (Mail Exchange) records tell other mail servers where to deliver email for your domain.

### Google Workspace

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": true,
    "zone": [
      {
        "name": "@",
        "type": "MX",
        "ttl": 3600,
        "records": [
          { "content": "1 aspmx.l.google.com." },
          { "content": "5 alt1.aspmx.l.google.com." },
          { "content": "5 alt2.aspmx.l.google.com." },
          { "content": "10 alt3.aspmx.l.google.com." },
          { "content": "10 alt4.aspmx.l.google.com." }
        ]
      }
    ]
  }'
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

await client.dns.zone.updateRecords("example.com", {
  overwrite: true,
  zone: [
    {
      name: "@",
      type: "MX",
      ttl: 3600,
      records: [
        { content: "1 aspmx.l.google.com." },
        { content: "5 alt1.aspmx.l.google.com." },
        { content: "5 alt2.aspmx.l.google.com." },
        { content: "10 alt3.aspmx.l.google.com." },
        { content: "10 alt4.aspmx.l.google.com." },
      ],
    },
  ],
});
```

### Microsoft 365

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": true,
    "zone": [
      {
        "name": "@",
        "type": "MX",
        "ttl": 3600,
        "records": [
          { "content": "0 example-com.mail.protection.outlook.com." }
        ]
      }
    ]
  }'
```

### Hostinger Email

```bash
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
          { "content": "5 mx1.hostinger.com." },
          { "content": "10 mx2.hostinger.com." }
        ]
      }
    ]
  }'
```

## SPF Records

SPF (Sender Policy Framework) prevents email spoofing by declaring which mail servers are authorized to send email on behalf of your domain.

### Google Workspace SPF

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "@",
        "type": "TXT",
        "ttl": 3600,
        "records": [
          { "content": "v=spf1 include:_spf.google.com ~all" }
        ]
      }
    ]
  }'
```

### Microsoft 365 SPF

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "@",
        "type": "TXT",
        "ttl": 3600,
        "records": [
          { "content": "v=spf1 include:spf.protection.outlook.com ~all" }
        ]
      }
    ]
  }'
```

### Multiple Senders (Combined SPF)

If you use multiple email services, combine them in a single SPF record:

```bash
# Google Workspace + Mailgun + your own server
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "@",
        "type": "TXT",
        "ttl": 3600,
        "records": [
          { "content": "v=spf1 include:_spf.google.com include:mailgun.org ip4:198.51.100.10 ~all" }
        ]
      }
    ]
  }'
```

> **Important:** Only one SPF record per domain. Multiple SPF records cause validation failures.

## DKIM Records

DKIM (DomainKeys Identified Mail) adds a cryptographic signature. Your email provider gives you the DKIM key value.

### Google Workspace DKIM

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "google._domainkey",
        "type": "TXT",
        "ttl": 3600,
        "records": [
          { "content": "v=DKIM1; k=rsa; p=YOUR_DKIM_PUBLIC_KEY_FROM_GOOGLE_ADMIN" }
        ]
      }
    ]
  }'
```

### Microsoft 365 DKIM

Microsoft 365 uses CNAME records for DKIM:

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "selector1._domainkey",
        "type": "CNAME",
        "ttl": 3600,
        "records": [
          { "content": "selector1-example-com._domainkey.example.onmicrosoft.com." }
        ]
      },
      {
        "name": "selector2._domainkey",
        "type": "CNAME",
        "ttl": 3600,
        "records": [
          { "content": "selector2-example-com._domainkey.example.onmicrosoft.com." }
        ]
      }
    ]
  }'
```

## DMARC Records

DMARC (Domain-based Message Authentication, Reporting, and Conformance) tells receiving servers what to do with emails that fail SPF/DKIM checks.

### Monitoring Mode (Start Here)

```bash
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      {
        "name": "_dmarc",
        "type": "TXT",
        "ttl": 3600,
        "records": [
          { "content": "v=DMARC1; p=none; rua=mailto:dmarc-reports@example.com; pct=100" }
        ]
      }
    ]
  }'
```

### Quarantine Mode (After Monitoring)

```bash
# Move failing emails to spam
{ "content": "v=DMARC1; p=quarantine; rua=mailto:dmarc-reports@example.com; pct=100" }
```

### Reject Mode (Full Protection)

```bash
# Reject emails that fail SPF/DKIM
{ "content": "v=DMARC1; p=reject; rua=mailto:dmarc-reports@example.com; pct=100" }
```

## Complete Setup Workflow

Set up all email records at once using `overwrite: false` to preserve existing records:

```bash
# Step 1: Validate first
curl -X POST "https://developers.hostinger.com/api/dns/v1/zones/example.com/validate" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "overwrite": false,
    "zone": [
      { "name": "@", "type": "MX", "ttl": 3600, "records": [
        { "content": "1 aspmx.l.google.com." },
        { "content": "5 alt1.aspmx.l.google.com." }
      ]},
      { "name": "@", "type": "TXT", "ttl": 3600, "records": [
        { "content": "v=spf1 include:_spf.google.com ~all" }
      ]},
      { "name": "_dmarc", "type": "TXT", "ttl": 3600, "records": [
        { "content": "v=DMARC1; p=none; rua=mailto:dmarc@example.com" }
      ]}
    ]
  }'

# Step 2: Apply if validation passes (200)
curl -X PUT "https://developers.hostinger.com/api/dns/v1/zones/example.com" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ ... same body as above ... }'
```

## Verification

After setting records, verify with DNS lookups:

```bash
# Check MX records
dig MX example.com +short

# Check SPF
dig TXT example.com +short | grep spf

# Check DKIM
dig TXT google._domainkey.example.com +short

# Check DMARC
dig TXT _dmarc.example.com +short
```

## Common Mistakes

1. **Multiple SPF records** — combine all senders into one record
2. **Missing trailing dot** on MX hostnames — `aspmx.l.google.com.` not `aspmx.l.google.com`
3. **Using `overwrite: true` for TXT records** — this deletes ALL TXT records including site verification
4. **Forgetting to validate** — always use the `/validate` endpoint first
5. **Starting DMARC at `reject`** — always start with `none`, monitor, then escalate
