---
name: horizons
description: Hostinger Horizons API for the AI website builder. Use when creating a website, landing page, blog, or web app from a natural-language prompt, or when getting an editor link to modify an existing Horizons website.
last_updated: "2026-06-12"
doc_source: https://developers.hostinger.com
---

# Hostinger Horizons

Horizons is Hostinger's AI website builder. The API creates a website from a natural-language description and returns a link where the user can preview and edit it. Use it when a user asks to build a website, landing page, blog, or other web application, or to fetch an edit link for an existing Horizons site.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Common Patterns](#common-patterns)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Core Concepts

### Prompt-Driven Creation

You describe the desired site in natural language (the `message`), and Horizons generates it. The create call returns a **website URL and ID immediately**, but generation happens **asynchronously** — the site is built in the background after the call returns.

### Messages

The create request takes a `message` array of message objects. Each has a `type` (currently `text`) and the `text` describing what to build, e.g. *"Create a landing page for a coffee shop with a hero section, menu, and contact form."*

### Editing in the Horizons Interface

Horizons websites can only be modified inside the Horizons web interface. To change an existing site, fetch its edit link with `GET /websites/{websiteId}` and open the returned URL — there is no direct content-editing API.

## Common Patterns

### Create a Website from a Prompt

```bash
curl -X POST "https://developers.hostinger.com/api/horizons/v1/websites" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": [
      {
        "type": "text",
        "text": "Create a landing page for a coffee shop with a hero section, menu, and contact form"
      }
    ]
  }'
```

> Returns a website URL and ID right away; the site continues generating asynchronously. Share the URL with the user to watch progress and preview the result.

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

site = client.horizons.websites.create(
    message=[{"type": "text", "text": "Create a portfolio site for a photographer"}]
)
print(site.id, site.url)
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

const site = await client.horizons.websites.create({
  message: [{ type: "text", text: "Create a portfolio site for a photographer" }],
});
console.log(site.id, site.url);
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$site = $client->horizons->websites->create([
    'message' => [
        ['type' => 'text', 'text' => 'Create a portfolio site for a photographer'],
    ],
]);
echo $site->id . ' ' . $site->url . "\n";
```

### Get an Edit Link for an Existing Website

```bash
curl -X GET "https://developers.hostinger.com/api/horizons/v1/websites/12345" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

> Returns a link to edit the website in the Horizons interface. Use this whenever the user wants to modify, edit, or add features to an existing Horizons site.

## API Reference

### Websites

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/horizons/v1/websites` | Create a website from a prompt (async generation) |
| `GET` | `/api/horizons/v1/websites/{websiteId}` | Get a Horizons editor link for the website |

### Create Website Body

| Field | Type | Description |
|-------|------|-------------|
| `message` | array | Required. Array of message objects describing the site |
| `message[].type` | string | Message type (currently `text`) |
| `message[].text` | string | The natural-language description of what to build |

## Best Practices

### Prompts
- Be specific about sections, purpose, and tone in the `message` text — more detail yields a closer first result
- One clear description per create call; refine afterwards in the Horizons interface rather than re-creating

### Async Handling
- Treat create as fire-and-forget: surface the returned URL to the user so they can watch generation finish
- Don't expect a fully built site in the create response — only the URL and ID are immediate

### Editing
- Always fetch a fresh edit link via `GET /websites/{websiteId}` rather than caching old URLs

## Troubleshooting

### 401 Unauthorized
- Verify your API token is valid and not expired
- Check the `Authorization: Bearer <token>` header format

### 422 Unprocessable Content
- The `message` array is missing or empty
- A message object is missing `type` or `text`

### Website Not Ready
- Generation is asynchronous — give it time and revisit the returned URL
- The edit link from `GET /websites/{websiteId}` opens the site in the Horizons interface even while it finishes building

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
