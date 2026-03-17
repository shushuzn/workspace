#!/bin/bash
# Innovator Dashboard Deployment Script
# Deploy to: 8.208.30.28:/var/www/innovator/

set -e

echo "🚀 Starting Innovator Dashboard Deployment..."
echo "Target: root@8.208.30.28:/var/www/innovator/"

# Create directory
echo "📁 Creating directory..."
ssh root@8.208.30.28 "mkdir -p /var/www/innovator"

# Upload files
echo "📤 Uploading files..."
scp -r ./33-dashboard/* root@8.208.30.28:/var/www/innovator/

# Set permissions
echo "🔐 Setting permissions..."
ssh root@8.208.30.28 "chmod -R 755 /var/www/innovator"

# Configure nginx
echo "🔧 Configuring nginx..."
cat > /tmp/innovator.conf << 'EOF'
server {
    listen 8443 ssl http2;
    server_name innovator.felixxii.xyz;
    
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    
    root /var/www/innovator;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

scp /tmp/innovator.conf root@8.208.30.28:/etc/nginx/sites-available/innovator

# Enable site
echo "✅ Enabling site..."
ssh root@8.208.30.28 "ln -sf /etc/nginx/sites-available/innovator /etc/nginx/sites-enabled/"

# Test and reload nginx
echo "🔄 Testing nginx config..."
ssh root@8.208.30.28 "nginx -t"

echo "♻️  Reloading nginx..."
ssh root@8.208.30.28 "systemctl reload nginx"

echo "✅ Deployment complete!"
echo "🌐 Access: https://innovator.felixxii.xyz:8443"
