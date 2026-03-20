---
name: reach
description: Hostinger Reach (Email Marketing) API for contact management, segmentation, and profile management. Use when creating or listing contacts, managing contact segments, filtering contacts by groups or subscription status, or working with email marketing profiles.
last_updated: "2026-03-20"
doc_source: https://developers.hostinger.com
---

# Hostinger Reach (Email Marketing)

The Reach API provides email marketing capabilities — managing contacts, creating segments for targeted campaigns, and working with sender profiles.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Contacts

Contacts are email recipients in your marketing system. Each contact has basic information (name, email, surname) and a subscription status. If double opt-in is enabled, new contacts start with a pending status and receive a confirmation email.

### Segments

Segments group contacts based on specific criteria (email, name, subscription status, engagement metrics, etc.). Segments support complex filtering with operators like `equals`, `contains`, `gte`, `lte`, `opened`, `clicked`, etc.

### Profiles

Sender profiles represent the email identity used to send campaigns. Each profile has basic information and is associated with your account.

### Contact Groups

Groups are a way to organize contacts (deprecated in favor of segments).

### Subscription Status

Contacts can have different subscription statuses that determine whether they receive emails. Status can be used as a filter when listing contacts.

## Common Patterns

### Create and Manage Contacts

```bash
# Create a new contact (via profile)
curl -X POST "https://developers.hostinger.com/api/reach/v1/profiles/{profileUuid}/contacts" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John",
    "surname": "Doe"
  }'

# List contacts (paginated)
curl -X GET "https://developers.hostinger.com/api/reach/v1/contacts?page=1" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Filter contacts by subscription status
curl -X GET "https://developers.hostinger.com/api/reach/v1/contacts?subscription_status=active" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Delete a contact
curl -X DELETE "https://developers.hostinger.com/api/reach/v1/contacts/{uuid}" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

# List contacts
contacts = client.reach.contacts.list(page=1)
for contact in contacts:
    print(f"{contact.name} <{contact.email}>")
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const contacts = await client.reach.contacts.list({ page: 1 });
for (const contact of contacts) {
  console.log(`${contact.name} <${contact.email}>`);
}
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$contacts = $client->reach->contacts->list(['page' => 1]);
foreach ($contacts as $contact) {
    echo "{$contact->name} <{$contact->email}>\n";
}
```

### Work with Segments

```bash
# List all segments
curl -X GET "https://developers.hostinger.com/api/reach/v1/segmentation/segments" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Create a segment (e.g., engaged subscribers who opened emails)
curl -X POST "https://developers.hostinger.com/api/reach/v1/segmentation/segments" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engaged Subscribers",
    "logic": "and",
    "conditions": [
      {
        "field": "subscription_status",
        "operator": "equals",
        "value": "active"
      },
      {
        "field": "email_engagement",
        "operator": "opened"
      }
    ]
  }'

# Get segment details
curl -X GET "https://developers.hostinger.com/api/reach/v1/segmentation/segments/{segmentUuid}" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# List contacts in a segment (paginated)
curl -X GET "https://developers.hostinger.com/api/reach/v1/segmentation/segments/{segmentUuid}/contacts?page=1&per_page=50" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Manage Profiles

```bash
# List all sender profiles
curl -X GET "https://developers.hostinger.com/api/reach/v1/profiles" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## API Reference

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reach/v1/contacts` | List contacts (paginated, filterable) |
| `POST` | `/api/reach/v1/profiles/{profileUuid}/contacts` | Create new contact |
| `DELETE` | `/api/reach/v1/contacts/{uuid}` | Delete a contact |

### Segments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reach/v1/segmentation/segments` | List all segments |
| `POST` | `/api/reach/v1/segmentation/segments` | Create a new segment |
| `GET` | `/api/reach/v1/segmentation/segments/{segmentUuid}` | Get segment details |
| `GET` | `/api/reach/v1/segmentation/segments/{segmentUuid}/contacts` | List segment contacts |

### Profiles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reach/v1/profiles` | List sender profiles |

### Contact Query Parameters

| Parameter | Description |
|-----------|-------------|
| `page` | Page number |
| `group_uuid` | Filter by group UUID |
| `subscription_status` | Filter by subscription status |

### Segment Condition Operators

| Operator | Description |
|----------|-------------|
| `equals` / `not_equals` | Exact match |
| `contains` / `not_contains` | Partial match |
| `gte` / `lte` | Greater/less than or equal |
| `exists` | Field has a value |
| `within_last_days` / `not_within_last_days` | Date range |
| `older_than_days` | Older than N days |
| `opened` / `not_opened` | Email open engagement |
| `clicked` / `not_clicked` | Email click engagement |
| `bounced` / `not_bounced` | Bounce status |
| `delivered` / `not_delivered` | Delivery status |
| `unsubscribed` / `not_unsubscribed` | Unsubscribe status |

## Best Practices

### Contact Management
- Use profiles endpoint (`/profiles/{profileUuid}/contacts`) for creating contacts (preferred over deprecated endpoint)
- Enable double opt-in for compliance with email marketing regulations (GDPR, CAN-SPAM)
- Clean your contact list regularly by removing bounced and unsubscribed contacts

### Segmentation
- Use `and` logic for narrow, precise targeting
- Use `or` logic for broader audience reach
- Combine engagement operators (`opened`, `clicked`) with time-based operators for re-engagement campaigns
- Create segments before campaigns to preview audience size

### Profiles
- Verify sender profiles to improve deliverability
- Use consistent sender identity across campaigns

## Troubleshooting

### Contact Not Receiving Emails
- Check subscription status — contact may be unsubscribed or pending
- If double opt-in is enabled, contact must confirm their email first
- Verify the contact's email address is valid and not bouncing

### Segment Returns No Contacts
- Verify conditions and operators are correct
- Check that `logic` field (`and`/`or`) matches your intent
- Ensure contacts exist that match all/any conditions

### 422 Validation Error on Contact Creation
- Missing required fields (email is required)
- Invalid email format
- Duplicate email address in the system

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
