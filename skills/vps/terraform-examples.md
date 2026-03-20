# Terraform Examples for Hostinger VPS

Infrastructure as Code patterns using the [Hostinger Terraform Provider](https://github.com/hostinger/terraform-provider-hostinger) for VPS provisioning and management.

## Provider Setup

```hcl
terraform {
  required_providers {
    hostinger = {
      source  = "hostinger/hostinger"
    }
  }
}

provider "hostinger" {
  # Set via HOSTINGER_API_TOKEN environment variable
  # or directly: api_token = "your-token"
}
```

```bash
# Set token via environment
export HOSTINGER_API_TOKEN="your-api-token"

# Initialize Terraform
terraform init
```

## Basic VPS Provisioning

### Single Server

```hcl
# Look up available templates
data "hostinger_vps_templates" "all" {}

# Look up available data centers
data "hostinger_vps_data_centers" "all" {}

# Look up catalog for pricing
data "hostinger_billing_catalog" "vps" {
  category = "vps"
}

resource "hostinger_vps" "web" {
  hostname    = "web-server"
  template_id = data.hostinger_vps_templates.all.templates[0].id
  data_center = data.hostinger_vps_data_centers.all.data_centers[0].id
  item_id     = "hostingercom-vps-kvm2-usd-1m"
  password    = var.root_password
}

variable "root_password" {
  type      = string
  sensitive = true
}

output "server_ip" {
  value = hostinger_vps.web.ip_address
}
```

### Multiple Servers

```hcl
variable "servers" {
  default = {
    web = { hostname = "web-prod" }
    api = { hostname = "api-prod" }
    db  = { hostname = "db-prod" }
  }
}

resource "hostinger_vps" "cluster" {
  for_each = var.servers

  hostname    = each.value.hostname
  template_id = data.hostinger_vps_templates.all.templates[0].id
  data_center = data.hostinger_vps_data_centers.all.data_centers[0].id
  item_id     = "hostingercom-vps-kvm2-usd-1m"
  password    = var.root_password
}

output "server_ips" {
  value = { for k, v in hostinger_vps.cluster : k => v.ip_address }
}
```

## SSH Key Management

```hcl
resource "hostinger_vps_ssh_key" "deploy" {
  name = "deploy-key"
  key  = file("~/.ssh/id_ed25519.pub")
}

resource "hostinger_vps_ssh_key" "developer" {
  name = "dev-key"
  key  = var.developer_ssh_key
}

# Attach keys to server
resource "hostinger_vps_ssh_key_attachment" "web_keys" {
  virtual_machine_id = hostinger_vps.web.id
  ssh_key_ids        = [
    hostinger_vps_ssh_key.deploy.id,
    hostinger_vps_ssh_key.developer.id,
  ]
}
```

## Firewall Configuration

```hcl
resource "hostinger_vps_firewall" "web" {
  name = "web-server-fw"
}

# SSH access
resource "hostinger_vps_firewall_rule" "ssh" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "22"
  source      = var.office_ip
  action      = "accept"
}

# HTTP
resource "hostinger_vps_firewall_rule" "http" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "80"
  source      = "0.0.0.0/0"
  action      = "accept"
}

# HTTPS
resource "hostinger_vps_firewall_rule" "https" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "443"
  source      = "0.0.0.0/0"
  action      = "accept"
}

# Activate firewall on VM
resource "hostinger_vps_firewall_activation" "web" {
  firewall_id        = hostinger_vps_firewall.web.id
  virtual_machine_id = hostinger_vps.web.id
}

variable "office_ip" {
  type        = string
  description = "Office IP in CIDR notation (e.g., 203.0.113.50/32)"
}
```

## Post-Install Scripts

```hcl
resource "hostinger_vps_post_install_script" "docker_setup" {
  name    = "install-docker"
  content = <<-SCRIPT
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io docker-compose-plugin
    systemctl enable docker
    systemctl start docker
    echo "Docker installed" >> /post_install.log
  SCRIPT
}

resource "hostinger_vps_post_install_script" "hardening" {
  name    = "security-hardening"
  content = <<-SCRIPT
    #!/bin/bash
    # Disable password auth for SSH
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    systemctl restart sshd

    # Enable automatic security updates
    apt-get install -y unattended-upgrades
    echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades

    echo "Hardening complete" >> /post_install.log
  SCRIPT
}
```

## Complete Infrastructure Example

A full production setup with web server, database, firewall, and SSH keys:

```hcl
terraform {
  required_providers {
    hostinger = {
      source = "hostinger/hostinger"
    }
  }
}

provider "hostinger" {}

# Data sources
data "hostinger_vps_templates" "all" {}
data "hostinger_vps_data_centers" "all" {}

# Variables
variable "root_password" {
  type      = string
  sensitive = true
}

variable "ssh_public_key" {
  type = string
}

variable "admin_ip" {
  type        = string
  description = "Admin IP for SSH access (CIDR)"
}

# SSH Key
resource "hostinger_vps_ssh_key" "admin" {
  name = "admin-key"
  key  = var.ssh_public_key
}

# Web Server
resource "hostinger_vps" "web" {
  hostname    = "web-prod"
  template_id = data.hostinger_vps_templates.all.templates[0].id
  data_center = data.hostinger_vps_data_centers.all.data_centers[0].id
  item_id     = "hostingercom-vps-kvm4-usd-1m"
  password    = var.root_password
}

# Database Server
resource "hostinger_vps" "db" {
  hostname    = "db-prod"
  template_id = data.hostinger_vps_templates.all.templates[0].id
  data_center = data.hostinger_vps_data_centers.all.data_centers[0].id
  item_id     = "hostingercom-vps-kvm2-usd-1m"
  password    = var.root_password
}

# Attach SSH keys
resource "hostinger_vps_ssh_key_attachment" "web" {
  virtual_machine_id = hostinger_vps.web.id
  ssh_key_ids        = [hostinger_vps_ssh_key.admin.id]
}

resource "hostinger_vps_ssh_key_attachment" "db" {
  virtual_machine_id = hostinger_vps.db.id
  ssh_key_ids        = [hostinger_vps_ssh_key.admin.id]
}

# Web Server Firewall
resource "hostinger_vps_firewall" "web" {
  name = "web-fw"
}

resource "hostinger_vps_firewall_rule" "web_ssh" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "22"
  source      = var.admin_ip
  action      = "accept"
}

resource "hostinger_vps_firewall_rule" "web_http" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "80"
  source      = "0.0.0.0/0"
  action      = "accept"
}

resource "hostinger_vps_firewall_rule" "web_https" {
  firewall_id = hostinger_vps_firewall.web.id
  protocol    = "tcp"
  port        = "443"
  source      = "0.0.0.0/0"
  action      = "accept"
}

resource "hostinger_vps_firewall_activation" "web" {
  firewall_id        = hostinger_vps_firewall.web.id
  virtual_machine_id = hostinger_vps.web.id
}

# Database Firewall
resource "hostinger_vps_firewall" "db" {
  name = "db-fw"
}

resource "hostinger_vps_firewall_rule" "db_ssh" {
  firewall_id = hostinger_vps_firewall.db.id
  protocol    = "tcp"
  port        = "22"
  source      = var.admin_ip
  action      = "accept"
}

resource "hostinger_vps_firewall_rule" "db_postgres" {
  firewall_id = hostinger_vps_firewall.db.id
  protocol    = "tcp"
  port        = "5432"
  source      = "${hostinger_vps.web.ip_address}/32"
  action      = "accept"
}

resource "hostinger_vps_firewall_activation" "db" {
  firewall_id        = hostinger_vps_firewall.db.id
  virtual_machine_id = hostinger_vps.db.id
}

# Outputs
output "web_ip" {
  value = hostinger_vps.web.ip_address
}

output "db_ip" {
  value     = hostinger_vps.db.ip_address
  sensitive = true
}
```

### Apply

```bash
terraform plan -var="root_password=SecurePass123!" \
  -var="ssh_public_key=$(cat ~/.ssh/id_ed25519.pub)" \
  -var="admin_ip=203.0.113.50/32"

terraform apply
```

## Tips

- Use `terraform plan` to preview changes before applying
- Store state remotely (S3, Terraform Cloud) for team collaboration
- Use `sensitive = true` for passwords and private IPs
- The Terraform provider wraps the same Hostinger API — resource names map to API endpoints
- Refer to the [provider documentation](https://github.com/hostinger/terraform-provider-hostinger) for the latest resource schemas
