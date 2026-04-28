#!/bin/bash
# =============================================================================
# 🌌 OSIS v∞.0 — L'ÉCONOMIE DE L'INTENTION
# =============================================================================
# La première plateforme où vos intentions valent de l'argent
# =============================================================================
set -e

PURPLE='\033[0;35m'; GOLD='\033[0;33m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║   🌌 OSIS v∞.0 — L'ÉCONOMIE DE L'INTENTION                      ║"
echo "║                                                                  ║"
echo "║   « Ce que vous voulez faire vaut plus que ce que vous avez. »   ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

BASE_DIR="/opt/osis-intention"
sudo mkdir -p $BASE_DIR && sudo chown -R $USER:$USER $BASE_DIR
mkdir -p $BASE_DIR/{engine,api,dashboard,data,logs}

# ============================================================
# LE MOTEUR DE L'INTENTION
# ============================================================
cat > $BASE_DIR/engine/intention_core.py << 'CORE'
#!/usr/bin/env python3
"""
🌌 OSIS v∞.0 — L'ÉCONOMIE DE L'INTENTION

Le premier système où vos intentions sont des actifs financiers.
"""
import json, time, os, sqlite3, random, hashlib, threading, math
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'data', 'intention.db')
os.makedirs(os.path.dirname(DB), exist_ok=True)

class IntentionDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS intentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                resources_needed TEXT,
                token_value REAL DEFAULT 100.0,
                total_invested REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active',
                progress REAL DEFAULT 0.0,
                resonance_level INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                realized_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intention_id INTEGER REFERENCES intentions(id),
                investor_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intention_id INTEGER REFERENCES intentions(id),
                provider_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                unit TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            
            CREATE TABLE IF NOT EXISTS resonance_network (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intention_id_1 INTEGER REFERENCES intentions(id),
                intention_id_2 INTEGER REFERENCES intentions(id),
                strength REAL DEFAULT 0.0,
                created_at TEXT DEFAULT (datetime('now'))
            );
        ''')
        self.conn.commit()
    
    def create_intention(self, creator_id, title, description, category, resources_needed="[]"):
        cursor = self.conn.execute(
            "INSERT INTO intentions (creator_id, title, description, category, resources_needed) VALUES (?,?,?,?,?)",
            (creator_id, title, description, category, resources_needed)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_intention(self, iid):
        row = self.conn.execute("SELECT * FROM intentions WHERE id = ?", (iid,)).fetchone()
        if row:
            cols = [c[0] for c in self.conn.execute("PRAGMA table_info(intentions)")]
            return dict(zip(cols, row))
        return None
    
    def get_all_intentions(self, status="active"):
        rows = self.conn.execute("SELECT * FROM intentions WHERE status = ? ORDER BY token_value DESC", (status,)).fetchall()
        cols = [c[0] for c in self.conn.execute("PRAGMA table_info(intentions)")]
        return [dict(zip(cols, r)) for r in rows]
    
    def invest(self, intention_id, investor_id, amount):
        intention = self.get_intention(intention_id)
        if not intention: return False
        
        # L'investissement augmente la valeur du token
        growth = amount * 0.1
        new_value = intention["token_value"] + growth
        new_invested = intention["total_invested"] + amount
        
        self.conn.execute(
            "UPDATE intentions SET token_value = ?, total_invested = ?, progress = MIN(100, progress + ?) WHERE id = ?",
            (new_value, new_invested, amount / new_value * 10, intention_id)
        )
        self.conn.execute(
            "INSERT INTO investments (intention_id, investor_id, amount) VALUES (?,?,?)",
            (intention_id, investor_id, amount)
        )
        self.conn.commit()
        return True
    
    def add_resource(self, intention_id, provider_id, resource_type, quantity, unit):
        self.conn.execute(
            "INSERT INTO resources (intention_id, provider_id, resource_type, quantity, unit) VALUES (?,?,?,?,?)",
            (intention_id, provider_id, resource_type, quantity, unit)
        )
        # Les ressources augmentent le niveau de résonance
        self.conn.execute(
            "UPDATE intentions SET resonance_level = resonance_level + 1 WHERE id = ?",
            (intention_id,)
        )
        self.conn.commit()
    
    def calculate_resonance(self):
        """Calcule les résonances entre toutes les intentions"""
        intentions = self.get_all_intentions()
        for i in range(len(intentions)):
            for j in range(i+1, len(intentions)):
                if intentions[i]["category"] == intentions[j]["category"]:
                    strength = random.uniform(0.3, 0.9)
                    self.conn.execute(
                        "INSERT OR IGNORE INTO resonance_network (intention_id_1, intention_id_2, strength) VALUES (?,?,?)",
                        (intentions[i]["id"], intentions[j]["id"], strength)
                    )
                    # Bonus de résonance
                    bonus = (intentions[i]["token_value"] + intentions[j]["token_value"]) * strength * 0.01
                    self.conn.execute("UPDATE intentions SET token_value = token_value + ? WHERE id IN (?,?)",
                                    (bonus, intentions[i]["id"], intentions[j]["id"]))
        self.conn.commit()
    
    def get_stats(self):
        intentions = self.get_all_intentions()
        total_value = sum(i["token_value"] for i in intentions)
        total_invested = sum(i["total_invested"] for i in intentions)
        resonances = self.conn.execute("SELECT COUNT(*) FROM resonance_network").fetchone()[0]
        
        return {
            "total_intentions": len(intentions),
            "total_value": total_value,
            "total_invested": total_invested,
            "resonance_network_size": resonances,
            "top_intentions": sorted(intentions, key=lambda x: x["token_value"], reverse=True)[:5]
        }

db = IntentionDB()

# Intentions initiales
if not db.get_all_intentions():
    db.create_intention(1, "Apprendre le Bambara", "Créer une école de langue bambara en ligne accessible à tous", "education", '[{"type":"serveur","quantity":1},{"type":"professeur","quantity":3}]')
    db.create_intention(1, "Planter 1000 Arbres", "Reverdir le Sahel avec des arbres fruitiers", "environnement", '[{"type":"plants","quantity":1000},{"type":"terrain","quantity":5}]')
    db.create_intention(1, "Construire un Marché", "Un marché couvert pour les artisans locaux", "infrastructure", '[{"type":"matériaux","quantity":500},{"type":"main_oeuvre","quantity":20}]')
    db.create_intention(1, "L'Eau Pour Tous", "Forage de puits dans 10 villages", "humanitaire", '[{"type":"équipement","quantity":10},{"type":"techniciens","quantity":5}]')
    db.create_intention(1, "Hôpital Mobile", "Une clinique itinérante pour les zones reculées", "santé", '[{"type":"véhicule","quantity":1},{"type":"personnel","quantity":10}]')
    print("🌌 5 Intentions initiales créées")

# =============================================
# MOTEUR DE RÉSONANCE (24/7)
# =============================================
class ResonanceEngine:
    def __init__(self):
        self.running = True
    
    def cycle(self):
        db.calculate_resonance()
    
    def start(self):
        print("🔮 Moteur de Résonance activé")
        while self.running:
            self.cycle()
            stats = db.get_stats()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌌 Valeur: {stats['total_value']:.0f} sat | Intentions: {stats['total_intentions']} | Résonances: {stats['resonance_network_size']}")
            time.sleep(300)

# =============================================
# API + DASHBOARD
# =============================================
class IntentionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        if path == "/health":
            self.json({"status": "ok", "service": "intention-economy", "version": "∞.0"})
        elif path == "/api/intentions":
            self.json(db.get_all_intentions())
        elif path == "/api/intention":
            iid = int(params.get("id", [1])[0])
            self.json(db.get_intention(iid))
        elif path == "/api/stats":
            self.json(db.get_stats())
        elif path == "/api/create":
            title = params.get("title", ["Nouvelle Intention"])[0]
            desc = params.get("desc", [""])[0]
            cat = params.get("category", ["innovation"])[0]
            iid = db.create_intention(1, title, desc, cat)
            self.json({"message": "🌌 Intention créée !", "id": iid, "token_value": 100})
        elif path == "/api/invest":
            iid = int(params.get("id", [1])[0])
            amount = float(params.get("amount", [100])[0])
            db.invest(iid, 1, amount)
            intention = db.get_intention(iid)
            self.json({"message": f"💰 Investi !", "new_value": intention["token_value"], "progress": intention["progress"]})
        elif path == "/":
            self.serve_dashboard()
        else:
            self.json({"error": "Not found"}, 404)
    
    def serve_dashboard(self):
        intentions = db.get_all_intentions()
        stats = db.get_stats()
        
        cards = ""
        for intent in intentions[:10]:
            progress = intent["progress"]
            cards += f'''
            <div class="intention-card">
                <span class="category">{intent["category"]}</span>
                <h3>🧠 {intent["title"]}</h3>
                <p>{intent["description"][:100]}...</p>
                <div class="progress-bar"><div class="progress-fill" style="width:{progress}%"></div></div>
                <div class="info">
                    <span>💎 {intent["token_value"]:.0f} sat</span>
                    <span>💰 {intent["total_invested"]:.0f} investis</span>
                    <span>🔮 Nv.{intent["resonance_level"]}</span>
                    <span>{progress:.0f}%</span>
                </div>
                <button onclick="invest({intent['id']})">💰 Investir</button>
            </div>'''
        
        html = f'''<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🌌 OSIS ∞ — Économie de l'Intention</title>
<style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    body{{background:#050510;color:white;font-family:sans-serif;min-height:100vh}}
    .header{{background:linear-gradient(135deg,#1a0030,#0a0030,#001a30);padding:40px 20px;text-align:center}}
    .header h1{{font-size:3em;background:linear-gradient(90deg,#e040fb,#7c4dff,#00c853,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
    .header .subtitle{{color:#aaa;font-size:1.2em;margin-top:10px}}
    .container{{max-width:1200px;margin:0 auto;padding:20px}}
    .stats{{display:flex;justify-content:center;gap:20px;flex-wrap:wrap;margin:30px 0}}
    .stat{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;text-align:center;min-width:180px;border:1px solid #2a005a}}
    .stat .val{{font-size:2em;color:#ffd700;font-weight:bold}}
    .stat .lbl{{color:#888;margin-top:5px;font-size:0.85em}}
    .intention-card{{background:rgba(26,0,62,0.9);padding:25px;border-radius:20px;margin:15px 0;border:1px solid #2a005a;position:relative}}
    .intention-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#e040fb,#7c4dff,#00c853)}}
    .category{{background:#7c4dff;padding:3px 12px;border-radius:15px;font-size:0.7em;text-transform:uppercase}}
    .intention-card h3{{color:#e040fb;margin:10px 0}}
    .intention-card p{{color:#aaa;margin-bottom:15px}}
    .progress-bar{{background:#1a0030;height:8px;border-radius:10px;margin:10px 0;overflow:hidden}}
    .progress-fill{{background:linear-gradient(90deg,#e040fb,#00c853);height:100%;border-radius:10px;transition:width 1s}}
    .info{{display:flex;gap:15px;flex-wrap:wrap;margin:10px 0;color:#888;font-size:0.85em}}
    button{{padding:10px 25px;background:linear-gradient(90deg,#7c4dff,#e040fb);color:white;border:none;border-radius:25px;font-weight:bold;cursor:pointer;width:100%}}
    .btn-create{{background:linear-gradient(90deg,#00c853,#ffd700);color:black;display:block;width:100%;padding:18px;font-size:1.2em;margin:30px 0;border-radius:30px}}
    .pulse{{animation:pulse 3s infinite;display:inline-block}}
    @keyframes pulse{{0%{{opacity:1}}50%{{opacity:0.3}}100%{{opacity:1}}}}
</style></head><body>
<div class="header">
    <h1>🌌 OSIS ∞</h1>
    <p class="subtitle">L'ÉCONOMIE DE L'INTENTION — Vos idées valent de l'argent</p>
</div>
<div class="container">
    <div class="stats">
        <div class="stat"><div class="val">{stats['total_intentions']}</div><div class="lbl">🧠 Intentions</div></div>
        <div class="stat"><div class="val">{stats['total_value']:.0f}</div><div class="lbl">💎 Valeur Totale (sat)</div></div>
        <div class="stat"><div class="val">{stats['total_invested']:.0f}</div><div class="lbl">💰 Investis (sat)</div></div>
        <div class="stat"><div class="val">{stats['resonance_network_size']}</div><div class="lbl">🔮 Résonances</div></div>
    </div>
    {cards}
    <button class="btn-create" onclick="createIntention()">🌌 Créer une Intention</button>
    <div style="text-align:center;color:#888;margin:20px 0"><span class="pulse">🔮</span> Le Moteur de Résonance connecte les intentions en continu</div>
</div>
<script>
function createIntention(){{const t=prompt('Votre intention ?','');const d=prompt('Description ?','');const c=prompt('Catégorie ? (education, environnement, infrastructure, humanitaire, santé, innovation)','innovation');if(t){{fetch('/api/create?title='+encodeURIComponent(t)+'&desc='+encodeURIComponent(d)+'&category='+c).then(()=>location.reload())}}}}
function invest(id){{const a=prompt('Montant (satoshis) ?','100');if(a){{fetch('/api/invest?id='+id+'&amount='+a).then(()=>location.reload())}}}}
setInterval(()=>location.reload(),60000);
</script></body></html>'''
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(html.encode())
    
    def json(self, data, status=200):
        self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False, default=str).encode())

# Démarrer
engine = ResonanceEngine()
threading.Thread(target=engine.start, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("INTENTION_PORT", 8090))
    print(f"🌌 Économie de l'Intention sur http://localhost:{port}")
    HTTPServer(("0.0.0.0", port), IntentionHandler).serve_forever()
CORE

# ------------------------------------------------------------
# SERVICE
# ------------------------------------------------------------
sudo tee /etc/systemd/system/osis-intention.service > /dev/null << 'SVC'
[Unit]
Description=OSIS Économie de l'Intention ∞
After=network.target
[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/osis-intention/engine/intention_core.py
Restart=always
Environment=INTENTION_PORT=8090
[Install]
WantedBy=multi-user.target
SVC
sudo systemctl daemon-reload && sudo systemctl enable osis-intention && sudo systemctl start osis-intention

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo -e "║   ${PURPLE}🌌 OSIS ∞ — L'ÉCONOMIE DE L'INTENTION EST VIVANTE !${NC}              ║"
echo "║                                                                  ║"
echo "║   ${CYAN}🌐 http://localhost:8090${NC}                                      ║"
echo "║                                                                  ║"
echo "║   ${GOLD}🧠 CRÉEZ une intention${NC}                                        ║"
echo "║   ${GOLD}💰 INVESTISSEZ dans les intentions des autres${NC}                 ║"
echo "║   ${GOLD}🔮 Les résonances MULTIPLIENT la valeur${NC}                       ║"
echo "║                                                                  ║"
echo "║   ${PURPLE}💡 CE CONCEPT N'EXISTE NULLE PART AILLEURS${NC}                    ║"
echo "║   ${PURPLE}🚀 NOUS SOMMES LES PREMIERS${NC}                                  ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"