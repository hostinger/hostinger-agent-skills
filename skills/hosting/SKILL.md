---
name: hosting
description: Hostinger Hosting API for website management, order listing, datacenter selection, domain verification, free subdomains, databases, subdomains, parked domains, Node.js applications, and WordPress installs. Use when creating websites, listing hosting orders, choosing datacenters, verifying domain ownership, managing MySQL databases, adding subdomains or parked domains, deploying Node.js apps, or installing WordPress.
last_updated: "2026-06-12"
doc_source: https://developers.hostinger.com
---

# Hostinger Hosting

The Hosting API manages shared hosting services — creating websites, listing orders, selecting datacenters, verifying domain ownership, generating free subdomains, managing databases, subdomains and parked domains, deploying Node.js applications, and installing WordPress.

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

### Hosting Accounts (`username`)

Beyond the order/website model above, many hosting operations are scoped to a **hosting account**, identified by its `username`. The username is returned in the websites list (`GET /api/hosting/v1/websites`) and is the path root for managing databases, subdomains, parked domains, Node.js builds, and per-account WordPress installs (`/api/hosting/v1/accounts/{username}/...`). Database names and users are automatically prefixed with this username.

### Databases

Each hosting account can hold multiple MySQL databases, each with its own database user and password. Databases are assigned to a website domain. You can create and delete databases, change the database user password, repair corrupted tables, and obtain a single sign-on phpMyAdmin link for visual management.

### Subdomains & Parked Domains

- **Subdomains** — additional hostnames under an existing website (e.g., `blog.example.com`), each with its own document root.
- **Parked domains** (alias domains) — additional domains that serve the *same* content as the parent website.

Both are managed under a specific website: `/api/hosting/v1/accounts/{username}/websites/{domain}/...`.

### Node.js Applications

Websites on Node.js-capable plans run a build pipeline. The recommended flow uploads a project archive, auto-detects build settings from its `package.json`, and starts a build in one step. Each build has a `uuid` and a state (`pending`, `running`, `completed`, `failed`); poll the build's logs (using `from_line`) to stream output while it runs.

### WordPress

Install WordPress on an existing website. The website must already exist — create it first via `POST /api/hosting/v1/websites` and poll until it appears. Installation is asynchronous; poll `GET /api/hosting/v1/wordpress/installations` to confirm readiness.

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

### Manage Databases

```bash
# List databases for an account (filter by domain / assignment / search)
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases?domain=example.com&is_assigned=true" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Create a database (name and user are auto-prefixed with the account username)
curl -X POST "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "appdb",
    "user": "appuser",
    "password": "SecurePass123!",
    "website_domain": "example.com"
  }'

# Change the database user password (also update it in your site config)
curl -X PATCH "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases/u123456789_appdb/change-password" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "password": "NewSecurePass456!" }'

# Get a single sign-on phpMyAdmin link
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases/u123456789_appdb/phpmyadmin-link" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Repair corrupted tables (asynchronous)
curl -X PATCH "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases/u123456789_appdb/repair" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Delete a database (use the full name from the list endpoint)
curl -X DELETE "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/databases/u123456789_appdb" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

**Python SDK:**

```python
from hostinger_api import Hostinger

client = Hostinger(api_token="YOUR_API_TOKEN")

# Create a database
client.hosting.databases.create(
    username="u123456789",
    name="appdb",
    user="appuser",
    password="SecurePass123!",
    website_domain="example.com",
)

# List databases
databases = client.hosting.databases.list(username="u123456789")
for db in databases:
    print(db.name)
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

await client.hosting.databases.create("u123456789", {
  name: "appdb",
  user: "appuser",
  password: "SecurePass123!",
  websiteDomain: "example.com",
});

const databases = await client.hosting.databases.list("u123456789");
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$client->hosting->databases->create('u123456789', [
    'name' => 'appdb',
    'user' => 'appuser',
    'password' => 'SecurePass123!',
    'website_domain' => 'example.com',
]);

$databases = $client->hosting->databases->list('u123456789');
```

### Manage Subdomains and Parked Domains

```bash
# List subdomains for a website
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/subdomains" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Create a subdomain (optionally with a custom directory)
curl -X POST "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/subdomains" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subdomain": "blog",
    "directory": "blog",
    "is_using_public_directory": false
  }'

# Delete a subdomain
curl -X DELETE "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/subdomains/blog" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# List parked (alias) domains
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/parked-domains" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Park a domain so it serves the same content as the parent website
curl -X POST "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/parked-domains" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "parked_domain": "example.net" }'

# Remove a parked domain
curl -X DELETE "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/parked-domains/example.net" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Deploy a Node.js Application

```bash
# Create and start a build from a project archive (settings auto-detected from package.json)
curl -X POST "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/nodejs/builds/from-archive" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "archive": "uploads/my-app.zip",
    "node_version": 20,
    "app_type": "ssr",
    "build_script": "build",
    "entry_file": "server.js",
    "package_manager": "npm"
  }'

# List builds (filter by state)
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/nodejs/builds?states[]=running" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Stream build logs while running (poll with from_line = previously returned line count)
curl -X GET "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/websites/example.com/nodejs/builds/3f9a.../logs?from_line=0" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Install WordPress

```bash
# Step 1: ensure the website exists (POST /websites, then poll GET /websites)
# Step 2: install WordPress on it
curl -X POST "https://developers.hostinger.com/api/hosting/v1/accounts/u123456789/wordpress/installations" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "site_title": "My Site",
    "language": "en_US",
    "directory": "public_html",
    "auto_updates": "minor",
    "credentials": {
      "email": "owner@example.com",
      "login": "admin",
      "password": "SecureAdminPass123!"
    }
  }'

# Step 3: poll for readiness (installation is asynchronous)
curl -X GET "https://developers.hostinger.com/api/hosting/v1/wordpress/installations?username=u123456789&domain=example.com" \
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

### Databases

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/accounts/{username}/databases` | List account databases (filters: `page`, `per_page`, `domain`, `is_assigned`, `search`) |
| `POST` | `/api/hosting/v1/accounts/{username}/databases` | Create a database with user and password |
| `DELETE` | `/api/hosting/v1/accounts/{username}/databases/{name}` | Delete a database (use full name) |
| `PATCH` | `/api/hosting/v1/accounts/{username}/databases/{name}/change-password` | Change database user password |
| `GET` | `/api/hosting/v1/accounts/{username}/databases/{name}/phpmyadmin-link` | Get phpMyAdmin single sign-on link |
| `PATCH` | `/api/hosting/v1/accounts/{username}/databases/{name}/repair` | Repair corrupted tables (async) |

### Subdomains

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/accounts/{username}/websites/{domain}/subdomains` | List website subdomains |
| `POST` | `/api/hosting/v1/accounts/{username}/websites/{domain}/subdomains` | Create a subdomain |
| `DELETE` | `/api/hosting/v1/accounts/{username}/websites/{domain}/subdomains/{subdomain}` | Delete a subdomain |

### Parked Domains

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/accounts/{username}/websites/{domain}/parked-domains` | List parked (alias) domains |
| `POST` | `/api/hosting/v1/accounts/{username}/websites/{domain}/parked-domains` | Create a parked domain |
| `DELETE` | `/api/hosting/v1/accounts/{username}/websites/{domain}/parked-domains/{parkedDomain}` | Delete a parked domain |

### Node.js

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds` | List builds (filters: `page`, `per_page`, `states`) |
| `POST` | `/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds/from-archive` | Create and start a build from an archive |
| `GET` | `/api/hosting/v1/accounts/{username}/websites/{domain}/nodejs/builds/{uuid}/logs` | Get build logs (poll with `from_line`) |

### WordPress

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/hosting/v1/accounts/{username}/wordpress/installations` | Install WordPress on an existing website |
| `GET` | `/api/hosting/v1/wordpress/installations` | List WordPress installations (filters: `username`, `domain`, `ownership`) |

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

### Databases
- The `name` and `user` you supply are auto-prefixed with the account `username` — always use the **full name** returned by the list endpoint for delete/change-password/repair/phpMyAdmin calls
- After `change-password`, update the credentials in any website configuration (e.g., `wp-config.php`) that uses the database
- `repair` runs asynchronously — re-list or retry the operation rather than expecting an immediate result

### Subdomains & Parked Domains
- Use **subdomains** for separate content under a host (`blog.example.com`); use **parked domains** to serve the same content from another domain
- Subdomain DNS must point to Hostinger for the host to resolve

### Node.js
- Prefer the `from-archive` endpoint — it auto-detects build settings from `package.json` in one step
- Poll the logs endpoint with `from_line` (the previous `lines` count) to stream only new output while the build state is `running`

### WordPress
- The target website must exist **before** installing — create it first and poll the websites list
- Installation is asynchronous; confirm completion by polling `GET /wordpress/installations`
- Use `auto_updates: minor` (default-safe) unless you have a reason to disable updates

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

### Database Operation Returns 404
- Use the **full** prefixed database name (e.g., `u123456789_appdb`) from the list endpoint, not the short name you passed to create
- Confirm the `username` in the path matches the account that owns the database

### Node.js Build Fails
- Check the build logs: `GET .../nodejs/builds/{uuid}/logs`
- Verify `package.json` exists in the archive and `build_script`/`entry_file` are correct
- Ensure `node_version` matches what your app requires

### WordPress Install Not Completing
- Confirm the website exists first (`GET /websites`) — installs fail if the site is missing
- Installation is asynchronous — poll `GET /wordpress/installations` (filter by `username` + `domain`)
- Set `overwrite: true` only if you intend to replace existing files in the target directory

## References

- [Hostinger API Documentation](https://developers.hostinger.com)
- [Hostinger API Changelog](https://github.com/hostinger/api/blob/main/CHANGELOG.md)
- [Python SDK](https://github.com/hostinger/api-python-sdk)
- [TypeScript SDK](https://github.com/hostinger/api-typescript-sdk)
- [PHP SDK](https://github.com/hostinger/api-php-sdk)
- [CLI Tool](https://github.com/hostinger/api-cli)
