# AWS EC2 Deployment - Quick Checklist

## Pre-Deployment (Do BEFORE deploying)

### AWS Console Setup
- [ ] Launch EC2 instance (Ubuntu 22.04 LTS, t3.medium recommended)
- [ ] Configure Security Group with these inbound rules:
  - [ ] Port 22 (SSH) - Your IP only
  - [ ] Port 80 (HTTP) - 0.0.0.0/0
  - [ ] Port 443 (HTTPS) - 0.0.0.0/0
  - [ ] Port 9000 (Backend API) - 0.0.0.0/0
  - [ ] Port 5173 (Frontend) - 0.0.0.0/0
- [ ] Allocate and associate Elastic IP (recommended)
- [ ] Download .pem key file

### Code Changes (Do on YOUR local machine BEFORE deploying)

#### Backend
1. [ ] Update `backend/.env.production`:
   ```bash
   DEBUG=False
   ALLOWED_ORIGINS=http://YOUR_EC2_IP:5173,http://YOUR_EC2_IP
   JWT_SECRET_KEY=GENERATE_NEW_ONE  # Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. [ ] Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Add production configuration"
   git push
   ```

#### Frontend
1. [ ] Update `frontend/.env.production`:
   ```bash
   VITE_API_URL=http://YOUR_EC2_IP:9000
   ```

2. [ ] Commit and push

---

## Deployment Steps (On EC2 instance)

### Step 1: Connect to EC2
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
```

### Step 2: Clone Repository
```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USERNAME/PathFinder---Personalized-Academic-Dashboard.git
cd PathFinder---Personalized-Academic-Dashboard
```

### Step 3: Run Deployment Script
```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Step 4: Manual Configuration
```bash
# 1. Update backend .env
cd /home/ubuntu/PathFinder---Personalized-Academic-Dashboard/backend
nano .env
# Update ALLOWED_ORIGINS and JWT_SECRET_KEY

# 2. Restart backend
sudo systemctl restart pathfinder-backend

# 3. Start frontend
cd ../frontend
npm run dev -- --host 0.0.0.0 &
```

### Step 5: Verify Deployment
- [ ] Backend health: http://YOUR_EC2_IP:9000/health
- [ ] API docs: http://YOUR_EC2_IP:9000/docs
- [ ] Frontend: http://YOUR_EC2_IP:5173
- [ ] Test login functionality

---

## Quick Reference Commands

### Service Management
```bash
# Backend
sudo systemctl status pathfinder-backend
sudo systemctl restart pathfinder-backend
sudo systemctl stop pathfinder-backend
sudo systemctl start pathfinder-backend

# View logs
sudo journalctl -u pathfinder-backend -f
sudo tail -f /var/log/pathfinder-backend.log
```

### Frontend Management
```bash
# If using PM2
pm2 list
pm2 restart pathfinder-frontend
pm2 logs pathfinder-frontend

# Manual run
cd /home/ubuntu/PathFinder---Personalized-Academic-Dashboard/frontend
npm run dev -- --host 0.0.0.0
```

### Nginx
```bash
sudo systemctl status nginx
sudo systemctl restart nginx
sudo nginx -t  # Test configuration
sudo tail -f /var/log/nginx/error.log
```

### Update Code
```bash
cd /home/ubuntu/PathFinder---Personalized-Academic-Dashboard
git pull
sudo systemctl restart pathfinder-backend
# Restart frontend if needed
```

---

## Troubleshooting

### Backend not starting
```bash
# Check service status
sudo systemctl status pathfinder-backend

# Check logs
sudo journalctl -u pathfinder-backend -n 50

# Test manually
cd /home/ubuntu/PathFinder---Personalized-Academic-Dashboard/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 9000
```

### CORS errors
- Check `backend/.env` ALLOWED_ORIGINS includes your EC2 IP
- Restart backend after changes

### Can't connect to API
- Check AWS Security Group allows port 9000
- Check UFW firewall: `sudo ufw status`
- Verify backend is running: `curl http://localhost:9000/health`

### Frontend shows blank page
- Check browser console for errors
- Verify `frontend/.env.production` has correct VITE_API_URL
- Check frontend is running on 0.0.0.0 (not just localhost)

---

## Production URLs

Replace YOUR_EC2_IP with your actual IP:

- **Frontend**: http://YOUR_EC2_IP:5173
- **Backend API**: http://YOUR_EC2_IP:9000
- **API Docs**: http://YOUR_EC2_IP:9000/docs
- **Health Check**: http://YOUR_EC2_IP:9000/health

---

## Important Notes

⚠️ **Security**:
- Change JWT_SECRET_KEY in production
- Set DEBUG=False
- Limit SSH access to your IP only
- Use HTTPS in production (setup SSL with Let's Encrypt)

⚠️ **Costs**:
- t3.medium: ~$30/month
- Elastic IP: Free if attached
- Data transfer: Variable

⚠️ **Database**:
- Cassandra is already external (sunway.hep88.com)
- Ensure EC2 can reach it (test with: `telnet sunway.hep88.com 9042`)
