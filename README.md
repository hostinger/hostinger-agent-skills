# Hostinger Agent Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code](https://img.shields.io/badge/Claude-Code-blueviolet)](https://claude.ai/code)

Supercharge Claude Code with Hostinger API skills across 6 core service domains.

## Why Hostinger Agent Skills?

Managing Hostinger services programmatically spans billing, domains, DNS, hosting, email marketing, and VPS infrastructure.

Hostinger Agent Skills equips Claude Code (and Codex) with deep expertise across all Hostinger API domains, enabling automated infrastructure management from domain registration to VPS deployment and Docker orchestration.

### Why not just use an MCP?

Hostinger offers an [official MCP server](https://github.com/hostinger/api-mcp-server), which is great for live API calls. Hostinger Agent Skills complements it by providing a curated, LLM-optimized knowledge base with real-world patterns, best practices, and troubleshooting guides — without streaming large API docs or schemas. Because the skills are local and pre-compressed, they are far more token efficient and keep the context window small and predictable.

## Installation

### Claude Code

#### From GitHub

```bash
# Add the marketplace
/plugin marketplace add https://github.com/hostinger/hostinger-agent-skills

# Install the plugin
/plugin install hostinger-agent-skills

# Activate
/reload-plugins
```

#### Local Development

```bash
# Add local marketplace
/plugin marketplace add /path/to/hostinger-agent-skills

# Install the plugin
/plugin install hostinger-agent-skills

# Activate
/reload-plugins
```

#### Validate (optional)

```bash
/plugin validate /path/to/hostinger-agent-skills/
```

## Available Skills

| Skill | Description |
|-------|-------------|
| **billing** | Catalog browsing, order creation, payment methods, subscriptions |
| **dns** | Zone record management, snapshots, validation, reset |
| **domains** | Portfolio management, availability checks, forwarding, WHOIS, nameservers, locks, privacy |
| **hosting** | Website creation, order listing, datacenter selection, domain verification, free subdomains |
| **reach** | Email marketing contacts, segments, profiles |
| **vps** | Virtual machines, Docker projects, firewalls, SSH keys, backups, snapshots, templates, scripts, recovery, malware scanning, metrics |

## Usage Examples

### Domain Management
Ask Claude to help with domains:
- "Check if example.com is available"
- "Register a new .com domain"
- "Set up domain forwarding from old-site.com to new-site.com"

### VPS Operations
- "Create a new VPS with Ubuntu"
- "Deploy a Docker Compose project on my VPS"
- "Configure a firewall to allow only SSH and HTTP"

### DNS Configuration
- "Add an A record pointing www to 1.2.3.4"
- "Set up SPF and DKIM records for email"
- "Restore DNS from a previous snapshot"

### Hosting Setup
- "Create a new website on my hosting plan"
- "Generate a free subdomain for testing"
- "List all my hosting orders"

## Skill Structure

Each skill contains:
- `SKILL.md` - Core concepts, common patterns (curl + Python SDK), API reference, best practices, troubleshooting

Skills include metadata showing when content was last updated, so you always know how current the information is.

## API Authentication

All Hostinger API requests require a bearer token:

```
Authorization: Bearer YOUR_API_TOKEN
```

Create tokens at: [hPanel API Settings](https://hpanel.hostinger.com/profile/api)

### Using with Claude Code

Set your token as an environment variable so it stays out of the conversation history:

```bash
export HOSTINGER_API_TOKEN="your-api-token"
```

For persistence, add it to your shell profile (`~/.zshrc` or `~/.bashrc`) or use a `.env` file (make sure it's in `.gitignore`).

**Never paste API tokens directly into the chat** — use `$HOSTINGER_API_TOKEN` in commands instead. If a token is accidentally exposed, rotate it immediately at [hPanel](https://hpanel.hostinger.com/profile/api).

## Contributing

1. Fork this repository
2. Create a feature branch
3. Add or update skills following the SKILL.md template
4. Submit a pull request

### SKILL.md Template

```yaml
---
name: service-name
description: Service description. Use when <trigger phrases>.
last_updated: "YYYY-MM-DD"
doc_source: https://developers.hostinger.com
---

# Hostinger Service Name

## Core Concepts
## Common Patterns
## API Reference
## Best Practices
## Troubleshooting
## References
```

## License

MIT License - see [LICENSE](LICENSE) for details.
