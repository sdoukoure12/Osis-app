#!/bin/bash
# =============================================================================
# 🌲 OSIS vULTIMATE PRODUCTION — Plateforme Complète Multi-Marchés
# =============================================================================
# Auteur  : sdoukoure12
# GitHub  : https://github.com/sdoukoure12/Osis-app
# Email   : africain3x21@gmail.com
# Marchés : Carbon Credits ($50B) + Artisanat ($8B) + Certification ($3B)
#           + Identité Numérique ($30B) + Micro-tâches ($12B) + Agri-IoT ($20B)
# Potentiel Total : $123 Milliards
# =============================================================================
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; GOLD='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
clear
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║   🌲  OSIS  vULTIMATE  PRODUCTION  —  Plateforme Multi-Marchés           ║"
echo "║                                                                          ║"
echo "║   Auteur  : sdoukoure12                                                  ║"
echo "║   GitHub  : https://github.com/sdoukoure12/Osis-app                      ║"
echo "║   Email   : africain3x21@gmail.com                                       ║"
echo "║   Marchés : $123 Milliards potentiels                                    ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
sleep 2

# =============================================================================
# CONFIGURATION
# =============================================================================
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "localhost")
DOMAIN="osis.${PUBLIC_IP}.nip.io"
BASE_DIR="/opt/osis-production"
GIT_REPO="https://github.com/sdoukoure12/Osis-app.git"
GIT_EMAIL="africain3x21@gmail.com"
GIT_USER="sdoukoure12"
SECRET_KEY=$(openssl rand -hex 32)

BTC_ADDRESS_1="bc1qkue2h6hy0mchup80f9me036qwywfpmmcvefnsf"
BTC_ADDRESS_2="bc1qv4cez2gxvdh4ntha28at5f9mw0nv38szwn79ap"
BTC_ADDRESS_3="bc1qt3p7fw7fw3a3k6a82zmh4m45drgrdldx7r3u79"
BTC_ADDRESS_4="bc1qh7zl4t533vq2pg83udkvxpk30dz3rp4zlzzv78"

SSH_KEY_TERMUX="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKpdzEfKym6f5Gw5y+3ZPdp27ZfKAPxQFkn1YOYpj8iM termux@localhost"
SSH_KEY_EMAIL="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINDfvTC+o2h9FyGC1R7eoYni8RrX3ONB9YP+pwy0kdIF ton_email@example.com"
SSH_KEY_MAIN="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMRuxUDQZ/KJ8K+28ObRdyz6dd/iaVZfxgusQ67/Mv+M africain3x21@gmail.com"

echo -e "${YELLOW}📋 Configuration${NC}"
echo "   Domaine    : $DOMAIN"
echo "   IP         : $PUBLIC_IP"
echo "   Dossier    : $BASE_DIR"
echo ""

# =============================================================================
# 1. DÉPENDANCES SYSTÈME
# =============================================================================
echo -e "${CYAN}📦 Installation des dépendances...${NC}"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx sqlite3 redis-server git curl wget openssl libssl-dev libsodium-dev qrencode golang-go rustc cargo postgresql-client

# =============================================================================
# 2. STRUCTURE DU PROJET
# =============================================================================
echo -e "${CYAN}📁 Création de la structure...${NC}"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
cd $BASE_DIR

SERVICES=(
    "core:8000:API Principale"
    "auth:8200:Authentification SSO"
    "browser:8100:Navigateur Récompensé"
    "browser-pro:8101:Navigateur PRO"
    "intention:8091:Économie de l'Intention"
    "garden:8070:Jardin Financier"
    "possibles:8085:Marché des Possibles"
    "carbon:8700:Crédits Carbone ($50B)"
    "artisan:8701:Marketplace Artisanat ($8B)"
    "certification:8702:Certification Blockchain ($3B)"
    "identity:8703:Identité Numérique ($30B)"
    "agri:8704:Agri-Piney IoT ($20B)"
    "microtasks:8705:Micro-tâches Récompensées ($12B)"
    "social:8002:Banque Sociale"
    "build:8003:Architecture"
    "education:8004:Cours & Certifications"
    "donate:8005:Dons Hôpitaux"
    "market:8600:Marketplace Générale"
    "notifications:8300:Système Notifications"
    "analytics:8400:Analytics"
    "map:8500:Carte Robots"
    "docs:9001:Documentation"
    "admin:9000:Administration"
)

for svc_info in "${SERVICES[@]}"; do
    IFS=':' read -r name port desc <<< "$svc_info"
    mkdir -p $BASE_DIR/services/$name
done

mkdir -p $BASE_DIR/{scripts,config,data,logs,static,deploy,.github/workflows}

# =============================================================================
# 3. CONFIGURATION GLOBALE
# =============================================================================
cat > $BASE_DIR/config/osis.conf << EOF
{
    "project": "OSIS Production",
    "version": "3.0.0",
    "author": "sdoukoure12",
    "email": "africain3x21@gmail.com",
    "github": "https://github.com/sdoukoure12/Osis-app",
    "domain": "$DOMAIN",
    "secret_key": "$SECRET_KEY",
    "btc_addresses": ["$BTC_ADDRESS_1","$BTC_ADDRESS_2","$BTC_ADDRESS_3","$BTC_ADDRESS_4"],
    "markets": {
        "carbon_credits": {"potential": "$50B", "status": "active"},
        "artisan_market": {"potential": "$8B", "status": "active"},
        "certification": {"potential": "$3B", "status": "active"},
        "digital_identity": {"potential": "$30B", "status": "active"},
        "agri_iot": {"potential": "$20B", "status": "active"},
        "microtasks": {"potential": "$12B", "status": "active"}
    },
    "total_market_potential": "$123B"
}
EOF

# =============================================================================
# 4. NOYAU CENTRAL UNIFIÉ
# =============================================================================
echo -e "${CYAN}🧠 Création du Noyau Central...${NC}"

cat > $BASE_DIR/services/core/server.py << 'COREEOF'
#!/usr/bin/env python3
"""OSIS Production Core — Noyau Central Unifié"""
import json, os, sqlite3, hashlib, secrets, time, math, random
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'osis.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class CoreDB:
    def __init__(self):
        self.c = sqlite3.connect(DB)
        self.c.executescript('''
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, email TEXT, password_hash TEXT, balance REAL DEFAULT 10000, total_earned REAL DEFAULT 0, total_hashes REAL DEFAULT 0, level INTEGER DEFAULT 1, referral_code TEXT, premium INTEGER DEFAULT 0, vip INTEGER DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS machines(id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, hostname TEXT, hashrate REAL DEFAULT 0, is_robot INTEGER DEFAULT 0, status TEXT DEFAULT 'active', last_heartbeat DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, user_id INTEGER, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS earnings(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, source TEXT, amount REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS dictionary(id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, definition TEXT, language TEXT DEFAULT 'fr', contributor_id INTEGER, status TEXT DEFAULT 'approved');
            CREATE TABLE IF NOT EXISTS donations(id INTEGER PRIMARY KEY AUTOINCREMENT, donor_id INTEGER, campaign TEXT, amount REAL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS intentions(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, category TEXT, token_value REAL DEFAULT 10000, total_invested REAL DEFAULT 0, resonance_level INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS gardens(id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, name TEXT, seed_amount REAL, current_value REAL, growth_rate REAL DEFAULT 0.05, level INTEGER DEFAULT 1);
            CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, difficulty TEXT, language TEXT DEFAULT 'fr', reward REAL DEFAULT 10);
            CREATE TABLE IF NOT EXISTS certifications(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, course_id INTEGER, score INTEGER DEFAULT 100, cert_hash TEXT, completed_at DATETIME DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE IF NOT EXISTS carbon_credits(id INTEGER PRIMARY KEY AUTOINCREMENT, project_name TEXT, location TEXT, trees_planted INTEGER, co2_tons REAL, tokens_issued REAL DEFAULT 0, price_per_ton REAL DEFAULT 25);
            CREATE TABLE IF NOT EXISTS artisan_products(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, artisan TEXT, country TEXT, category TEXT, price REAL, stock INTEGER, sales INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS identities(id INTEGER PRIMARY KEY AUTOINCREMENT, did TEXT UNIQUE, name TEXT, country TEXT, public_key TEXT, verified INTEGER DEFAULT 0);
        ''')
        self.c.commit()
        self._init_data()
    
    def _init_data(self):
        if not self.c.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
            self.c.execute("INSERT INTO users(username,email,password_hash,balance,level) VALUES('demo','demo@osis.io','demo',100000,5)")
            self.c.execute("INSERT INTO intentions(title,category) VALUES('École du Futur','education'),('L Eau Pour Tous','humanitaire'),('Forêt Éternelle','environnement'),('Santé Mobile','santé'),('Villages Connectés','infrastructure')")
            self.c.execute("INSERT INTO gardens(owner_id,name,seed_amount,current_value) VALUES(1,'Jardin Principal',1000,1000)")
            self.c.execute("INSERT INTO courses(title,difficulty,reward) VALUES('Blockchain Fondamentaux','débutant',10),('Architecture Africaine','intermédiaire',25),('Menuiserie Artisanale','débutant',15),('Crédits Carbone','avancé',50),('Identité Numérique','avancé',75)")
            self.c.execute("INSERT INTO carbon_credits(project_name,location,trees_planted,co2_tons) VALUES('Forêt du Sahel','Mali',50000,12500),('Mangroves Sénégal','Sénégal',100000,25000),('Reforestation Kenya','Kenya',75000,18750)")
            self.c.execute("INSERT INTO artisan_products(name,artisan,country,category,price,stock) VALUES('Tabouret Dogon','Amadou Diallo','Mali','mobilier',25000,10),('Tissu Bogolan','Fatou Keita','Mali','textile',15000,25),('Masque Baoulé','Koffi Yao','Côte d Ivoire','art',50000,3),('Collier Touareg','Amina Ag','Niger','bijoux',35000,15)")
            self.c.commit()
    
    def register(self, username, email, password):
        h = hashlib.sha256(password.encode()).hexdigest()
        ref = secrets.token_hex(4)
        try:
            self.c.execute("INSERT INTO users(username,email,password_hash,referral_code,balance) VALUES(?,?,?,?,10000)", (username, email, h, ref))
            self.c.commit()
            return self.c.execute("SELECT last_insert_rowid()").fetchone()[0]
        except: return None
    
    def login(self, username, password):
        h = hashlib.sha256(password.encode()).hexdigest()
        r = self.c.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, h)).fetchone()
        if r:
            t = secrets.token_hex(32)
            self.c.execute("INSERT INTO sessions(token,user_id) VALUES(?,?)", (t, r[0]))
            self.c.commit()
            return {"token": t, "user_id": r[0]}
        return None
    
    def earn(self, user_id, source, amount):
        self.c.execute("INSERT INTO earnings(user_id,source,amount) VALUES(?,?,?)", (user_id, source, amount))
        self.c.execute("UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE id=?", (amount, amount, user_id))
        self.c.execute("UPDATE users SET level=MAX(1,CAST(SQRT(total_earned/1000) AS INTEGER)) WHERE id=?", (user_id,))
        self.c.commit()
        r = self.c.execute("SELECT balance, total_earned, level FROM users WHERE id=?", (user_id,)).fetchone()
        return {"balance": r[0], "total_earned": r[1], "level": r[2]} if r else {}
    
    def get_stats(self):
        return {
            "users": self.c.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "machines": self.c.execute("SELECT COUNT(*) FROM machines WHERE status='active'").fetchone()[0],
            "total_earned": self.c.execute("SELECT COALESCE(SUM(total_earned),0) FROM users").fetchone()[0],
            "intentions": self.c.execute("SELECT COUNT(*) FROM intentions").fetchone()[0],
            "carbon_tons": self.c.execute("SELECT COALESCE(SUM(co2_tons),0) FROM carbon_credits").fetchone()[0],
            "artisan_products": self.c.execute("SELECT COUNT(*) FROM artisan_products").fetchone()[0],
            "dictionary_words": self.c.execute("SELECT COUNT(*) FROM dictionary WHERE status='approved'").fetchone()[0],
            "total_donations": self.c.execute("SELECT COALESCE(SUM(amount),0) FROM donations").fetchone()[0]
        }

db = CoreDB()

class CoreHandler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Access-Control-Allow-Methods","GET,POST,PUT,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers","Content-Type,Authorization")
    
    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()
    
    def _json(self, d, s=200):
        self.send_response(s); self._cors(); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(d, ensure_ascii=False, default=str).encode())
    
    def _html(self, h, s=200):
        self.send_response(s); self._cors(); self.send_header("Content-Type","text/html; charset=utf-8"); self.end_headers()
        self.wfile.write(h.encode())
    
    def do_GET(self):
        p = urlparse(self.path); q = parse_qs(p.query)
        
        routes = {
            "/": self._serve_dashboard,
            "/health": lambda: self._json({"status":"operational","version":"3.0.0","markets":"$123B potential"}),
            "/api/stats": lambda: self._json(db.get_stats()),
            "/api/intentions": lambda: self._json([dict(zip(["id","title","category","value"], r)) for r in db.c.execute("SELECT id,title,category,token_value FROM intentions").fetchall()]),
            "/api/gardens": lambda: self._json([dict(zip(["id","name","value","level"], r)) for r in db.c.execute("SELECT id,name,current_value,level FROM gardens").fetchall()]),
            "/api/courses": lambda: self._json([dict(zip(["id","title","difficulty","reward"], r)) for r in db.c.execute("SELECT id,title,difficulty,reward FROM courses").fetchall()]),
            "/api/carbon": lambda: self._json([dict(zip(["id","project","location","co2","price"], r)) for r in db.c.execute("SELECT id,project_name,location,co2_tons,price_per_ton FROM carbon_credits").fetchall()]),
            "/api/artisan": lambda: self._json([dict(zip(["id","name","artisan","country","price","stock"], r)) for r in db.c.execute("SELECT id,name,artisan,country,price,stock FROM artisan_products").fetchall()]),
            "/api/leaderboard": lambda: self._json([dict(zip(["username","earned","level"], r)) for r in db.c.execute("SELECT username,total_earned,level FROM users ORDER BY total_earned DESC LIMIT 20").fetchall()]),
            "/api/languages": lambda: self._json(["fr","en","bambara","wolof","peul","sonrhaï","tamasheq","haoussa","lingala","swahili","zoulou"]),
        }
        
        handler = routes.get(p.path, lambda: self._json({"error":"Not found"}, 404))
        handler()
    
    def do_POST(self):
        p = urlparse(self.path)
        b = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        d = json.loads(b) if b else {}
        
        if p.path == "/auth/register":
            uid = db.register(d.get("username",""), d.get("email",""), d.get("password",""))
            if uid: self._json({"success":True,"user_id":uid,"bonus":10000,"message":"Bienvenue ! 10 000 sat offerts !"})
            else: self._json({"error":"Utilisateur déjà existant"},400)
        
        elif p.path == "/auth/login":
            r = db.login(d.get("username",""), d.get("password",""))
            if r: self._json({"success":True,"token":r["token"],"user_id":r["user_id"]})
            else: self._json({"error":"Identifiants invalides"},401)
        
        elif p.path == "/api/earn":
            result = db.earn(d.get("user_id",1), d.get("source","browsing"), d.get("amount",100))
            self._json({"earned":d.get("amount",100),"balance":result.get("balance",0),"level":result.get("level",1)})
        
        elif p.path == "/api/donate":
            db.c.execute("INSERT INTO donations(donor_id,campaign,amount) VALUES(?,?,?)", (d.get("user_id",1), d.get("campaign",""), d.get("amount",0)))
            db.c.commit()
            self._json({"message":"💝 Merci pour votre don !"})
        
        elif p.path == "/api/intention/create":
            db.c.execute("INSERT INTO intentions(title,description,category) VALUES(?,?,?)", (d.get("title",""), d.get("description",""), d.get("category","innovation")))
            db.c.commit()
            db.earn(d.get("user_id",1), "intention_created", 10000)
            self._json({"message":"🌌 Intention créée ! +10 000 sat"})
        
        elif p.path == "/api/build/plan":
            s = d.get("style","toumbouctou"); a = d.get("area",100); r = d.get("rooms",3)
            w = max(int(math.sqrt(a)*10),200); h = int(w*1.3)
            svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#f5e6c8" stroke="#8b5e3c" stroke-width="2"/><rect x="10" y="10" width="{w-20}" height="{h-20}" fill="none" stroke="#8b5e3c" stroke-width="3"/><text x="{w//2}" y="30" text-anchor="middle" font-size="20">🏗️ {s}</text><text x="{w//2}" y="{h-10}" text-anchor="middle" font-size="14">{a}m² - {r} pièces</text></svg>'
            db.earn(d.get("user_id",1), "plan_generated", 5)
            self._json({"svg":svg,"reward":5})
        
        elif p.path == "/api/carbon/buy":
            tons = d.get("tons",100); price = tons * 25
            db.c.execute("UPDATE carbon_credits SET tokens_issued=tokens_issued+? WHERE id=1", (tons,))
            db.c.commit()
            self._json({"message":f"🌍 {tons} tonnes achetées !","price":price,"certificate":f"CERT-{random.randint(10000,99999)}"})
        
        elif p.path == "/api/identity/create":
            did = f"did:osis:{secrets.token_hex(16)}"
            pubkey = secrets.token_hex(32)
            db.c.execute("INSERT INTO identities(did,name,country,public_key,verified) VALUES(?,?,?,?,1)", (did, d.get("name",""), d.get("country",""), pubkey))
            db.c.commit()
            self._json({"did":did,"name":d.get("name",""),"status":"verified"})
        
        else:
            self._json({"error":"Not found"}, 404)
    
    def _serve_dashboard(self):
        stats = db.get_stats()
        h = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌲 OSIS Production</title>
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#0a0a1a">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:linear-gradient(135deg,#050510 0%,#0a0a2e 50%,#050510 100%);color:white;font-family:'Segoe UI',sans-serif;min-height:100vh}}
.header{{background:linear-gradient(135deg,#1a0030,#0a0030,#001a30);padding:40px 20px;text-align:center;border-bottom:3px solid #ffd700}}
.header h1{{font-size:3em;background:linear-gradient(90deg,#ffd700,#ffaa00,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:shine 2s infinite}}
@keyframes shine{{0%{{filter:brightness(1)}}50%{{filter:brightness(1.5)}}100%{{filter:brightness(1)}}}}
.header .subtitle{{color:#aaa;font-size:1.1em;margin-top:10px}}
.container{{max-width:1400px;margin:0 auto;padding:30px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;margin:30px 0}}
.stat{{background:rgba(26,26,62,0.9);padding:25px;border-radius:20px;text-align:center;border:2px solid #2a2a5a;transition:all .3s}}
.stat:hover{{border-color:#ffd700;transform:translateY(-5px)}}
.stat .val{{font-size:2.5em;font-weight:bold;display:block}}
.stat .lbl{{color:#888;font-size:0.9em;margin-top:5px}}
.gold{{color:#ffd700}}.green{{color:#00c853}}.purple{{color:#e040fb}}.blue{{color:#448aff}}.orange{{color:#ff6b35}}.red{{color:#ff1744}}.cyan{{color:#00bcd4}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(350px,1fr));gap:25px;margin:30px 0}}
.card{{background:rgba(26,26,62,0.9);padding:30px;border-radius:20px;border:1px solid #2a2a5a}}
.card h3{{margin-bottom:15px;font-size:1.3em}}
.btn{{display:inline-block;padding:12px 30px;border-radius:25px;font-weight:bold;cursor:pointer;text-decoration:none;margin:5px;border:none;font-size:1em}}
.btn-gold{{background:linear-gradient(90deg,#ffd700,#ffaa00);color:black}}
.btn-purple{{background:linear-gradient(90deg,#7c4dff,#e040fb);color:white}}
.btn-green{{background:linear-gradient(90deg,#00c853,#00e676);color:black}}
.btn-orange{{background:linear-gradient(90deg,#ff6b35,#ff8a65);color:white}}
input{{padding:12px 20px;border-radius:25px;border:1px solid #333;background:#0a0a2a;color:white;width:100%;margin:8px 0;font-size:1em}}
.actions{{margin-top:20px;text-align:center}}
.footer{{text-align:center;padding:30px;color:#666;font-size:0.9em}}
.footer a{{color:#ffd700;text-decoration:none}}
.badge{{display:inline-block;padding:5px 15px;border-radius:20px;font-size:0.8em;font-weight:bold;margin:3px}}
.badge-gold{{background:#ffd700;color:black}}
.badge-purple{{background:#7c4dff;color:white}}
</style></head><body>
<div class="header">
    <h1>🌲 OSIS Production</h1>
    <p class="subtitle">Plateforme Multi-Marchés — Potentiel : <span style="color:#ffd700;font-weight:bold">$123 Milliards</span></p>
    <div style="margin-top:15px">
        <span class="badge badge-gold">🌍 Carbon Credits</span>
        <span class="badge badge-purple">🛍️ Artisanat</span>
        <span class="badge badge-gold">🎓 Certification</span>
        <span class="badge badge-purple">🔐 Identité</span>
        <span class="badge badge-gold">🌾 Agri-IoT</span>
        <span class="badge badge-purple">💼 Micro-tâches</span>
    </div>
</div>
<div class="container">
    <div class="stats">
        <div class="stat"><span class="val gold">{stats['users']}</span><span class="lbl">👥 Utilisateurs</span></div>
        <div class="stat"><span class="val green">{stats['total_earned']:.0f}</span><span class="lbl">💰 Total Gagné (sat)</span></div>
        <div class="stat"><span class="val purple">{stats['intentions']}</span><span class="lbl">🌌 Intentions</span></div>
        <div class="stat"><span class="val cyan">{stats['carbon_tons']:.0f}</span><span class="lbl">🌍 CO2 Séquestré (t)</span></div>
        <div class="stat"><span class="val orange">{stats['artisan_products']}</span><span class="lbl">🛍️ Produits Artisanaux</span></div>
        <div class="stat"><span class="val red">{stats['total_donations']:.0f}</span><span class="lbl">💝 Dons (sat)</span></div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3 class="gold">⚡ Actions Rapides</h3>
            <p style="color:#888;margin-bottom:15px">Gagnez des satoshis instantanément</p>
            <button class="btn btn-gold" onclick="earn('tab_open',500)">📑 Nouvel Onglet (+500 sat)</button>
            <button class="btn btn-gold" onclick="earn('search',1000)">🔍 Recherche (+1K sat)</button>
            <button class="btn btn-green" onclick="earn('share',5000)">📤 Partage (+5K sat)</button>
            <button class="btn btn-purple" onclick="earn('daily_login',10000)">🎁 Connexion (+10K sat)</button>
        </div>
        
        <div class="card">
            <h3 class="purple">🌌 Créer une Intention</h3>
            <p style="color:#888;margin-bottom:15px">+10 000 sat à la création</p>
            <input id="intention-title" placeholder="Titre de votre intention">
            <input id="intention-desc" placeholder="Description">
            <input id="intention-cat" placeholder="Catégorie (education, sante, environnement...)">
            <button class="btn btn-purple" onclick="createIntention()">🌌 Créer (+10K sat)</button>
        </div>
        
        <div class="card">
            <h3 class="orange">🏗️ Architecture</h3>
            <p style="color:#888;margin-bottom:15px">Générez un plan architectural</p>
            <input id="build-style" placeholder="Style (toumbouctou, gao, bamako...)">
            <input id="build-area" placeholder="Surface (m²)" type="number">
            <input id="build-rooms" placeholder="Nombre de pièces" type="number">
            <button class="btn btn-orange" onclick="buildPlan()">🏗️ Générer (+5 sat)</button>
            <div id="plan-result" style="margin-top:15px"></div>
        </div>
        
        <div class="card">
            <h3 class="cyan">🌍 Crédits Carbone</h3>
            <p style="color:#888;margin-bottom:15px">Achetez des crédits carbone</p>
            <input id="carbon-tons" placeholder="Tonnes de CO2" type="number" value="100">
            <button class="btn btn-green" onclick="buyCarbon()">🌍 Acheter (25€/tonne)</button>
            <div id="carbon-result" style="margin-top:15px"></div>
        </div>
    </div>
</div>
<div class="footer">
    <p>🌲 OSIS Production v3.0 | <a href="https://github.com/sdoukoure12/Osis-app">GitHub</a> | <a href="mailto:africain3x21@gmail.com">Contact</a></p>
    <p style="margin-top:10px">Marchés : Carbon Credits ($50B) | Artisanat ($8B) | Certification ($3B) | Identité ($30B) | Agri-IoT ($20B) | Micro-tâches ($12B)</p>
</div>
<script>
const API = 'http://' + window.location.hostname + ':8000';

async function earn(source, amount) {{
    try {{
        const r = await fetch(API + '/api/earn', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:1,source,amount}})}});
        const d = await r.json();
        alert('💰 +' + amount + ' sat !\\nSolde : ' + d.balance.toFixed(0) + ' sat\\nNiveau : ' + d.level);
    }} catch(e) {{ alert('Erreur de connexion'); }}
}}

async function createIntention() {{
    const title = document.getElementById('intention-title').value;
    const desc = document.getElementById('intention-desc').value;
    const cat = document.getElementById('intention-cat').value || 'innovation';
    if (!title) return alert('Titre requis');
    const r = await fetch(API + '/api/intention/create', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:1,title,description:desc,category:cat}})}});
    const d = await r.json();
    alert(d.message);
}}

async function buildPlan() {{
    const style = document.getElementById('build-style').value || 'toumbouctou';
    const area = document.getElementById('build-area').value || 100;
    const rooms = document.getElementById('build-rooms').value || 3;
    const r = await fetch(API + '/api/build/plan', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{user_id:1,style,area:parseFloat(area),rooms:parseInt(rooms)}})}});
    const d = await r.json();
    document.getElementById('plan-result').innerHTML = d.svg;
}}

async function buyCarbon() {{
    const tons = document.getElementById('carbon-tons').value || 100;
    const r = await fetch(API + '/api/carbon/buy', {{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{tons:parseFloat(tons)}})}});
    const d = await r.json();
    document.getElementById('carbon-result').innerHTML = '<p style="color:#00c853;margin-top:10px">✅ ' + d.message + ' | ' + d.price + '€ | Certificat : ' + d.certificate + '</p>';
}}

setInterval(() => earn('minute_browsing', 100), 60000);
</script></body></html>'''
        self._html(h)

if __name__ == "__main__":
    port = int(os.getenv("CORE_PORT", 8000))
    print(f"🧠 OSIS Production Core sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), CoreHandler).serve_forever()
COREEOF

# =============================================================================
# 5. SCRIPTS DE DÉMARRAGE
# =============================================================================
cat > $BASE_DIR/scripts/start-all.sh << 'STARTEOF'
#!/bin/bash
cd /opt/osis-production
echo "🌲 Démarrage OSIS Production..."
python3 services/core/server.py &
echo "✅ Core : http://localhost:8000"
echo "🌲 OSIS Production démarré"
STARTEOF

cat > $BASE_DIR/scripts/stop-all.sh << 'STOPEOF'
#!/bin/bash
pkill -f "services/core/server.py" 2>/dev/null
echo "✅ OSIS arrêté"
STOPEOF

chmod +x $BASE_DIR/scripts/*.sh

# =============================================================================
# 6. NGINX
# =============================================================================
sudo tee /etc/nginx/sites-available/osis-prod > /dev/null << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 100M;
    location / { proxy_pass http://127.0.0.1:8000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; }
}
NGINXEOF
sudo ln -sf /etc/nginx/sites-available/osis-prod /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# =============================================================================
# 7. SSH KEYS
# =============================================================================
mkdir -p ~/.ssh
echo "$SSH_KEY_TERMUX" >> ~/.ssh/authorized_keys
echo "$SSH_KEY_EMAIL" >> ~/.ssh/authorized_keys
echo "$SSH_KEY_MAIN" >> ~/.ssh/authorized_keys
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys

# =============================================================================
# 8. GIT INIT & PUSH
# =============================================================================
cd $BASE_DIR
git init 2>/dev/null || true
git config user.email "$GIT_EMAIL"
git config user.name "$GIT_USER"
git remote add origin $GIT_REPO 2>/dev/null || true

cat > .gitignore << 'GITIGNORE'
*.db
*.log
__pycache__/
*.pyc
.env
data/
logs/
GITIGNORE

git add -A
git commit -m "🌲 OSIS Production v3.0 — Plateforme Multi-Marchés ($123B potentiel)" 2>/dev/null || true

# =============================================================================
# 9. DÉMARRAGE
# =============================================================================
python3 $BASE_DIR/services/core/server.py &

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo -e "║   ${GREEN}✅ OSIS PRODUCTION v3.0 — DÉMARRÉ !${NC}                                      ║"
echo "║                                                                          ║"
echo -e "║   ${GOLD}🌐 Dashboard    : http://localhost:8000${NC}                                   ║"
echo -e "║   ${GOLD}🌐 Domaine      : http://${DOMAIN}${NC}                                         ║"
echo "║                                                                          ║"
echo -e "║   ${CYAN}📊 Marchés Actifs :${NC}                                                       ║"
echo -e "║   🌍 Crédits Carbone      : $50 Milliards                               ║"
echo -e "║   🛍️  Artisanat Africain   : $8 Milliards                                ║"
echo -e "║   🎓 Certification         : $3 Milliards                                ║"
echo -e "║   🔐 Identité Numérique    : $30 Milliards                               ║"
echo -e "║   🌾 Agri-Piney IoT        : $20 Milliards                               ║"
echo -e "║   💼 Micro-tâches          : $12 Milliards                               ║"
echo "║                                                                          ║"
echo -e "║   ${YELLOW}💰 Potentiel Total : \$123 Milliards${NC}                                     ║"
echo "║                                                                          ║"
echo -e "║   ${GOLD}🐙 GitHub : https://github.com/sdoukoure12/Osis-app${NC}                       ║"
echo -e "║   ${GOLD}📧 Email  : africain3x21@gmail.com${NC}                                        ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"