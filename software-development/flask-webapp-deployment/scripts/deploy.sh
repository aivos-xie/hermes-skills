#!/bin/bash
# Quick deploy script for Flask application with nginx reverse proxy
# Usage: ./deploy.sh [app_name] [port]

set -e

APP_NAME="${1:-myapp}"
APP_PORT="${2:-8080}"
APP_DIR="/opt/$APP_NAME"

echo "🚀 Deploying $APP_NAME on port $APP_PORT..."

# Create directory
mkdir -p "$APP_DIR"

# Check if app.py exists
if [ ! -f "$APP_DIR/app.py" ]; then
    echo "❌ Error: $APP_DIR/app.py not found"
    echo "Please copy your Flask app to $APP_DIR/app.py first"
    exit 1
fi

# Create systemd service
echo "📦 Creating systemd service..."
sudo tee "/etc/systemd/system/$APP_NAME.service" > /dev/null << EOF
[Unit]
Description=$APP_NAME Flask Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Create nginx config
echo "🌐 Configuring nginx..."
sudo tee "/etc/nginx/conf.d/$APP_NAME.conf" > /dev/null << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;
    }
}
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable and start service
echo "▶️  Starting service..."
sudo systemctl enable "$APP_NAME"
sudo systemctl restart "$APP_NAME"

# Test nginx config
echo "🔍 Testing nginx configuration..."
sudo nginx -t

# Reload nginx
echo "🔄 Reloading nginx..."
sudo nginx -s reload

# Wait for service to start
sleep 2

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status "$APP_NAME" --no-pager | head -10

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📌 Access URLs:"
echo "   - http://localhost"
echo "   - http://$(hostname -I | awk '{print $1}')"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: sudo journalctl -u $APP_NAME -f"
echo "   - Restart: sudo systemctl restart $APP_NAME"
echo "   - Stop: sudo systemctl stop $APP_NAME"
echo "   - Status: sudo systemctl status $APP_NAME"
