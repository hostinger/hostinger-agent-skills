# Hostinger API References

## Official Documentation

| Resource | URL |
|----------|-----|
| API Portal | https://developers.hostinger.com |
| API Changelog | https://github.com/hostinger/api/blob/main/CHANGELOG.md |
| GitHub Repository | https://github.com/hostinger/api |

## SDKs & Tools

| Tool | URL |
|------|-----|
| Python SDK | https://github.com/hostinger/api-python-sdk |
| TypeScript SDK | https://github.com/hostinger/api-typescript-sdk |
| PHP SDK | https://github.com/hostinger/api-php-sdk |
| CLI Tool | https://github.com/hostinger/api-cli |
| Terraform Provider | https://github.com/hostinger/terraform-provider-hostinger |
| Ansible Collection | https://github.com/hostinger/ansible-collection-hostinger |
| MCP Server | https://github.com/hostinger/api-mcp-server |
| n8n Node | https://github.com/hostinger/api-n8n-node |
| WHMCS Module | https://github.com/hostinger/api-whmcs-plugin |
| Postman Collection | https://www.postman.com/hostinger-api |

## API Base URL

```
https://developers.hostinger.com
```

## Authentication

Bearer token authentication via `Authorization: Bearer YOUR_API_TOKEN` header.

Tokens are created at: https://hpanel.hostinger.com/profile/api

## Service Endpoints by Skill

| Skill | Base Path | Documentation Tag |
|-------|-----------|-------------------|
| Billing | `/api/billing/v1/` | Billing: Catalog, Orders, Payment methods, Subscriptions |
| DNS | `/api/dns/v1/` | DNS: Zone, Snapshot |
| Domains | `/api/domains/v1/` | Domains: Availability, Forwarding, Portfolio, WHOIS |
| Hosting | `/api/hosting/v1/` | Hosting: Datacenters, Domains, Orders, Websites |
| Reach | `/api/reach/v1/` | Reach: Contacts, Segments, Profiles |
| VPS | `/api/vps/v1/` | VPS: Virtual machine, Docker Manager, Firewall, Public Keys, OS Templates, Post-install scripts, Actions, Backups, Snapshots, Recovery, PTR records, Malware scanner |
