# AWS EC2 Deployment Guide - PathFinder Academic Dashboard

## Prerequisites
- AWS Account with EC2 access
- EC2 instance running (recommended: t3.medium or larger)
- Ubuntu 22.04 LTS (recommended)
- Domain name (optional but recommended)

---

## Changes Required for AWS EC2 Deployment

### 1. Backend Changes

#### A. Environment Variables (.env)
**CRITICAL CHANGES:**
```bash
# Set to production mode
DEBUG=False

# Update CORS to include your EC2 public IP/domain
ALLOWED_ORIGINS=http://your-ec2-public-ip:5173,http://your-domain.com,https://your-domain.com

# Use strong JWT secret (generate new one!)
JWT_SECRET_KEY=generate-a-new-secure-256-bit-key-here-use-secrets-token-urlsafe

# Keep existing Cassandra settings (already external)
CASSANDRA_HOST=sunway.hep88.com
CASSANDRA_PORT=9042
```

#### B. Security Group Configuration
**Required Inbound Rules:**
- **Port 9000** (Backend API) - Source: 0.0.0.0/0 or specific IPs
- **Port 5173** (Frontend Dev) or **Port 80/443** (Production) - Source: 0.0.0.0/0
- **Port 22** (SSH) - Source: Your IP only
- **Port 9042** (Cassandra) - Should already be accessible to sunway.hep88.com

---

### 2. Frontend Changes

#### A. Environment Configuration
Create `.env.production` file in `frontend/`:
```bash
VITE_API_URL=http://your-ec2-public-ip:9000
# Or for domain:
# VITE_API_URL=https://api.yourdomain.com
```

#### B. Build Configuration
Update `vite.config.ts` for production:
```typescript
export default defineConfig({
  server: {
    host: '0.0.0.0', // Allow external connections
    port: 5173,
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
  }
})
```

---

### 3. Deployment Files to Create

#### A. Systemd Service for Backend
Create `/etc/systemd/system/pathfinder-backend.service`:
```ini
[Unit]
Description=PathFinder Backend API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/PathFinder---Personalized-Academic-Dashboard/backend
Environment="PATH=/home/ubuntu/PathFinder---Personalized-Academic-Dashboard/backend/venv/bin"
ExecStart=/home/ubuntu/PathFinder---Personalized-Academic-Dashboard/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### B. Nginx Configuration (Optional - Recommended for Production)
Install nginx: `sudo apt install nginx`

Create `/etc/nginx/sites-available/pathfinder`:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or EC2 public IP

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:9000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

---

## Step-by-Step Deployment Process

### Step 1: Connect to EC2 Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 2: Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Git
sudo apt install git -y

# Install Nginx (optional)
sudo apt install nginx -y
```

### Step 3: Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/yourusername/PathFinder---Personalized-Academic-Dashboard.git
cd PathFinder---Personalized-Academic-Dashboard
```

### Step 4: Setup Backend
```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with production settings
nano .env
# (Copy production settings from above)

# Test backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000
# Press Ctrl+C after confirming it works
```

### Step 5: Setup Frontend
```bash
cd ../frontend

# Install dependencies
npm install

# Create production env file
nano .env.production
# Add: VITE_API_URL=http://your-ec2-public-ip:9000

# Build for production (optional - for static hosting)
npm run build

# Or run dev server (for testing)
npm run dev -- --host 0.0.0.0
```

### Step 6: Configure Systemd Service
```bash
# Create backend service
sudo nano /etc/systemd/system/pathfinder-backend.service
# (Copy service file from above)

# Reload systemd
sudo systemctl daemon-reload

# Start and enable service
sudo systemctl start pathfinder-backend
sudo systemctl enable pathfinder-backend

# Check status
sudo systemctl status pathfinder-backend

# View logs
sudo journalctl -u pathfinder-backend -f
```

### Step 7: Configure Nginx (Optional)
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/pathfinder

# Enable site
sudo ln -s /etc/nginx/sites-available/pathfinder /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 8: Configure Firewall
```bash
# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 9000/tcp  # Backend API
sudo ufw allow 5173/tcp  # Frontend (if not using nginx)
sudo ufw enable
```

---

## Production Checklist

### Security
- [ ] Change DEBUG=False in backend .env
- [ ] Generate new JWT_SECRET_KEY (use: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] Update ALLOWED_ORIGINS with actual domain/IP
- [ ] Configure AWS Security Groups properly
- [ ] Enable UFW firewall
- [ ] Use HTTPS with SSL certificate (Let's Encrypt)
- [ ] Remove .env files from git (should already be in .gitignore)

### Backend
- [ ] Update .env with production settings
- [ ] Install all Python dependencies
- [ ] Setup systemd service
- [ ] Configure logging to file
- [ ] Test API endpoints
- [ ] Setup monitoring (optional: PM2, CloudWatch)

### Frontend
- [ ] Update VITE_API_URL to EC2 public IP or domain
- [ ] Build production bundle (npm run build) or run dev server
- [ ] Configure web server (nginx recommended)
- [ ] Test all routes and API calls
- [ ] Setup auto-restart on failure

### Database
- [ ] Verify Cassandra connection from EC2
- [ ] Ensure security group allows connection to sunway.hep88.com:9042
- [ ] Test queries from EC2 instance

### Monitoring
- [ ] Setup CloudWatch logs
- [ ] Configure health check endpoint monitoring
- [ ] Setup alerts for downtime
- [ ] Monitor disk space and memory

---

## Quick Commands Reference

### Backend Management
```bash
# Start backend
sudo systemctl start pathfinder-backend

# Stop backend
sudo systemctl stop pathfinder-backend

# Restart backend
sudo systemctl restart pathfinder-backend

# View logs
sudo journalctl -u pathfinder-backend -f

# Check status
sudo systemctl status pathfinder-backend
```

### Frontend Management (if using PM2)
```bash
# Install PM2
sudo npm install -g pm2

# Start frontend
pm2 start npm --name "pathfinder-frontend" -- run dev -- --host 0.0.0.0

# Save PM2 config
pm2 save
pm2 startup
```

### Update Deployment
```bash
# Pull latest code
cd /home/ubuntu/PathFinder---Personalized-Academic-Dashboard
git pull

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart pathfinder-backend

# Update frontend
cd ../frontend
npm install
npm run build  # If using production build
pm2 restart pathfinder-frontend  # If using PM2
```

---

## Environment Variables Summary

### Backend (.env)
```bash
DEBUG=False
HOST=0.0.0.0
PORT=9000
ALLOWED_ORIGINS=http://your-domain.com,https://your-domain.com
JWT_SECRET_KEY=your-secure-production-key
CASSANDRA_HOST=sunway.hep88.com
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=subjectplanning
CASSANDRA_USERNAME=planusertest
CASSANDRA_PASSWORD=Ic7cU8K965Zqx
LOG_LEVEL=INFO
```

### Frontend (.env.production)
```bash
VITE_API_URL=http://your-ec2-ip:9000
# Or with domain:
# VITE_API_URL=https://api.yourdomain.com
```

---

## Common Issues & Solutions

### Issue 1: CORS Errors
**Solution:** Ensure ALLOWED_ORIGINS includes your frontend URL (with correct protocol and port)

### Issue 2: Can't Connect to Backend
**Solution:** 
- Check security group allows port 9000
- Verify backend is running: `sudo systemctl status pathfinder-backend`
- Check firewall: `sudo ufw status`

### Issue 3: Cassandra Connection Failed
**Solution:**
- Verify EC2 can reach sunway.hep88.com
- Check security group outbound rules
- Test: `telnet sunway.hep88.com 9042`

### Issue 4: Frontend Shows "Network Error"
**Solution:**
- Update VITE_API_URL in .env.production
- Rebuild frontend: `npm run build`
- Clear browser cache

---

## SSL/HTTPS Setup (Recommended)

### Using Let's Encrypt (Free)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
# Test renewal: sudo certbot renew --dry-run
```

Update nginx config to use SSL:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of config
}
```

---

## Cost Estimation (AWS)
- **t3.medium EC2**: ~$30/month (2 vCPU, 4GB RAM)
- **20GB Storage**: ~$2/month
- **Data Transfer**: Varies (~$9/GB egress)
- **Total Estimated**: ~$35-50/month

---

## Support & Troubleshooting
- View backend logs: `sudo journalctl -u pathfinder-backend -f`
- View nginx logs: `sudo tail -f /var/log/nginx/error.log`
- Check ports: `sudo netstat -tlnp | grep -E '(9000|5173)'`
- Test API: `curl http://localhost:9000/health`
