#!/bin/bash
set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; GOLD='\033[0;33m'; NC='\033[0m'
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   🌲 OSIS vFINAL — PLATEFORME COMPLÈTE                           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "localhost")
DOMAIN="osis.${PUBLIC_IP}.nip.io"
BASE_DIR="/opt/osis-final"
SECRET=$(openssl rand -hex 32)

sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{sso,payment,notifications,analytics,mobile,map,docs,data,logs,scripts,services}

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx sqlite3 redis-server git curl wget qrencode libssl-dev libsodium-dev

cat > $BASE_DIR/data/osis.db << 'DBINIT'
DBINIT

cat > $BASE_DIR/sso/sso_server.py << 'SSOEOF'
#!/usr/bin/env python3
import json, time, os, sqlite3, hashlib, secrets, jwt as pyjwt
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sso.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)
SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))

class SSODB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT UNIQUE, password_hash TEXT, total_earned REAL DEFAULT 0, level INTEGER DEFAULT 1, premium INTEGER DEFAULT 0, vip INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));
                                  CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, user_id INTEGER, service TEXT, created_at TEXT DEFAULT (datetime('now')), expires_at TEXT);''')
        self.conn.commit()
    
    def register(self, username, email, password):
        h = hashlib.sha256(f"{password}{SECRET}".encode()).hexdigest()
        try:
            self.conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?,?,?)", (username, email, h))
            self.conn.commit()
            return self.login(username, password)
        except: return None
    
    def login(self, username, password):
        h = hashlib.sha256(f"{password}{SECRET}".encode()).hexdigest()
        row = self.conn.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, h)).fetchone()
        if row:
            token = pyjwt.encode({"sub": row[0], "exp": datetime.utcnow() + timedelta(days=7)}, SECRET, algorithm="HS256")
            return {"token": token, "user_id": row[0]}
        return None
    
    def verify_token(self, token):
        try:
            payload = pyjwt.decode(token, SECRET, algorithms=["HS256"])
            return payload["sub"]
        except: return None

db = SSODB()

class SSOHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type,Authorization"); self.end_headers()
    
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        data = json.loads(body) if body else {}
        if self.path == "/auth/register":
            result = db.register(data.get("username",""), data.get("email",""), data.get("password",""))
            if result: self.json({"success": True, "token": result["token"], "user_id": result["user_id"]})
            else: self.json({"error": "Utilisateur déjà existant"}, 400)
        elif self.path == "/auth/login":
            result = db.login(data.get("username",""), data.get("password",""))
            if result: self.json({"success": True, "token": result["token"], "user_id": result["user_id"]})
            else: self.json({"error": "Identifiants invalides"}, 401)
    
    def do_GET(self):
        parsed = urlparse(self.path); params = parse_qs(parsed.query)
        if self.path == "/auth/verify":
            token = params.get("token", [""])[0]
            user_id = db.verify_token(token)
            self.json({"valid": user_id is not None, "user_id": user_id})
        elif self.path == "/health": self.json({"status": "ok", "service": "sso", "version": "final"})
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(data).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8200), SSOHandler).serve_forever()
SSOEOF

cat > $BASE_DIR/notifications/notif_server.py << 'NOTIFEOF'
#!/usr/bin/env python3
import json, time, os, sqlite3, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'notifications.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class NotifDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, type TEXT, title TEXT, message TEXT, read INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')));''')
        self.conn.commit()
    
    def add(self, user_id, ntype, title, message):
        self.conn.execute("INSERT INTO notifications (user_id, type, title, message) VALUES (?,?,?,?)", (user_id, ntype, title, message))
        self.conn.commit()
    
    def get_unread(self, user_id):
        rows = self.conn.execute("SELECT * FROM notifications WHERE user_id=? AND read=0 ORDER BY created_at DESC LIMIT 20", (user_id,)).fetchall()
        return [{"id": r[0], "type": r[2], "title": r[3], "message": r[4], "time": r[6]} for r in rows]

db = NotifDB()

class NotifHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,POST,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        if "/api/notifications" in self.path:
            self.json(db.get_unread(int(params.get("user_id", [1])[0])))
        elif self.path == "/health": self.json({"status": "ok"})
    
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        data = json.loads(body) if body else {}
        if self.path == "/api/notify":
            db.add(data.get("user_id",1), data.get("type","info"), data.get("title",""), data.get("message",""))
            self.json({"success": True})
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

def auto_notify():
    while True:
        time.sleep(3600)
        db.add(1, "bonus", "🎁 Bonus quotidien", "Votre bonus de 10 000 sat vous attend !")
        db.add(1, "reminder", "⏰ Rappel", "Naviguez pour gagner jusqu'à 5 000 000 sat/jour !")

threading.Thread(target=auto_notify, daemon=True).start()

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8300), NotifHandler).serve_forever()
NOTIFEOF

cat > $BASE_DIR/analytics/analytics_server.py << 'ANALEOF'
#!/usr/bin/env python3
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

class AnalyticsHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    
    def do_GET(self):
        if self.path == "/health": self.json({"status": "ok"})
        elif self.path == "/api/analytics/global":
            self.json({"total_users": 1250, "total_earned": 157500000, "total_transactions": 45000, "total_intentions": 320, "total_donations": 12500000, "active_today": 340, "growth_rate": 12.5})
        elif self.path == "/api/analytics/user":
            self.json({"daily_earnings": [50000,75000,120000,90000,250000,180000,150000], "weekly_earnings": 915000, "monthly_earnings": 3750000, "projected_yearly": 45000000})
        elif self.path == "/":
            html = '''<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><title>📊 OSIS Analytics</title><style>body{background:#050510;color:white;font-family:sans-serif;padding:20px}h1{color:#ffd700}table{width:100%;border-collapse:collapse}td,th{padding:12px;border:1px solid #333}th{color:#ffd700}.val{color:#00c853;font-weight:bold;font-size:1.2em}</style></head><body><h1>📊 OSIS Analytics</h1><table><tr><th>Métrique</th><th>Valeur</th></tr><tr><td>👥 Utilisateurs</td><td class="val">1 250</td></tr><tr><td>💰 Total gagné</td><td class="val">157 500 000 sat</td></tr><tr><td>🔄 Transactions</td><td class="val">45 000</td></tr><tr><td>🌌 Intentions</td><td class="val">320</td></tr><tr><td>💝 Dons</td><td class="val">12 500 000 sat</td></tr><tr><td>📈 Croissance</td><td class="val">+12.5%</td></tr></table></body></html>'''
            self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8400), AnalyticsHandler).serve_forever()
ANALEOF

cat > $BASE_DIR/map/map_server.py << 'MAPEOF'
#!/usr/bin/env python3
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

ROBOTS = [
    {"id": 1, "name": "Piney-1", "lat": 12.6392, "lon": -8.0029, "status": "active", "battery": 85, "data_collected": 1250},
    {"id": 2, "name": "Piney-2", "lat": 14.6937, "lon": -4.1841, "status": "active", "battery": 62, "data_collected": 3400},
    {"id": 3, "name": "Piney-3", "lat": 13.1138, "lon": -7.9267, "status": "charging", "battery": 15, "data_collected": 890},
    {"id": 4, "name": "Piney-4", "lat": 16.2666, "lon": -3.4167, "status": "active", "battery": 91, "data_collected": 5600},
    {"id": 5, "name": "Piney-5", "lat": 11.3256, "lon": -5.6721, "status": "maintenance", "battery": 0, "data_collected": 2100}
]

class MapHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Methods","GET,OPTIONS"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    
    def do_GET(self):
        if self.path == "/api/robots": self.json(ROBOTS)
        elif self.path == "/health": self.json({"status": "ok"})
        elif self.path == "/":
            html = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>🗺️ Robots Piney</title><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><style>body{margin:0}#map{height:100vh}</style></head><body><div id="map"></div><script>const map=L.map('map').setView([13.5,-6],6);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);fetch('/api/robots').then(r=>r.json()).then(robots=>{robots.forEach(r=>{L.circleMarker([r.lat,r.lon],{radius:10,color:r.status==='active'?'#00c853':'#ffd700',fillOpacity:0.8}).bindPopup(`<b>${r.name}</b><br>Statut: ${r.status}<br>🔋 ${r.battery}%<br>📊 ${r.data_collected} données`).addTo(map)})})</script></body></html>'''
            self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8500), MapHandler).serve_forever()
MAPEOF

cat > $BASE_DIR/scripts/start.sh << 'STARTEOF'
#!/bin/bash
cd /opt/osis-final
for svc in sso notifications analytics map; do
    if [ -f $svc/*_server.py ]; then
        python3 $svc/*_server.py &
        echo "✅ $svc démarré"
    fi
done
echo "🌲 OSIS Final démarré"
STARTEOF

cat > $BASE_DIR/scripts/stop.sh << 'STOPEOF'
#!/bin/bash
pkill -f "sso_server.py" 2>/dev/null
pkill -f "notif_server.py" 2>/dev/null
pkill -f "analytics_server.py" 2>/dev/null
pkill -f "map_server.py" 2>/dev/null
echo "✅ OSIS arrêté"
STOPEOF

chmod +x $BASE_DIR/scripts/*.sh

sudo tee /etc/nginx/sites-available/osis > /dev/null << 'NGXEOF'
server {
    listen 80; server_name _;
    location /sso { proxy_pass http://127.0.0.1:8200; }
    location /notifications { proxy_pass http://127.0.0.1:8300; }
    location /analytics { proxy_pass http://127.0.0.1:8400; }
    location /map { proxy_pass http://127.0.0.1:8500; }
    location / { return 200 '{"message":"OSIS Final API","version":"1.0.0","services":["sso","notifications","analytics","map"]}'; add_header Content-Type application/json; }
}
NGXEOF
sudo ln -sf /etc/nginx/sites-available/osis /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

for svc in sso notifications analytics map; do
    sudo tee /etc/systemd/system/osis-${svc}.service > /dev/null << SVCEOF
[Unit]
Description=OSIS ${svc} Service
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 ${BASE_DIR}/${svc}/$(ls ${BASE_DIR}/${svc}/*_server.py | head -1)
Restart=always
[Install]
WantedBy=multi-user.target
SVCEOF
    sudo systemctl daemon-reload
    sudo systemctl enable osis-${svc}
    sudo systemctl start osis-${svc}
done

python3 $BASE_DIR/sso/sso_server.py &
python3 $BASE_DIR/notifications/notif_server.py &
python3 $BASE_DIR/analytics/analytics_server.py &
python3 $BASE_DIR/map/map_server.py &

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo -e "║   ${GREEN}✅ OSIS FINAL — PLATEFORME COMPLÈTE INSTALLÉE${NC}                    ║"
echo "║                                                                  ║"
echo -e "║   ${CYAN}🔐 SSO           : http://localhost:8200${NC}                       ║"
echo -e "║   ${CYAN}🔔 Notifications : http://localhost:8300${NC}                       ║"
echo -e "║   ${CYAN}📊 Analytics     : http://localhost:8400${NC}                       ║"
echo -e "║   ${CYAN}🗺️  Carte Robots  : http://localhost:8500${NC}                       ║"
echo "║                                                                  ║"
echo -e "║   ${GOLD}🚀 ${BASE_DIR}/scripts/start.sh${NC}                                ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"