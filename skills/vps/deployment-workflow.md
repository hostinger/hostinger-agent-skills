# SSH-First Deployment Workflow for Hostinger VPS

End-to-end operational guide for deploying and managing Dockerized applications on Hostinger VPS. Uses SSH + Docker Compose as the primary deployment mechanism, with the Hostinger API for account-level infrastructure operations.

## When to Use This vs. Docker Manager API

| Use SSH + Docker Compose | Use Hostinger Docker Manager API |
|--------------------------|----------------------------------|
| Production deployments with existing compose files | Quick prototyping without SSH access |
| Complex multi-service apps with migrations | Simple single-container deployments |
| When you need fine-grained control over startup order | When you want to deploy from a GitHub URL |
| When the repo already has deployment scripts | When you don't need custom startup logic |

**Rule of thumb:** If the project already has a working `docker-compose.yaml` and deployment scripts, use SSH. Don't replace a working SSH + Docker Compose workflow with the Docker Manager API unless explicitly requested.

## Workflow Overview

```
1. Gather Inputs → 2. SSH Key Setup → 3. VPS Baseline → 4. Deploy/Update → 5. Verify → 6. Rollback Plan → 7. API Guardrails
```

## Step 1: Gather Inputs

Collect these values before running any commands:

| Variable | Description | Example |
|----------|-------------|---------|
| `HOSTINGER_API_TOKEN` | API bearer token | From hPanel > Profile > API |
| `HOSTINGER_VPS_ID` | Virtual machine ID | `12345` |
| `SSH_USER` | SSH username | `root` |
| `SSH_HOST` | VPS IP or hostname | `198.51.100.10` |
| `SSH_PRIVATE_KEY_PATH` | Path to SSH private key | `~/.ssh/hostinger_vps` |
| `REMOTE_APP_DIR` | App directory on VPS | `~/app` |

```bash
export HOSTINGER_API_TOKEN="your-token"
export HOSTINGER_VPS_ID="12345"
export SSH_USER="root"
export SSH_HOST="198.51.100.10"
export SSH_KEY="~/.ssh/hostinger_vps"
export REMOTE_APP_DIR="~/app"
```

**Important:** If the current repository already has deployment scripts or runbooks, reuse them first rather than reimplementing generic commands.

## Step 2: SSH Key Setup

### Generate a Keypair (if missing)

```bash
ssh-keygen -t ed25519 -C "hostinger-vps" -f ~/.ssh/hostinger_vps
```

### Register and Attach via Hostinger API

```bash
# 1. Register the public key in your Hostinger account
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/public-keys" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"deploy-key-$(hostname)\",
    \"key\": \"$(cat ~/.ssh/hostinger_vps.pub)\"
  }"
# Note the returned key ID

# 2. Attach the key to your VPS
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/public-keys/attach/$HOSTINGER_VPS_ID" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "ids": [KEY_ID_FROM_STEP_1] }'

# 3. Verify SSH access
ssh -i ~/.ssh/hostinger_vps $SSH_USER@$SSH_HOST "echo SSH_OK && whoami && hostname"
```

**Python SDK:**

```python
from hostinger_api import Hostinger
import subprocess

client = Hostinger(api_token="YOUR_API_TOKEN")

# Read public key
with open(os.path.expanduser("~/.ssh/hostinger_vps.pub")) as f:
    pub_key = f.read().strip()

# Register key
key = client.vps.public_keys.create(name="deploy-key", key=pub_key)

# Attach to VPS
client.vps.public_keys.attach(vm_id=12345, ids=[key.id])

# Verify SSH
result = subprocess.run(
    ["ssh", "-i", "~/.ssh/hostinger_vps", "root@198.51.100.10", "echo SSH_OK"],
    capture_output=True, text=True
)
assert "SSH_OK" in result.stdout
```

## Step 3: VPS Baseline (First-Time Setup)

Run these checks on the VPS via SSH before the first deployment:

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'SETUP'
# Install Docker (Ubuntu/Debian)
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose plugin
if ! docker compose version &> /dev/null; then
    apt-get update && apt-get install -y docker-compose-plugin
fi

# Create deployment directory
mkdir -p ~/app

# Verify
docker --version
docker compose version
SETUP
```

### Baseline Checklist

- [ ] Docker engine installed and running
- [ ] Docker Compose plugin available (`docker compose version`)
- [ ] Deployment directory exists
- [ ] `.env` file exists with all required variables (non-empty)
- [ ] Firewall allows SSH (22) and required app ports only
- [ ] Database ports are NOT publicly exposed unless explicitly needed

### Configure Firewall via API

```bash
# Create firewall with SSH + app ports only
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/firewall" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "name": "app-deploy" }'

# Add SSH rule
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/firewall/FW_ID/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "22", "source": "0.0.0.0/0", "action": "accept" }'

# Add app port (e.g., 443 for HTTPS)
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/firewall/FW_ID/rules" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "protocol": "tcp", "port": "443", "source": "0.0.0.0/0", "action": "accept" }'

# Activate and sync
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/firewall/FW_ID/activate/$HOSTINGER_VPS_ID" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Step 4: Deploy and Update

### First Deployment

```bash
# 1. Sync project files to VPS
rsync -avz -e "ssh -i $SSH_KEY" \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='.env.local' \
  ./ $SSH_USER@$SSH_HOST:$REMOTE_APP_DIR/

# 2. Copy environment file (never commit this)
scp -i $SSH_KEY .env.production $SSH_USER@$SSH_HOST:$REMOTE_APP_DIR/.env

# 3. Deploy on VPS
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'DEPLOY'
cd ~/app

# Start database dependencies first
docker compose up -d db redis

# Wait for DB to be ready
echo "Waiting for database..."
sleep 10

# Run migrations
docker compose run --rm app npm run migrate
# or: docker compose run --rm app python manage.py migrate

# Start application services
docker compose up -d

# Verify
docker compose ps
docker compose logs --tail=50
DEPLOY
```

### Subsequent Updates

Follow the same order — this keeps deployments predictable:

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'UPDATE'
cd ~/app

# Pull latest images (if using registry)
docker compose pull

# Or sync updated code first (if building locally)
# rsync done before this SSH session

# Restart with minimal downtime
docker compose up -d --build

# Run any new migrations
docker compose run --rm app npm run migrate

# Verify
docker compose ps
docker compose logs --tail=50 app
UPDATE
```

**Key rules for updates:**
- Keep the same startup order: dependencies → migrations → app
- Avoid `docker compose down -v` — this destroys volumes and data
- Use `docker compose up -d` which recreates only changed services
- Commands should be idempotent — safe to run multiple times

## Step 5: Verify

Three levels of verification, from infrastructure to functionality:

### Level 1: Container Health

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'CHECK'
cd ~/app

# All containers should show "Up" or "healthy"
docker compose ps

# Check for restart loops
docker compose ps --format json | jq '.[] | select(.State != "running")'
CHECK
```

### Level 2: Application Logs

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'LOGS'
cd ~/app

# Recent logs from app service
docker compose logs --tail=200 app

# Check for errors across all services
docker compose logs --tail=100 | grep -i "error\|fatal\|exception"
LOGS
```

### Level 3: Functional Smoke Test

```bash
# HTTP health check (from local machine or VPS)
curl -sf https://your-app.example.com/health || echo "HEALTH CHECK FAILED"

# Or from VPS internally
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "curl -sf http://localhost:3000/health"
```

For application-specific tests (e.g., Discord bot, API endpoints), run a real end-to-end test from the client surface to confirm the deployed service works as expected.

## Step 6: Rollback

### Pre-Deploy Safety Net

**Always** before risky deployments (database migrations, major version bumps):

```bash
# Create VPS snapshot via API
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/snapshot" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# And/or create a database backup on VPS
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'BACKUP'
cd ~/app
docker compose exec db pg_dump -U postgres mydb > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql
# or for MySQL:
# docker compose exec db mysqldump -u root -p mydb > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql
BACKUP
```

### If Deploy Fails

```bash
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST << 'ROLLBACK'
cd ~/app

# 1. Restore previous compose/image version
git checkout HEAD~1 -- docker-compose.yaml
# or: docker compose pull app:previous-tag

# 2. Restart services
docker compose up -d

# 3. If migration was incompatible, restore DB
docker compose exec -T db psql -U postgres mydb < /tmp/backup_YYYYMMDD_HHMMSS.sql

# 4. Verify
docker compose ps
docker compose logs --tail=50
ROLLBACK
```

### Full VPS Rollback (Nuclear Option)

```bash
# Restore from VPS snapshot (overwrites everything)
curl -sS -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/$HOSTINGER_VPS_ID/snapshot/restore" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Step 7: Hostinger API — When to Use What

| Operation | Use SSH | Use API |
|-----------|---------|---------|
| Deploy/update app | Yes | No (unless using Docker Manager for simple cases) |
| Run migrations | Yes | No |
| View logs | Yes | No |
| Register SSH keys | No | Yes |
| Configure firewall | No | Yes |
| Create snapshots/backups | No | Yes |
| Check VM status | Either | Yes (for automation) |
| Restart VM | Either | Yes |
| Install Monarx malware scanner | No | Yes |

## Safety Rules

1. **Never print secrets** in terminal output — use env vars, not inline values
2. **Never commit `.env` files** — add to `.gitignore`
3. **Never run `docker compose down -v`** in production unless explicitly approved — this destroys data volumes
4. **Validate critical env vars** before deployment — check `.env` has non-empty values for required keys
5. **Keep commands idempotent** — every command should be safe to run multiple times
6. **Snapshot before migrations** — database schema changes are the riskiest part of any deploy
7. **Don't expose database ports** publicly unless explicitly needed — keep them internal to the Docker network

## Quick Reference: Common SSH Commands

```bash
# Deploy
rsync -avz -e "ssh -i $SSH_KEY" ./ $SSH_USER@$SSH_HOST:~/app/
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose up -d"

# Status
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose ps"

# Logs
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose logs --tail=100"

# Restart
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose restart"

# Shell into container
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose exec app sh"

# DB backup
ssh -i $SSH_KEY $SSH_USER@$SSH_HOST "cd ~/app && docker compose exec db pg_dump -U postgres mydb > /tmp/backup.sql"
```
