#!/bin/bash

# PathFinder Deployment Script for AWS EC2
# Run this script on your EC2 instance after cloning the repository

set -e  # Exit on error

echo "======================================"
echo "PathFinder - AWS EC2 Deployment"
echo "======================================"

# Variables
APP_DIR="/home/ubuntu/PathFinder---Personalized-Academic-Dashboard"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
PYTHON_VERSION="3.11"

echo ""
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo ""
echo "2. Installing dependencies..."
sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv python3-pip nodejs npm git nginx ufw

echo ""
echo "3. Setting up backend..."
cd "$BACKEND_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    python${PYTHON_VERSION} -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "4. Configuring backend environment..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo "⚠️  IMPORTANT: Edit backend/.env with your production settings!"
    echo "   - Update ALLOWED_ORIGINS with your EC2 IP/domain"
    echo "   - Generate new JWT_SECRET_KEY"
    read -p "Press Enter after you've updated the .env file..."
fi

echo ""
echo "5. Setting up frontend..."
cd "$FRONTEND_DIR"

# Install Node packages
npm install

echo ""
echo "6. Configuring frontend environment..."
if [ ! -f ".env.production" ]; then
    echo "⚠️  IMPORTANT: Create frontend/.env.production with:"
    echo "   VITE_API_URL=http://YOUR_EC2_PUBLIC_IP:9000"
    read -p "Press Enter after you've created the .env.production file..."
fi

echo ""
echo "7. Installing systemd service..."
sudo cp "$APP_DIR/deployment/pathfinder-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pathfinder-backend
sudo systemctl start pathfinder-backend

echo ""
echo "8. Configuring Nginx..."
sudo cp "$APP_DIR/deployment/nginx.conf" /etc/nginx/sites-available/pathfinder
sudo ln -sf /etc/nginx/sites-available/pathfinder /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "9. Configuring firewall..."
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 9000/tcp # Backend API
sudo ufw allow 5173/tcp # Frontend (if not using nginx)
sudo ufw --force enable

echo ""
echo "10. Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/pathfinder-backend.log
sudo touch /var/log/pathfinder-backend-error.log
sudo chown ubuntu:ubuntu /var/log/pathfinder-backend*.log

echo ""
echo "======================================"
echo "✅ Deployment Complete!"
echo "======================================"
echo ""
echo "Next Steps:"
echo "1. Update backend/.env with production settings"
echo "2. Update frontend/.env.production with your EC2 IP"
echo "3. Configure AWS Security Group to allow ports 80, 443, 9000, 5173"
echo "4. Start frontend: cd $FRONTEND_DIR && npm run dev -- --host 0.0.0.0"
echo ""
echo "Useful Commands:"
echo "  - Backend status: sudo systemctl status pathfinder-backend"
echo "  - Backend logs: sudo journalctl -u pathfinder-backend -f"
echo "  - Nginx status: sudo systemctl status nginx"
echo "  - Restart backend: sudo systemctl restart pathfinder-backend"
echo ""
echo "Access your app at: http://YOUR_EC2_PUBLIC_IP"
echo "API docs at: http://YOUR_EC2_PUBLIC_IP:9000/docs"
