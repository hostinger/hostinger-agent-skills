# Docker Deployment Patterns on Hostinger VPS

Deep dive into deploying and managing Docker Compose projects via the Hostinger VPS API.

## Deployment Methods

### From Inline Content

Provide `docker-compose.yaml` content directly in the API request. Best for simple projects or when you want full control over the compose file.

**curl:**

```bash
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "webapp",
    "content": "version: \"3.8\"\nservices:\n  web:\n    image: nginx:alpine\n    ports:\n      - \"80:80\"\n    volumes:\n      - ./html:/usr/share/nginx/html\n  db:\n    image: postgres:16\n    environment:\n      POSTGRES_PASSWORD: secret\n    volumes:\n      - pgdata:/var/lib/postgresql/data\nvolumes:\n  pgdata:"
  }'
```

**TypeScript SDK:**

```typescript
import { Hostinger } from "hostinger-api-sdk";

const client = new Hostinger({ apiToken: "YOUR_API_TOKEN" });

await client.vps.docker.createProject(12345, {
  projectName: "webapp",
  content: `
version: "3.8"
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
`,
});
```

**PHP SDK:**

```php
use Hostinger\Api\HostingerApi;

$client = new HostingerApi('YOUR_API_TOKEN');

$client->vps->docker->createProject(12345, [
    'project_name' => 'webapp',
    'content' => 'version: "3.8"
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"',
]);
```

### From GitHub Repository

Provide a GitHub URL — the API auto-resolves to `docker-compose.yaml` in the master branch.

```bash
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-app",
    "url": "https://github.com/user/repo"
  }'
```

### From Any URL

Any URL that returns raw `docker-compose.yaml` content works.

```bash
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "my-app",
    "url": "https://raw.githubusercontent.com/user/repo/main/docker-compose.yaml"
  }'
```

## Common Application Stacks

### WordPress with MySQL

```yaml
version: "3.8"
services:
  wordpress:
    image: wordpress:latest
    ports:
      - "80:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wp_secret_123
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html
    depends_on:
      - db
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_secret
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wp_secret_123
    volumes:
      - db_data:/var/lib/mysql
volumes:
  wp_data:
  db_data:
```

### Node.js API with Redis and PostgreSQL

```yaml
version: "3.8"
services:
  api:
    image: node:20-alpine
    working_dir: /app
    command: npm start
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://api:secret@db:5432/myapp
      REDIS_URL: redis://cache:6379
    depends_on:
      - db
      - cache
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: api
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - pgdata:/var/lib/postgresql/data
  cache:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
volumes:
  pgdata:
  redis_data:
```

### Reverse Proxy with SSL (Traefik)

```yaml
version: "3.8"
services:
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - letsencrypt:/letsencrypt
  app:
    image: my-app:latest
    labels:
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
volumes:
  letsencrypt:
```

## Project Lifecycle Management

### Monitoring Project Health

```bash
# Get all projects with container status
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Get detailed container stats (CPU, memory, network)
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/containers" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Check logs for debugging (last 300 entries)
curl -X GET "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/logs" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Update Workflow

When you need to deploy new image versions:

```bash
# Update pulls latest images and recreates containers
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/update" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

This preserves data volumes while refreshing containers — ideal for rolling out application updates.

### Graceful Restart

```bash
# Stop all services (preserves data)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/stop" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Start services back up
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/start" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"

# Or restart in one step (preserves volumes and networks)
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/restart" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

### Tear Down (Irreversible)

```bash
# Stops containers, removes networks/volumes/images
curl -X DELETE "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker/webapp/down" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN"
```

## Replacing Existing Projects

Deploying a project with the same name as an existing one **replaces** it. Use this for zero-config redeployment:

```bash
# Redeploy with updated compose file
curl -X POST "https://developers.hostinger.com/api/vps/v1/virtual-machines/12345/docker" \
  -H "Authorization: Bearer $HOSTINGER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "webapp",
    "content": "...updated compose content..."
  }'
```

## Troubleshooting Docker Deployments

### Container Keeps Restarting
- Check logs: `GET .../docker/{name}/logs`
- Common causes: missing environment variables, incorrect image name, port conflicts
- Verify the image exists and is accessible from the VPS

### Port Already in Use
- Only one service can bind to a host port at a time
- Check existing projects: `GET .../docker`
- Use different host ports or remove conflicting projects

### Out of Disk Space
- Check VM metrics: `GET .../metrics`
- Docker images and volumes consume disk — clean up unused projects
- Consider upgrading the VPS plan for more storage

### GitHub URL Not Working
- URL must be in format `https://github.com/[user]/[repo]`
- Repo must have `docker-compose.yaml` in the root of the master branch
- For other branches, use the raw file URL instead
